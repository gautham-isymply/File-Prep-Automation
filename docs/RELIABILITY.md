# Reliability and recovery

**Implemented:** source read-only; output written to temporary sibling and renamed on pass; JSON report on completion of `engine.run`; deterministic header-based detection with refusal for ambiguous matches; errors block output; warnings block only under `--strict`.

**Not guaranteed:** atomicity across output + report; isolation across two concurrent CLI runs targeting same path; schema validation of all target cell types; external-query freshness; complete file provenance/hashes; user-friendly report when config/autodetection fails before `run()` establishes report context; automatic retries/rollback or a central execution-history database.

## Failure matrix

| Failure | Effect | Action |
|---|---|---|
| Missing/invalid source | failed run and report when handled in engine | inspect `PREPARATION_FAILURE` |
| Mismatch with reference headers | no new output | obtain approved target schema |
| Warning (regular) | may prepare with warnings | review JSON; consider `--strict` |
| Warning (`--strict`) | status FAILED, no new output | remediate or document explicit exception |
| Failed run with existing output | old file remains | **never** ship the stale output |
| Batch partial failure | other jobs continue; exit 2 | inspect each report separately |
| PowerQuery workbook not refreshed | CLI warns only, cannot detect stale values | refresh externally and rerun |

Recommendations, not yet implemented: content hashes in reports; run IDs; output/report atomic bundles; structured terminal logs; concurrency-safe output lock; PII-safe report retention; schema certification and snapshot comparisons. All planned work must follow [ExecPlans](PLANS.md) and [debt](exec-plans/tech-debt-tracker.md).
