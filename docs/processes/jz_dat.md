# JZ-DAT profit center subsets (shares `jz` CLI profile)

**Manual:** pp. 29–30. **Parent runbook:** [JZ combined](jz.md). **Profile:** [`jz.yaml`](../../config/profiles/jz.yaml). This is **not** an independent CLI profile.

| Incoming direct-hours group | Output Segment | Plant | Profit center | Company code |
|---|---|---|---|---|
| Cables | DAT | 3614 | COP | 3600 |
| Fibra | DAT | 3614 | FIB | 3600 |
| Connectors | DAT | 3614 | RAC | 3600 |
| Servertech | DAT | 3614 | DAT | 3600 |

- Manual requires Sunday start date of the selected week and separate Paid/OT values for each profit center.
- Implemented `jz` processor maps normalized `Category`, `Paid Hours`, `OT Hours` and requires exactly one of each of five shared BUS/DAT categories.
- Unresolved: raw HC invoice-hours cells and how paid versus OT are derived. No guessed split permitted ([TD-003](../exec-plans/tech-debt-tracker.md)).
- Acceptance: independent approved raw-source extraction yields 4 DAT rows with exact profit centers, plant and totals, plus 1 BUS row in a single combined output.

Command: `uv run factoryprep prepare --profile jz --input NORMALIZED_JZ.xlsx --week-ending 2026-02-28 --output jz_prepared.xlsx`.
