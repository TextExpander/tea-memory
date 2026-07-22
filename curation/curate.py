#!/usr/bin/env python3
"""Nightly curation for the tea-memory library.

Reads the memory notes in each directory (shared/, watson/, sherlock/, ...),
asks a model for a CONSERVATIVE curation plan, and applies it in two lanes:

  - Consolidation (merges + reconciling rewrites): improves the library without
    losing information. Applied on a branch, opened as a PR, and AUTO-MERGED, so
    every change still leaves a PR trail.
  - Deletions (a note judged wrong/obsolete/superseded): information is removed,
    so these are opened as a PR and LEFT OPEN for a human to merge or close.

No-ops quietly when there is nothing to do. Set CURATE_DRY_RUN=1 to print the
plan without touching git.

Env: ANTHROPIC_API_KEY, GH_TOKEN (repo-scoped, provided by Actions).
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = "claude-sonnet-4-6"  # curation is subtle; Sonnet, once a night, is cheap
DRY = os.environ.get("CURATE_DRY_RUN") == "1"
TODAY = datetime.date.today().isoformat()

# ---------------------------------------------------------------------------
# helpers

def run(cmd: list[str], check: bool = True) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{r.stderr}")
    return r.stdout.strip()


def anthropic(system: str, user: str, max_tokens: int = 6000) -> str:
    body = json.dumps(
        {
            "model": MODEL,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        d = json.load(resp)
    return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")


FRONT = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)
INDEX_LINE = re.compile(r"^- \[(?P<title>[^\]]+)\]\((?P<slug>[^)]+)\.md\)\s*(?:—|,|-)?\s*(?P<hook>.*)$")


def parse_note(p: Path) -> dict:
    txt = p.read_text()
    m = FRONT.match(txt)
    desc, typ, body = "", "reference", txt.strip()
    if m:
        head, body = m.group(1), m.group(2).strip()
        d = re.search(r"^description:\s*(.+)$", head, re.M)
        t = re.search(r"^\s*type:\s*(.+)$", head, re.M)
        desc = d.group(1).strip() if d else ""
        typ = t.group(1).strip() if t else "reference"
    return {"slug": p.stem, "path": p, "hook": desc, "type": typ, "body": body}


def index_titles(d: Path) -> dict[str, str]:
    titles = {}
    ip = d / "MEMORY.md"
    if ip.exists():
        for line in ip.read_text().splitlines():
            m = INDEX_LINE.match(line.strip())
            if m:
                titles[m.group("slug")] = m.group("title")
    return titles


def memory_dirs() -> list[Path]:
    return sorted(p.parent for p in ROOT.glob("*/MEMORY.md"))


def load_dir(d: Path) -> list[dict]:
    titles = index_titles(d)
    notes = []
    for p in sorted(d.glob("*.md")):
        if p.name == "MEMORY.md":
            continue
        n = parse_note(p)
        n["title"] = titles.get(n["slug"], n["slug"])
        notes.append(n)
    return notes


# ---------------------------------------------------------------------------
# planning

SYSTEM = """You curate a small library of durable memory notes for an autonomous engineering and investigation bot. You are given the notes in ONE directory. Propose CONSERVATIVE curation, only changes that clearly improve the library.

- merges: two or more notes that are near-duplicates or cover the same fact/topic and should be a single note. Provide the merged note and the list of source slugs it replaces.
- rewrites: a note whose content is outdated or directly contradicted by a newer note; rewrite it to reflect the current truth (newer supersedes older). Provide the slug and the new body.
- deletes: a note that is explicitly wrong, obsolete, or fully superseded and carries no residual value. Be very conservative; when unsure, do NOT delete.

Do not invent facts. Do not merge notes that are merely related but distinct. Prefer leaving the library unchanged over speculative edits. Keep titles and hooks concise.

Respond with ONLY a JSON object, no prose or code fence:
{"merges":[{"sources":["slug-a","slug-b"],"slug":"new-slug","title":"...","hook":"one line","type":"reference|feedback|project","body":"merged note body"}],
 "rewrites":[{"slug":"slug-c","hook":"optional new one line","body":"new body"}],
 "deletes":[{"slug":"slug-d","reason":"why it should go"}]}
