# Verification strategy and release gates

## Fast local checks

```bash
uv sync --extra dev
uv run pytest -q
uv run python scripts/check_docs.py
uv run ruff check src tests
```

**Baseline evidence:** 19 tests passed on 2026-11-23 using installed Python env; `uv.lock` does not exist yet. The `ruff` command is a desired check, not confirmed passing at baseline. Failure of a code-quality command must be recorded, not silently ignored.

## Layers of assurance

1. *Unit/functional synthetic*: header detection, date fraction handling, number parsing, exclusions, corrupt cells, override safety, destination headers. See the current test count and command evidence in [current state](../progress/CURRENT_STATE.md).
2. *Integrity*: `scripts/check_docs.py` verifies Markdown local links, 10 profile docs and mirrored YAML equality.
3. *Golden real-world sanitized fixtures* (**not yet done**): each profile's approved raw layout, expected output schema/types/totals, manual parity and negative cases.
4. *Operational signoff* (**not yet done**): business approval of numeric precision, time unit semantics, date/week semantics, file naming and retention policy; no BW tests in scope.

## Minimum matrix per process

Required positive: input variant works, output headers/order/types and totals correct, report `PREPARED` with expected checks. Negative: missing column, duplicate semantic header, wrong date locale, negative/null hours, unknown label, extra/missing rows, stale reference, unauthorized correction (when applicable). Batch: partial failures and unique report paths. Source workbook hash must remain unchanged. At least one test must show reconciliation filters **do not** remove source rows.

## Definition of done for a change

Updated code, both YAML copies, runbook, tests, actual check results in execution log, and current state/debt/ADRs if affected. For production claims, attach real sanitized fixture evidence and approval. **Synthetic success alone is insufficient.**
