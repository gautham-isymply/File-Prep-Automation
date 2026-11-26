# Verification strategy and release gates

## Fast local checks

```bash
uv sync --extra dev
uv run pytest -q
uv run python scripts/check_docs.py
uv run ruff check src tests
```

**Current evidence:** see [current state](../progress/CURRENT_STATE.md) for exact
test/check counts and limitations. Tests use synthetic temporary files; they do not
certify real source layouts or destination schemas.

## Layers of assurance

1. *Unit/functional synthetic*: header detection, date fraction handling, number parsing, exclusions, corrupt cells, override safety, destination headers. See the current test count and command evidence in [current state](../progress/CURRENT_STATE.md).
2. *Integrity*: `scripts/check_docs.py` verifies Markdown local links, ten profile runbooks and mirrored YAML equality; tests also compare profile bytes.
3. *Golden real-world sanitized fixtures* (**not yet done**): each profile's approved raw layout, expected output schema/types/totals, manual parity and negative cases.
4. *Operational signoff* (**not yet done**): business approval of numeric precision, time unit semantics, date/week semantics, file naming and retention policy; no BW tests in scope.

## Minimum matrix per process

Required positive: input variant works, output headers/order/types and totals correct, report `PREPARED` with expected checks. Negative: missing column, duplicate semantic header, wrong date locale, negative/null hours, unknown label, extra/missing rows, stale reference, unauthorized correction (when applicable). Batch: partial failures and unique report paths. Source workbook hash must remain unchanged. At least one test must show reconciliation filters **do not** remove source rows.

## Processing steps and executable evidence

Follow each profile's [runbook](../processes/index.md) for manual-derived preparation
steps. The shared implemented sequence and its regression evidence are:

| Step / operation | Tests and asserted outcome |
|---|---|
| 1. Select explicit profile or detect conservatively; load config | [Config failures](../../tests/test_config_failures.py): invalid identity, YAML, processor, output, columns, aliases, dates, scan limits, flags, exclusions, metrics, sums, JZ mappings and corrections reject. [CLI/file tests](../../tests/test_io_cli.py): filename alone cannot identify a profile. |
| 2. Read source without mutation; choose sheet and header | [Profile matrix](../../tests/test_validation_matrix.py): the eight original XLSX profiles plus Taiwan CSV output with canonical/alias headers; Reno uses the dedicated timecard test and preamble; every required header missing or duplicate; source hash unchanged. [CLI/file tests](../../tests/test_io_cli.py): CSV comma/semicolon/pipe, TSV, BOM/quotes, XLSX and XLSM containers, missing/unsupported/damaged sources, sheet ambiguity and explicit selection. |
| 3. Normalize dates, numeric fields and hours | [Profile matrix](../../tests/test_validation_matrix.py): every configured numeric/time field rejects blank, negative, malformed, boolean and Excel-error values; every date field rejects blank/impossible dates. [Operations](../../tests/test_operations.py): currency, clocks, durations, locale, serial dates, GBR ambiguity blocking/explicit units and large-hour warnings. |
| 4. Apply declared cleanup and reviewed changes | [Existing profile tests](../../tests/test_profiles.py): SGP scheduled columns, SSI Shift/semicolon, CCB Notes/correction, Dayforce exclusion. [Operations](../../tests/test_operations.py): blank/summary cleanup; exclusion-label mismatch; corrections require unique match, target and old value. |
| 5. Check quality and compute diagnostics | [Operations](../../tests/test_operations.py): all seven tabular profiles' paid/OT metrics with nonmatching rows retained, null/duplicate/date-continuity/sum/schema checks; JZ five exact mappings and totals with missing/unknown/duplicate/week failures. |
| 6. Compare destination header template and gate | [CLI/file tests](../../tests/test_io_cli.py): duplicate/missing/extra/empty/multisheet reference rejection; validation-only and strict statuses. [Existing profile tests](../../tests/test_profiles.py): reference reordering, CCB strict warning gate. |
| 7. Write candidate and JSON audit; operate CLI/batch | [CLI/file tests](../../tests/test_io_cli.py): XLSX date type/format (also profile matrix), CSV dates/order, source overwrite rejection, prior-output preservation, temporary-file cleanup on write failure, report contents, command exit codes and batch continuation with distinct reports. |

File parsing retries delimiter detection on the first nonblank header line when
whole-sample sniffing fails. Invalid Excel ZIP containers become audited preparation
failures. Bundled profile YAML and business transformations are unchanged.

## Explicit assurance limits

Unknown JZ labels are blocking; unknown ordinary tabular labels generally only affect
diagnostic selection. Generic summary removal remains heuristic. This suite does not
prove arbitrary corruption recovery, VBA preservation, external data freshness,
concurrency safety, destination types, or business-approved week/paid-versus-OT rules.
Config structure is guarded, but full semantic preflight remains TD-002. These are
implemented-behavior tests, not evidence that unresolved manual assumptions are true.

## Definition of done for a change

Updated code, both YAML copies, runbook, tests, actual check results in execution log, and current state/debt/ADRs if affected. For production claims, attach real sanitized fixture evidence and approval. **Synthetic success alone is insufficient.**
## Executable verification

`tests/test_executable.py` covers safe repeat drops, source preservation, mixed
failures, ambiguous detection, explicit profiles, strict mode, launcher dispatch
and one-file bootloader console ownership. `scripts/smoke_exe.py` copies a built EXE
outside the checkout, removes Python path overrides and checks help, all ten
embedded profiles after rebuilding, prepare/validate, bare multi-file paths, repeated drops and JSON
failure reports. Fixtures are synthetic. This does not certify the Explorer gesture,
console lifetime on a clean PC, or real source/destination contracts.

## 2026-11-26 manual correction evidence

[Manual correction tests](../../tests/test_manual_corrections.py) cover Reno DMY/comma/two-header layouts, blank/status/date-coverage gates and explicit policies; GBR unit ambiguity; CBG detail retention/numeric text/table bounds and combined approved-filter audits; SSI date ambiguity; exact Dayforce exclusions/weekly diagnostics/refresh evidence and combined US CLI; JZ approved raw-cell extraction with label/week/value failures; Taiwan missing boundary and duplicate dates; correction revalidation and source/report path protection. Existing round trips now provide explicit weeks and synthetic refresh attestations where required. All fixtures remain synthetic. See current state/execution log for actual command results.
