# EP-0001 — certify real input and destination contracts

**State:** active / blocked on real sanitized workbooks and destination templates  
**Updated:** 2026-11-23  
**Linked debt:** TD-001, TD-003, TD-004, TD-005, TD-007, TD-008, TD-009, TD-010  
**Owner:** unassigned

## Objective

An operator can run every workflow on a sanitized representative source and obtain a destination-shaped candidate matching a business-approved manual preparation, with no ambiguous paid/OT transformations. **Do not integrate BW.**

## Baseline and scope

v0.1.0: 10 YAML profiles, `tabular`/`reno`/`jz` pipelines, 19 passing local tests (synthetic fixtures). Code and sample inputs examined 2026-11-23. Source-derived process details: `docs/processes/` and `docs/references/MANUAL_EVIDENCE.md`.

## Current repository facts

- Generic tabular output generally preserves incoming columns minus configured drops; no definitive SAP column schema in manual.
- `--reference` validates names/order, **not** cell types or business keys.
- JZ `jz.py` accepts only normalized `{Category, Paid Hours, OT Hours}`; raw HC invoice-hours workbook not yet supported.
- `gbr.yaml` uses DMY date parsing and `excel_hours` fraction conversion.
- `dayforce_*.yaml` only warn about external refresh; cannot execute it.

## Unknowns and human decisions

Need sanitized raw input (all ten profiles, including both CBG and Dayforce variants), approved final template per profile, sample exact paid/OT totals, GBR time units, JZ raw HC invoice/OT mapping, CCB row-key approval for the 65.8→75.8 example, Taiwan destination date/CSV conventions, week-date policy confirmation. Cannot manufacture these artifacts or business decisions.

## Milestones / Progress

- [x] M0 — enumerate ten profiles and document unresolved manual ambiguities (2026-11-23).
- [ ] M1 — collect and approve source/destination samples, including confidential-data sanitization.
- [ ] M2 — snapshot expected manual outputs and derived totals for each profile.
- [ ] M3 — harden profile schemas/parser contracts and add golden + negative fixture tests.
- [ ] M4 — update one process page per workflow with exact verified output schema and comparison results; get operational signoff.

## Step-by-step design

For each profile: inspect raw workbook header/sheet/locale/units; create redacted fixture and approved expected output; pin profile mappings; add regression test reading actual structure; compare row count, date cells, column names/order/types and totals. Make changes within corresponding pipeline or helpers. For JZ add raw-source extraction only after receiving HC cell locations and paid-vs-OT logic; never use invoice hours as paid/OT without authorization. Keep staged JZ as current supported input until then.

## Verification and acceptance

`uv run pytest -q`; `uv run python scripts/check_docs.py`; `uv run factoryprep validate --profile <id> --input <fixture> --strict --reference <approved-template>`; `prepare` and independently compare with approved output. Record for every profile tested file hash, schema version, input/output sums, row counts, differences, approval. Completion requires every profile to pass; synthetic-only results do **not** count.

## Evidence / execution log

2026-11-23: baseline `PYTHONPATH=src pytest -q --disable-warnings --maxfail=1` → `19 passed in 0.63s` on synthetic/current tests. Not a real-data certification.

## Decisions

2026-11-23: keep BW out of scope (ADR-0001); preserve existing generic profile-based pipeline while certifying sources (ADR-0002); block speculative raw JZ parsing (ADR-0005).

## Risks / rollback

Original source never overwritten; compare prepared artifacts in an isolated directory; restore previous YAML and fixtures if candidate mapping diverges. Do not deploy changes without signoff on real samples.

## Next step

Obtain sanitized SGP/GBR/CBG Core/Starline/CCB/Reno/JZ/Dayforce CCB/Dayforce non-CCB/Taiwan samples and approved template headers; begin with `jz` and `gbr` because their numeric semantics are most uncertain.
