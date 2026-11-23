# Documentation maintenance and retrieval hygiene

`AGENTS.md` is a routing index (<100 lines). `docs/index.md` is the task router. Deep docs carry evidence, code pointers and exact error codes. Avoid duplicating business rules in multiple narrative pages: canonical process rule lives in `docs/processes/<id>.md`; *executable* rule lives in YAML and pipeline.

## Mechanical check

Run `uv run python scripts/check_docs.py` (stdlib; `python scripts/check_docs.py` also works). It checks local Markdown link targets, missing per-profile process pages/index links, YAML drift between repo and packaged copies, key docs, and applies a root entrypoint line budget. It does **not** prove document claims match implementation or check external URLs.

## Human/agent review checklist

1. Identify what changed and which canonical docs must change: process → YAML + runbook; engine → architecture/design/quality; risk → debt; decision → ADR; milestone → plan/state/log.
2. Open exact code/config files referenced in changed docs and verify names, path and severity. Do not fix manual inconsistency by conjecture.
3. Cite manual pages for externally sourced assertions, and label unsupported source assumptions explicitly.
4. Remove stale links and obsolete entry points. Avoid adding new root-level instruction files that compete with `AGENTS.md`.
5. Run the docs checker and unit tests. Record command results and limitations in `progress/EXECUTION_LOG.md`.

## Retrieval optimization

Use stable filenames, exact `profile_id`, issue-code strings and TD/EP/ADR IDs. One concern per file. Keep Markdown headings consistent (`Purpose`, `Source evidence`, `Current implementation`, `Risks`, `Acceptance`) so search/chunk retrieval is predictable. Source page pointers are location labels rather than quotes. Privacy: never embed production employee data or screenshots in docs without approval.
