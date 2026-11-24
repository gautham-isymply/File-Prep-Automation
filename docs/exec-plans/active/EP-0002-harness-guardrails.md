# EP-0002 — enforce documentation and configuration guardrails

**State:** active  
**Updated:** 2026-11-24
**Linked debt:** TD-002, TD-006, TD-011  
**Owner:** unassigned

## Objective

Agents can navigate the repo from a short entry file and automatically detect broken local Markdown links, missing per-profile runbooks and drift between development and packaged YAML copies. Later milestones extend guards to full schema validation, static dependency checks and CI.

## Baseline and scope

The original v0.1.0 baseline had 10 profiles / 19 tests; current scope has eight profiles / 17 tests (EP-0003). No formal docs linter or dependency boundary enforcement in original CLI. This plan adds a lightweight stdlib documentation check; it does not change business file-preparation behavior.

## Current repository facts

`AGENTS.md` maps to `docs/index.md`; per-profile docs are in `docs/processes/`; `config/profiles` and `src/factoryprep/profiles` are duplicated configuration directories; `scripts/check_docs.py` checks basic integrity.

## Unknowns and human decisions

CI provider and repository branch protections are not supplied. Do not assume GitHub Actions or require access to a remote repository; local checks are sufficient for now.

## Milestones / Progress

- [x] M1 — short entrypoint, docs index, architecture map, process docs and debt tracking.
- [x] M2 — local checker for links, process coverage, and profile mirror consistency.
- [ ] M3 — typed YAML/schema rules with negative profile tests and migration documentation.
- [ ] M4 — static dependency/import boundaries and size/quality conventions with actionable failures.
- [ ] M5 — CI integration once platform and organization constraints are known.

## Step-by-step design

Keep checker in `scripts/check_docs.py` with zero extra runtime dependencies; expand it incrementally. Introduce a formal profile schema only after acceptance against real fixtures to avoid prematurely constraining legitimate formats. Dependency rule: CLI→engine→pipelines→models/transform/io; avoid process-to-CLI reverse edges. Add automated tests for checker itself before changing its behavior.

## Verification and acceptance

`uv run python scripts/check_docs.py` returns exit 0 and reports eight profile/runbook matches, no broken Markdown links and no YAML-copy drift. `uv run pytest -q` remains green. Later milestones require new tests proving bad YAML/import edges fail with clear diagnostics.

## Evidence / execution log

2026-11-23: baseline `PYTHONPATH=src pytest -q --disable-warnings --maxfail=1` → `19 passed in 0.63s`. Checker result recorded in `docs/progress/EXECUTION_LOG.md` after packaging.

## Decisions

2026-11-23: opt for small executable local integrity checks over heavy new tooling. Defer CI configuration until host service is known.

## Risks / rollback

Checks must not mutate code or raw inputs. If checker produces a false positive, document repro in this plan, fix test/checker, and retain integrity guarantees.

## Next step

Implement and validate full profile schema lint and boundary tests; keep this plan active until independently enforceable.
