# Technical debt tracker — persistent ledger

**Updated:** 2026-11-23. Status values: `open`, `in-progress`, `blocked`, `closed`. Priority P0 (incorrect numbers/data risk), P1 (production blocker), P2 (maintainability), P3 (optional). `Owner: unassigned` is intentional; do not imply an assignment. All open items require evidence and a checkable closure condition.

| ID | Priority/status | Scope / evidence | Closure test |
|---|---|---|---|
| TD-001 | P1 blocked | No approved exact destination schemas for most profiles; `--reference` checks headers only. | Each workflow has approved template + type, order and totals golden tests. |
| TD-002 | P1 open | `config.load_profile` checks a few YAML fields, not full semantic/config schema. | Invalid configs fail before source parsing; negative tests cover all supported keys. |
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
| TD-016 | P1 open | Dayforce non-CCB cost-center validation `contains_any` matches substrings, not approved normalized codes; business label variation risk. | Business-approved code parser and fixture suite for exact/variant codes. |

## Active cross-references

- [EP-0001 source certification](active/EP-0001-source-contract-certification.md): TD-001/003/004/005/007/008/009/010/016.
- [EP-0002 guardrails](active/EP-0002-harness-guardrails.md): TD-002/006/011.
- Deferred/owner unassigned: TD-012/013/014/015. Create a focused ExecPlan before substantial work.

## Updating a debt item

Never erase history to declare progress. For significant changes append a dated note to [execution log](../progress/EXECUTION_LOG.md), link tests and plan, then update table status/closure. Do not mark closed because a speculative design exists.
