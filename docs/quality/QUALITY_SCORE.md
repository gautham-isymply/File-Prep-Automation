# Quality scorecard — evidence, not a vanity grade

**Evaluated:** 2026-11-23. Scores: 0 unknown/unimplemented; 1 manual-based provisional; 2 tested synthetic; 3 tested with representative sanitized raw source and approved target; 4 operationally certified. No workflow currently has confirmed level 3 or 4 evidence in this repository.

| Profile | Current level | Main blocker |
|---|---:|---|
| sgp | 2 | exact destination template / date cell semantics |
| gbr | 2 | time-fraction semantics and source samples (TD-004) |
| cbg_core | 2 | raw header/totals structure and target layout |
| cbg_starline | 2 | MDY vs YMD mismatch (TD-009) |
| ccb | 2 | approved correction key, Dept vs CC equivalence (TD-005) |
| jz | 1 | normalized staging works in synthetic tests; raw HC extraction absent (TD-003) |
| dayforce_ccb | 2 | refresh freshness and exact exclusions |
| dayforce_non_ccb | 2 | refresh and fuzzy substring cost-center matching (TD-016) |

## Layer scores

| Layer | Level | Evidence / caveat |
|---|---:|---|
| Python CLI + processors | 2 | synthetic tests; see [current evidence](../progress/CURRENT_STATE.md); limited real-file evidence |
| Config/profile validation | 1 | shallow YAML structural checking only |
| Docs and retrieval harness | 2 | link/coverage/mirror checker in repo; no CI integration |
| Real business reconciliation | 0 | no verified business goldens or BW totals (outside scope) |
| Reporting/audit trail | 1 | per-run JSON, no complete run ledger or hash/retention |

Upgrade a score only with dated evidence linked to an executed plan and test artifacts. Do not increase scores because documentation is more extensive.
