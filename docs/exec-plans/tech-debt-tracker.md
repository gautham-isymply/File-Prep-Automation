# Technical debt tracker — persistent ledger

**Updated:** 2026-11-26. Status values: `open`, `in-progress`, `blocked`, `closed`. Priority P0 (incorrect numbers/data risk), P1 (production blocker), P2 (maintainability), P3 (optional). `Owner: unassigned` is intentional; do not imply an assignment. All open items require evidence and a checkable closure condition.

| ID | Priority/status | Scope / evidence | Closure test |
|---|---|---|---|
| TD-001 | P1 blocked | No approved exact destination schemas for most profiles; `--reference` checks headers only. | Each workflow has approved template + type, order and totals golden tests. |
| TD-002 | P1 in-progress | Owner: unassigned. 2026-11-25 structural checks and negative tests added for consumed profile/correction shapes (EP-0004); unknown keys and cross-field semantic constraints remain outside preflight. | Invalid configs fail before source parsing; negative tests cover all supported keys and semantic relationships. |
| TD-003 | P0 blocked | JZ original source HC invoice-hours placement and paid/OT split not specified; current staging assumption. | Raw JZ fixture → correct five output rows with business-approved paid/OT logic. |
| TD-004 | P1 blocked | GBR `0<x<1` hours encoding ambiguous; fraction ×24 may be wrong for pre-decimal values. | Raw data examples + independently checked regular/OT totals for mixed encodings. |
| TD-005 | P1 blocked | CCB manual one-row 65.8→75.8 correction lacks stable unique source key. | Approved exact-row mapping and case-specific fixture; no global replacement. |
| TD-006 | P2 open | Module dependency boundaries documented but not statically enforced. | Import/layer linter + negative regression test. |
| TD-007 | P1 blocked | Dayforce refresh is external; program cannot prove workbook data freshness. | Approved freshness evidence/check in operational gate or certified export contract. |
| TD-008 | P1 blocked | Taiwan date output format/complete schema not explicit in manual; current CSV assumptions. | Real target spec and byte/cell-level golden fixture comparison. |
| TD-009 | P1 blocked | CBG SSI date wizard says YMD while screenshot shows US-style; configured MDY. | Representative raw SSI workbook with verified parsed weekly dates. |
| TD-010 | P1 blocked | Sunday–Saturday stated overall, some SQL date examples differ. | Written business rule for all load windows and tests. |
| TD-011 | P2 open | Only local docs checker; CI, full link/code symbol lint, drift checks not integrated into remote pipeline. | CI enforces tests/docs/schema checks; reproducible failure evidence. |
| TD-012 | P2 open | Report/output non-transactional; stale prior output remains after fail; concurrency target collision possible. | Run-id/hash manifest + safe latest-success pointer or atomic output/report bundle with tests. |
| TD-013 | P2 open | Raw cell/report errors may expose confidential values/paths; no built-in redaction or retention. | Configured safe report policy and documented secure operational storage. |
| TD-014 | P2 open | `read_book` eagerly materializes workbook cells; memory/large-file performance not characterized. | Benchmarks on representative sizes and streaming plan or bound. |
| TD-015 | P2 open | Duplicate detection is optional `columns.duplicate_keys` and no real business keys specified by source manual for input. | Approved per-source candidate keys + tests proving duplicates flagged before output. |
| TD-016 | P1 in-progress | 2026-11-26: exact code > label parsing replaces substring matching for both Dayforce profiles, with lookalike regression cases. Real-source label variants/owner-approved grammar remain unverified. | Business-approved code parser and fixture suite for exact/variant codes. |
| TD-017 | P2 closed | Owner: unassigned. Historical 64 findings recorded 2026-11-25. On 2026-11-26 migrated touched CLI options to Annotated, cleaned legacy imports/style and retained boolean type validation; full Ruff exits 0 and 535 tests pass. | `uv run --offline ruff check src tests` PASS; `uv run --offline pytest -q` 535 passed. |

## Active cross-references

### 2026-11-26 manual-review additions

All owners below are **unassigned**. Evidence and per-process acceptance are detailed in [EP-0007](active/EP-0007-manual-parsing-corrections.md); implementation status is recorded per item; real-source closure evidence remains outstanding.

| ID | Priority/status | Scope / evidence | Closure test |
|---|---|---|---|
| TD-018 | P0 in-progress | DMY/comma parsing, explicit blank/status policies, ambiguous-week and missing-day blocks implemented/tested 2026-11-26. Real screenshot Saturday–Friday versus Sunday–Saturday coverage and approved status meanings remain unresolved. | Approved raw timecard/expected-output pair; explicit locale/status/blank/date-coverage contract; no fabricated missing Saturday or mis-scaled hours; independent seven-day totals. |
| TD-019 | P1 in-progress | First/declared-column summaries, repeated-header/table-boundary audit, stronger Core header and numeric hours/metrics implemented/tested 2026-11-26. Actual invoice boundaries and missing Core department evidence remain unapproved. | Real-layout fixtures retain all detail and omit only identified nondata rows; independent approved Core+SSI reconciliation. |
| TD-020 | P1 in-progress | Requested-week date predicates, exact code filters and combined component audits implemented with monthly-retention tests on 2026-11-26. Real-source/filter certification remains under TD-001/007/016. | Real monthly files retained except explicit CCB exclusion; weekly and combined totals match independent approved sums; real code/label grammar accepted. |
| TD-021 | P1 blocked | Supplied DOCX references absent Core preparation/pivot/filter images at P175/P210/P215; Core department list cannot be recovered from available text. | Repaired source evidence or owner-approved complete Core header, boundary and department contracts recorded and exercised in fixtures. |

- [EP-0001 source certification](active/EP-0001-source-contract-certification.md): TD-001/003/004/005/007/008/009/010/016.
- [EP-0002 guardrails](active/EP-0002-harness-guardrails.md): TD-002/006/011.
- Deferred/owner unassigned: TD-012/013/014/015. Create a focused ExecPlan before substantial work.

## Updating a debt item

Never erase history to declare progress. For significant changes append a dated note to [execution log](../progress/EXECUTION_LOG.md), link tests and plan, then update table status/closure. Do not mark closed because a speculative design exists.
