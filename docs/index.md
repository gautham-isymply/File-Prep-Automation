# Documentation router (start here)

**Use:** choose the question below; read that document first. Paths are stable repository-local entry points. Do not load the entire documentation tree for a single change.

| Agent question | Minimum read |
|---|---|
| What is live and trustworthy? | [CURRENT_STATE](progress/CURRENT_STATE.md) |
| How are modules coupled? | [ARCHITECTURE](../ARCHITECTURE.md), [module contracts](design-docs/MODULE_CONTRACTS.md) |
| How does a specific input work? | [process index](processes/index.md) → one process document → its YAML |
| How are rules expressed in YAML? | [profile contract](design-docs/PROFILE_CONTRACT.md) |
| How is output accepted or rejected? | [quality gates](design-docs/QUALITY_GATES.md), [report contract](quality/REPORT_CONTRACT.md) |
| What should I work on next? | [plans index](exec-plans/index.md), [debt](exec-plans/tech-debt-tracker.md) |
| How do I make a long-lived plan? | [PLANS.md](PLANS.md) |
| Why was an architectural choice made? | [ADRs](decisions/index.md) |
| What does the manual actually say? | [source evidence](references/MANUAL_EVIDENCE.md) |
| How to run a file / diagnose a failure? | [OPERATIONS](OPERATIONS.md) |
| How to keep docs current? | [DOC_GARDENING](quality/DOC_GARDENING.md) |
| What tests demonstrate correctness? | [TEST_STRATEGY](quality/TEST_STRATEGY.md), [quality score](quality/QUALITY_SCORE.md) |
| What are threat/data boundaries? | [SECURITY](SECURITY.md), [RELIABILITY](RELIABILITY.md) |
| Why OpenAI-style harness conventions? | [HARNESS_REFERENCES](references/HARNESS_REFERENCES.md) |

## Canonical sources, descending priority

**Executable behavior:** `src/factoryprep/*.py`, `src/factoryprep/pipelines/*.py`, embedded profiles in `src/factoryprep/profiles/`; **specification:** uploaded 39-page manual as summarized with page pointers; **development profile editing:** `config/profiles/`; **intent/decisions:** docs; **evidence:** tests and checked-in execution log. If sources disagree, do not silently reconcile; file debt, preserve evidence, and ask for the business contract where needed.

## Context and maintenance budget

Keep `AGENTS.md` under ~100 lines, this index under ~70, per-process documents focused on their own workflow. Use exact names of headers/profile IDs and issue codes to make `rg` effective. Update only documents whose assertions changed. Avoid auto-inserting runtime-generated reports into instructions; attach compact summaries and evidence references instead.
