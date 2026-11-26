# Quality scorecard — evidence, not a vanity grade

**Evaluated:** 2026-11-26. Scores: 0 unknown/unimplemented; 1 manual-based provisional; 2 tested synthetic; 3 tested with representative sanitized raw source and approved target; 4 operationally certified. No workflow currently has confirmed level 3 or 4 evidence in this repository.

| Profile | Current level | Main blocker |
|---|---:|---|
| sgp | 2 | exact destination template / date cell semantics |
| gbr | 2 | time-fraction semantics and source samples (TD-004) |
| cbg_core | 2 | raw header/totals structure and target layout |
| cbg_starline | 2 | MDY vs YMD mismatch (TD-009) |
| ccb | 2 | approved correction key, Dept vs CC equivalence (TD-005) |
| reno | 2 | timecard agency/row semantics, approved output template |
| jz | 1 | normalized staging works in synthetic tests; explicit raw-cell extraction tested synthetically; actual HC contract missing (TD-003) |
| dayforce_ccb | 2 | refresh freshness and exact exclusions |
| dayforce_non_ccb | 2 | hash-bound refresh evidence/exact code matching implemented; real label variants unverified (TD-016) |
| taiwan | 2 | exact CSV date/column contract (TD-008) |

## Layer scores

| Layer | Level | Evidence / caveat |
|---|---:|---|
| Python CLI + processors | 2 | synthetic tests; see [current evidence](../progress/CURRENT_STATE.md); limited real-file evidence |
| Config/profile validation | 2 | synthetic negative tests for consumed structures; full semantic preflight remains TD-002; see [test matrix](TEST_STRATEGY.md) |
| Docs and retrieval harness | 2 | link/coverage/mirror checker in repo; no CI integration |
| Real business reconciliation | 0 | no verified business goldens or BW totals (outside scope) |
| Reporting/audit trail | 2 | source hashes, row audit and combined weekly reports tested synthetically; no complete run ledger/retention |

Upgrade a score only with dated evidence linked to an executed plan and test artifacts. Do not increase scores because documentation is more extensive.
