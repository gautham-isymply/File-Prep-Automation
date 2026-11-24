# Current state / agent resume checkpoint

**Snapshot:** 2026-11-24; `factoryprep` version `0.1.0` as found in project archive. **Assurance:** functional synthetic-test baseline, **not** real-world destination certification.

## Implemented and verified locally

- Python package with uv-compatible `pyproject.toml`; Typer CLI: `profiles`, `detect`, `describe`, `prepare`, `validate`, `batch`.
- 8 YAML profiles: `sgp`, `gbr`, `cbg_core`, `cbg_starline`, `ccb`, `jz`, `dayforce_ccb`, `dayforce_non_ccb`.
- Two processors (`tabular` for 7, `jz`); report severity and output gate; optional header reference and reviewed corrections.
- Repository `.gitignore` excludes Python bytecode caches (`__pycache__/`, `*.py[cod]`); verified with `git check-ignore` on 2026-11-24.
- `uv run pytest -q` run 2026-11-24: **17 passed in 2.81 seconds** (synthetic fixtures). `uv run python scripts/check_docs.py`: **PASS**, 51 Markdown files / 8 mirrored profiles.
- `uv run ruff check src tests --output-format concise`: **failed**, 66 pre-existing findings; comparison with `HEAD` found zero new findings (TD-017).
- Scope reduction completed in [EP-0003](../exec-plans/completed/EP-0003-workflow-scope.md); CLI inventory and retired-reference audit verified.
- Harness documentation assembled from the uploaded manual and source inspected on 2026-11-23; see [execution log](EXECUTION_LOG.md) for checker result.

## Not implemented / unverified

- No BW loading, DTP/ADSO operations, email/PBI or external Excel refresh. Intentionally excluded.
- Direct parsing of arbitrary original JZ workbook HC section: **not supported**; normalized staging sheet required.
- Real destination header/types/templates for most processes; some manual labels and dates ambiguous.
- A local `uv.lock` exists in this checkout; it is not tracked. Development dependencies were installed with `uv sync --extra dev` on 2026-11-24. A committed reproducibility contract remains unverified.
- No input-source/business signoff or operational pipeline history; data quality reports are per-run only.

## Next 2 actions

1. [EP-0001](../exec-plans/active/EP-0001-source-contract-certification.md): get sanitized raw files + approved target template; resolve JZ, GBR and CBG rules.
2. [EP-0002](../exec-plans/active/EP-0002-harness-guardrails.md): grow mechanical config/type/dependency checks; execute docs checker each change.

## Where to read next

[Process index](../processes/index.md) → one file, [architecture](../../ARCHITECTURE.md), [tech debt](../exec-plans/tech-debt-tracker.md). Updated state must include exact command evidence and limitations, not guessed progress.
