# FactoryPrep agent entry point

Purpose: Prepare and audit Factory Insights source files with Python + uv. **Do not build SAP BW, DTP, ADSO, email, or PBI integrations.** This file is a *map*, not a complete manual.

## First read (minimal context)

1. [Current verified state](docs/progress/CURRENT_STATE.md) — what exists, what is unverified.
2. [Architecture](ARCHITECTURE.md) — boundaries, modules, processing route.
3. [Documentation router](docs/index.md) — open only documents related to your task.
4. [Active execution plans](docs/exec-plans/index.md) and [tech debt](docs/exec-plans/tech-debt-tracker.md) before significant changes.

## Non-negotiable rules

- A source workbook is read-only. Never mutate it or silently invent/correct hours.
- Distinguish **manual facts**, **implemented behavior**, **unverified assumptions**, and **proposed changes** in docs and reviews.
- Treat reconciliation filters as diagnostics, not row deletions, unless a profile explicitly declares `exclude_rows`.
- BW is outside current scope, even when the manual names its actions.
- Stop on ambiguous profile/header/date mappings. Never infer the JZ raw HC paid-vs-OT split.
- Any change to a load's behavior must update its `docs/processes/<profile>.md`, YAML, tests, debt/plan as relevant.
- Do not claim production validation without real, sanitized input AND confirmed destination schema evidence.
- Maintain both `config/profiles/*.yaml` and embedded `src/factoryprep/profiles/*.yaml` identically.

## Workflow

- Small change: identify relevant process + module + tests; implement; run checks; update [state](docs/progress/CURRENT_STATE.md) and [execution log](docs/progress/EXECUTION_LOG.md).
- Complex/multi-file change: author/update a self-contained [ExecPlan](docs/PLANS.md) in `docs/exec-plans/active/`; track milestones, decisions, evidence, blockers. Move to `completed/` only when acceptance criteria are evidenced.
- Architecture decision: append an [ADR](docs/decisions/index.md); never quietly rewrite accepted history.
- New unresolved problem: add numbered debt in [tracker](docs/exec-plans/tech-debt-tracker.md) with impact, evidence, owner = `unassigned` if unknown, and acceptance to close.
- Before handoff run: `uv run pytest -q`; `uv run python scripts/check_docs.py`; `uv run ruff check src tests` (if dev extras installed). Report each actual result, do not claim what was not run.

## Retrieval shortcuts

- Which input? → [Process index](docs/processes/index.md); each page points to its YAML, pipeline, tests and manual pages.
- Why built this way? → [Design index](docs/design-docs/index.md) and [ADRs](docs/decisions/index.md).
- How run/triage? → [Operations](docs/OPERATIONS.md), [quality contract](docs/quality/REPORT_CONTRACT.md).
- What remains? → [Current state](docs/progress/CURRENT_STATE.md), [quality score](docs/quality/QUALITY_SCORE.md), [debt tracker](docs/exec-plans/tech-debt-tracker.md).
- Where did a rule come from? → [Manual evidence map](docs/references/MANUAL_EVIDENCE.md).

Prefer targeted reading and `rg -n 'TERM' docs src config tests` over loading every file. Keep docs concise; link to one canonical truth rather than copy it repeatedly.
