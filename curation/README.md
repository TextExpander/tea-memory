# Memory curation

The bots (Watson, Sherlock, Leo) write durable notes here automatically as they
work. This module keeps the library healthy over time so it does not rot.

`curate.py` runs nightly via `.github/workflows/curate.yml`. For each memory
directory it asks a model for a **conservative** plan and applies it in two lanes:

- **Consolidation** (merge near-duplicates, reconcile a note that a newer one
  contradicts). This never loses information, so it is opened as a PR and
  **auto-merged**. The PR remains in history as the audit trail.
- **Deletions** (a note judged wrong, obsolete, or fully superseded). Information
  is removed, so it is opened as a PR and **left open** for a human to merge or
  close.

It no-ops quietly when there is nothing to do. Every change is a git commit, so
anything can be reviewed or reverted.

## Running it manually

Actions tab, "Curate memory", "Run workflow". Tick **dry_run** to print the plan
without changing anything.

## Requirements

- Repo secret `ANTHROPIC_API_KEY`. Git and PR operations use the built-in
  `GITHUB_TOKEN` (this repo only), so no other token is needed.

## Scope

This intentionally does not do semantic/vector retrieval. Notes are recalled by
the bots via their loaded index plus on-demand grep of these files, which scales
well for a small, curated library.