Empty arrays where nothing qualifies."""


def plan_for_dir(d: Path, notes: list[dict]) -> dict:
    if len(notes) < 2:
        return {"merges": [], "rewrites": [], "deletes": []}
    payload = "\n\n".join(
        f"### slug: {n['slug']}\ntitle: {n['title']}\ntype: {n['type']}\nhook: {n['hook']}\nbody:\n{n['body']}"
        for n in notes
    )
    raw = anthropic(SYSTEM, f"Directory: {d.name}\n\nNotes:\n\n{payload}")
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return {"merges": [], "rewrites": [], "deletes": []}
    try:
        plan = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return {"merges": [], "rewrites": [], "deletes": []}
    return {
        "merges": plan.get("merges") or [],
        "rewrites": plan.get("rewrites") or [],
        "deletes": plan.get("deletes") or [],
    }


def validate(d: Path, notes: list[dict], plan: dict) -> dict:
    """Drop plan items that reference unknown slugs or overlap unsafely."""
    have = {n["slug"] for n in notes}
    merged_away: set[str] = set()
    merges = []
    for m in plan["merges"]:
        srcs = [s for s in (m.get("sources") or []) if s in have]
        if len(srcs) < 2 or not m.get("slug") or not m.get("body") or not m.get("title"):
            continue
        m["sources"] = srcs
        merged_away.update(srcs)
        merges.append(m)
    rewrites = [r for r in plan["rewrites"] if r.get("slug") in have and r.get("body") and r["slug"] not in merged_away]
    # never delete something we are also merging away (merge already removes it)
    deletes = [x for x in plan["deletes"] if x.get("slug") in have and x["slug"] not in merged_away]
    return {"merges": merges, "rewrites": rewrites, "deletes": deletes}


# ---------------------------------------------------------------------------
# applying (operates on files in the current working tree / branch)

def note_text(slug: str, hook: str, typ: str, body: str) -> str:
    return (
        f"---\nname: {slug}\ndescription: {hook}\n"
        f"metadata:\n  type: {typ}\n  source: curation\n  curatedAt: {TODAY}\n---\n\n{body.strip()}\n"
    )


def index_remove(d: Path, slug: str) -> None:
    ip = d / "MEMORY.md"
    lines = ip.read_text().splitlines()
    kept = [ln for ln in lines if not (INDEX_LINE.match(ln.strip()) and INDEX_LINE.match(ln.strip()).group("slug") == slug)]
    ip.write_text("\n".join(kept) + "\n")


def index_add(d: Path, title: str, slug: str, hook: str) -> None:
    ip = d / "MEMORY.md"
    text = ip.read_text().rstrip("\n")
    ip.write_text(f"{text}\n- [{title}]({slug}.md) — {hook}\n")


def index_update_hook(d: Path, slug: str, hook: str) -> None:
    ip = d / "MEMORY.md"
    out = []
    for ln in ip.read_text().splitlines():
        m = INDEX_LINE.match(ln.strip())
        if m and m.group("slug") == slug:
            out.append(f"- [{m.group('title')}]({slug}.md) — {hook}")
        else:
            out.append(ln)
    ip.write_text("\n".join(out) + "\n")


def apply_consolidation(d: Path, plan: dict) -> int:
    changes = 0
    for m in plan["merges"]:
        slug = m["slug"]
        (d / f"{slug}.md").write_text(note_text(slug, m.get("hook", ""), m.get("type", "reference"), m["body"]))
        for src in m["sources"]:
            f = d / f"{src}.md"
            if f.exists():
                f.unlink()
            index_remove(d, src)
        index_remove(d, slug)  # in case a same-slug line already existed
        index_add(d, m["title"], slug, m.get("hook", ""))
        changes += 1
    for r in plan["rewrites"]:
        n = parse_note(d / f"{r['slug']}.md")
        hook = r.get("hook") or n["hook"]
        (d / f"{r['slug']}.md").write_text(note_text(r["slug"], hook, n["type"], r["body"]))
        if r.get("hook"):
            index_update_hook(d, r["slug"], hook)
        changes += 1
    return changes


def apply_deletions(d: Path, plan: dict) -> int:
    changes = 0
    for x in plan["deletes"]:
        f = d / f"{x['slug']}.md"
        if f.exists():
            f.unlink()
        index_remove(d, x["slug"])
        changes += 1
    return changes


# ---------------------------------------------------------------------------
# git / PR

def dirty() -> bool:
    return bool(run(["git", "status", "--porcelain"]))


def open_pr(branch: str, title: str, body: str, automerge: bool) -> str:
    run(["git", "checkout", "-B", branch])
    run(["git", "add", "-A"])
    if not dirty():
        run(["git", "checkout", "main"])
        return ""
    run(["git", "commit", "-m", title])
    run(["git", "push", "-f", "origin", branch])
    url = run(["gh", "pr", "create", "--base", "main", "--head", branch, "--title", title, "--body", body])
    if automerge:
        run(["gh", "pr", "merge", branch, "--squash", "--delete-branch"])
        run(["git", "checkout", "main"])
        run(["git", "fetch", "origin", "main"])
        run(["git", "reset", "--hard", "origin/main"])
    else:
        run(["git", "checkout", "main"])
    return url


# ---------------------------------------------------------------------------
# main

def main() -> int:
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    dirs = memory_dirs()
    plans = {d: validate(d, load_dir(d), plan_for_dir(d, load_dir(d))) for d in dirs}

    cons_lines, del_lines = [], []
    for d in dirs:
        p = plans[d]
        for m in p["merges"]:
            cons_lines.append(f"- {d.name}: merge {', '.join(m['sources'])} -> {m['slug']}")
        for r in p["rewrites"]:
            cons_lines.append(f"- {d.name}: rewrite {r['slug']}")
        for x in p["deletes"]:
            del_lines.append(f"- {d.name}: delete {x['slug']} ({x.get('reason','')})")

    print("=== curation plan ===")
    print("Consolidation:\n" + ("\n".join(cons_lines) or "  (none)"))
    print("Deletions:\n" + ("\n".join(del_lines) or "  (none)"))

    if DRY:
        print("\nDRY RUN: no changes applied.")
        return 0

    # Lane 1: consolidation -> PR, auto-merged.
    for d in dirs:
        apply_consolidation(d, plans[d])
    if dirty():
        body = "Automatic memory curation (merges and reconciling rewrites). Auto-merged; review in history.\n\n" + "\n".join(cons_lines)
        url = open_pr(f"curate/consolidate-{TODAY}", f"curate: consolidate memory ({TODAY})", body, automerge=True)
        if url:
            print(f"consolidation PR (auto-merged): {url}")

    # Lane 2: deletions -> PR, left open for a human.
    for d in dirs:
        apply_deletions(d, plans[d])
    if dirty():
        body = "Proposed memory deletions (notes judged wrong/obsolete). NOT auto-merged: review and merge or close.\n\n" + "\n".join(del_lines)
        url = open_pr(f"curate/deletions-{TODAY}", f"curate: proposed deletions ({TODAY})", body, automerge=False)
        if url:
            print(f"deletions PR (needs review): {url}")

    if not cons_lines and not del_lines:
        print("Nothing to curate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
