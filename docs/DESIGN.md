# Design overview

**Target:** one repeatable command per file, profile-driven transformation and validation, candidate destination file, and machine-readable audit report. **Not a roadmap:** current implementation and unverified requirements are distinguished in [state](progress/CURRENT_STATE.md).

The CLI is a *preparation and quality gate*, not an integration service. It does not call SAP BW, refresh Excel external queries, send reminders, or validate PBI. Inputs are untrusted. Profile YAML is reviewed code, not a workbook-provided instruction. A run is deterministic conditional on file bytes, profile, selected sheet, specified week, reference, overrides, Python/dependency versions.

## Minimal modules

- Readers/writers `io.py` support xlsx/xlsm/csv/tsv input and xlsx/csv output; formulas are loaded as cached values.
- `detect.py` and `config.py` select/load the profile (no inferred JZ paid/OT mapping).
- `engine.py` dispatches to `tabular`, `reno`, or `jz` and gates output based on `RunReport`.
- Profile rules control header aliases, drops, date display, numeric conversions, reconciliations, and narrow exclusions.
- `--reference` optionally compares the output header to an externally approved target schema.

See [architecture](../ARCHITECTURE.md), [module contracts](design-docs/MODULE_CONTRACTS.md), [profile contract](design-docs/PROFILE_CONTRACT.md), and [issue contract](quality/REPORT_CONTRACT.md). Source-derived process differences live in [processes](processes/index.md).

## Constraints and decisions

| Decision | Record |
|---|---|
| Separate source QA from BW | [ADR-0001](decisions/ADR-0001-preparation-only.md) |
| Use YAML and limited processing strategies | [ADR-0002](decisions/ADR-0002-profile-pipeline-boundary.md) |
| Stop on errors / audited corrections only | [ADR-0003](decisions/ADR-0003-quality-gate.md) |
| Sunday-to-Saturday and source discrepancy | [ADR-0004](decisions/ADR-0004-week-boundary.md) |
| Do not guess JZ HC mapping | [ADR-0005](decisions/ADR-0005-jz-provisional-source.md) |

Proposed additions: real destination schema descriptors, fixture-based certification, stronger profile schema lint, row lineage and hardened audit artifacts; **not in v0.1.0**. Track them in [debt](exec-plans/tech-debt-tracker.md) and [active plan](exec-plans/active/EP-0001-source-contract-certification.md).
