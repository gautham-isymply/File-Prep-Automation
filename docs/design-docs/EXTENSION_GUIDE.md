# Extending a file-load workflow

## For a new tabular source

1. Identify manual source pages and **obtain a sanitized real file** plus approved target template; record open questions in `docs/references/MANUAL_EVIDENCE.md` or the process doc.
2. Add one profile YAML in `config/profiles/<id>.yaml`; set required source headers, verified aliases, date conventions, numeric conversion, intended row drops and advisory reconciliations.
3. Copy the profile **identically** to `src/factoryprep/profiles/<id>.yaml`.
4. Add `docs/processes/<id>.md` with source evidence, implementation rules, output contract, ambiguities, expected tests; link it in process index.
5. Add tests using realistic sanitized workbook structures; cover missing, duplicate, misspelled labels, date ambiguity, unexpected columns, negatives and no silent data deletion.
6. Run `uv run pytest -q`, `uv run python scripts/check_docs.py`; record actual results in `docs/progress/EXECUTION_LOG.md`, update state and debt.

## For a structurally different source

Implement a processor in `src/factoryprep/pipelines/` with `Prepared` + `RunReport` as its contract, add a controlled dispatch in `engine.py`, document an ADR if introducing a new architectural boundary. Reuse `transform.py` parsers and `io.py` readers; do not duplicate report status semantics. Reno and JZ are examples.

## Production acceptance (not currently completed)

A workflow is *certified* only after real (redacted) source sample, exact destination schema, output totals, source-to-output row counts, manual-vs-CLI comparison, negative cases and required business signoff are linked in its process runbook. Mere 19-test functional pass does not imply this certification.
