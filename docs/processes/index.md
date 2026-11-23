# Source preparation runbooks — one per CLI profile

**Basis:** manual pages and actual v0.1.0 YAML/code, audited 2026-11-23. Each runbook separates the stated manual procedure from implemented behavior and unverified assumptions. **Do not use a runbook alone as a production-certified schema.**

| CLI `--profile` | Source | Processor | Manual pages | Runbook |
|---|---|---|---|---|
| `sgp` | SGP attendance | tabular | 1–3 | [SGP](sgp.md) |
| `gbr` | GBR WorkSegments | tabular | 5–11 | [GBR](gbr.md) |
| `cbg_core` | CBG Starline Core2 | tabular | 12–13 | [CBG Core](cbg_core.md) |
| `cbg_starline` | CBG Starline SSI | tabular | 13–19 | [CBG SSI](cbg_starline.md) |
| `ccb` | CCB summary | tabular | 20–26 | [CCB](ccb.md) |
| `reno` | Reno Temp Timecards | reno | 26–28 | [Reno](reno.md) |
| `jz` | JZ-BUS and JZ-DAT | jz (staged) | 29–31 | [JZ combined](jz.md); [BUS](jz_bus.md); [DAT](jz_dat.md) |
| `dayforce_ccb` | Dayforce CCB | tabular | 32–35 | [Dayforce CCB](dayforce_ccb.md) |
| `dayforce_non_ccb` | Dayforce non-CCB | tabular | 32–35 | [Dayforce non-CCB](dayforce_non_ccb.md) |
| `taiwan` | Taiwan | tabular | 36–39 | [Taiwan](taiwan.md) |

**Date convention:** Sunday start → Saturday end per manual introduction. SQL example discrepancies are documented in [evidence map](../references/MANUAL_EVIDENCE.md). No BW execution. Run a profile with `uv run factoryprep prepare --profile <id> --input SOURCE.xlsx`; use `.csv` output for Taiwan. JZ requires `--week-ending` and normalized staging source.
