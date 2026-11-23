# Current state / agent resume checkpoint

**Snapshot:** 2026-11-23; `factoryprep` version `0.1.0` as found in project archive. **Assurance:** functional synthetic-test baseline, **not** real-world destination certification.

## Implemented and verified locally

- Python package with uv-compatible `pyproject.toml`; Typer CLI: `profiles`, `detect`, `describe`, `prepare`, `validate`, `batch`.
- 10 YAML profiles: `sgp`, `gbr`, `cbg_core`, `cbg_starline`, `ccb`, `reno`, `jz`, `dayforce_ccb`, `dayforce_non_ccb`, `taiwan`.
- Three processors (`tabular` for 8, `reno`, `jz`); report severity and output gate; optional header reference and reviewed corrections.
- `PYTHONPATH=src pytest -q --disable-warnings --maxfail=1` run 2026-11-23: **19 passed in 0.63 seconds**. This proves the checked-in tests, not real-source certification.
- Harness documentation assembled from the uploaded manual and source inspected on 2026-11-23; see [execution log](EXECUTION_LOG.md) for checker result.

## Not implemented / unverified

- No BW loading, DTP/ADSO operations, email/PBI or external Excel refresh. Intentionally excluded.
- Direct parsing of arbitrary original JZ workbook HC section: **not supported**; normalized staging sheet required.
- Real destination header/types/templates for most processes; some manual labels and dates ambiguous.
- `uv.lock` absent (previous environment lacked package registry access). Do not claim a locked reproducible environment; `uv sync --extra dev` will resolve dependencies where accessible.
- No input-source/business signoff or operational pipeline history; data quality reports are per-run only.

## Next 2 actions

1. [EP-0001](../exec-plans/active/EP-0001-source-contract-certification.md): get sanitized raw files + approved target template; resolve JZ, GBR, CBG and Taiwan rules.
2. [EP-0002](../exec-plans/active/EP-0002-harness-guardrails.md): grow mechanical config/type/dependency checks; execute docs checker each change.

## Where to read next

[Process index](../processes/index.md) → one file, [architecture](../../ARCHITECTURE.md), [tech debt](../exec-plans/tech-debt-tracker.md). Updated state must include exact command evidence and limitations, not guessed progress.
