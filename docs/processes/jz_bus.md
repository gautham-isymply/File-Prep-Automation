# JZ-BUS profit center subset (shares `jz` CLI profile)

**Manual:** pp. 29–30. **Parent runbook:** [JZ combined](jz.md). **Profile:** [`jz.yaml`](../../config/profiles/jz.yaml). This is **not** an independent CLI profile.

- Manual source group: `Direct Hours (Starline)`; `HC` invoice-hours workbook context is mentioned but raw extraction logic is not specified.
- Documented template row: `Segment=BUS`, `Plant=3618`, `Plant name=Santa Teresa`, `Profitcent=BUSWAY`, `Companycode=3600`, `Date=Sunday of selected week`, `Paid Hours` and `OT Hours` supplied from approved source split.
- Implemented: normalized staging input row `Category: Direct Hours (Starline)` with independent numeric `Paid Hours`, `OT Hours`; mapped to BUSWAY by `pipelines/jz.py`.
- Unresolved: location and semantics of original invoice-hours HC source numbers. Neither use HC directly as paid nor fill OT with zero without business confirmation ([TD-003](../exec-plans/tech-debt-tracker.md)).
- Acceptance: real approved source split reconstructs template BUS row and totals; no duplicate/unknown categories.

Command: `uv run factoryprep prepare --profile jz --input NORMALIZED_JZ.xlsx --week-ending 2026-02-28 --output jz_prepared.xlsx`. This produces **all five** JZ rows, not just BUS.
