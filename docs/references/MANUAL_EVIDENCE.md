# Original manual evidence map / ambiguity register

**Source:** uploaded `FactoryInsights_MANUAL_LOAD_Process.docx`, 39 pages, heading “Factory Insights Manual Load/Process.” This source is **not included in this public-ready code ZIP** because it may contain internal screenshots/data. Page numbers refer to the user-provided document; process summaries below are compact paraphrases. Do not invent source filenames, business keys or destination columns not visible there.

| Manual pages | Process/rules directly visible | Runbook |
|---|---|---|
| 1–2 | Weekly process description; SGP convert DATE to `yyyymmdd`, drop scheduled time columns | [SGP](../processes/sgp.md) |
| 5–9 | GBR DATEIN/DATEOUT DMY→YYYYMMDD; time fractions ×24 for REG/O1/O2 | [GBR](../processes/gbr.md) |
| 12–13 | CBG Core2 data-only `Core` tab and numeric Pay Rate | [Core](../processes/cbg_core.md) |
| 13–16 | CBG SSI header/trailer removal, W/E date processing, delete Shift, numeric BRD | [Starline](../processes/cbg_starline.md) |
| 20–22 | CCB one highlighted 65.8→75.8 correction, four numeric hours columns, Notes removal | [CCB](../processes/ccb.md) |
| 29–30 | JZ: HC invoice-hours context, five Direct Hours category transfers, Sunday template date | [JZ](../processes/jz.md) |
| 32–35 | Two Dayforce files; auto-refresh on Excel open; exclude CCB Receiving Farmingdale; source reconciliation filters | [Dayforce CCB](../processes/dayforce_ccb.md), [non-CCB](../processes/dayforce_non_ccb.md) |

## Ambiguities and misleading artifacts

1. Manual introduction says **Sunday–Saturday**; some later SQL examples instead show dates from Monday through Sunday or other different weeks. CLI follows the introduction. **TD-010**.
2. GBR original hour cells may mix Excel fraction and decimal numeric data; converting `0.5` to `12` without verified cell format can be ambiguous. **TD-004**.
3. CBG Starline screenshots show US-style date strings, while text says choose YMD in wizard, then display `m/d/yyyy`. Current config uses MDY. **TD-009**.
4. CCB correction is one highlighted cell; the manual does not give a unique stable row key for automated matching. **TD-005**.
5. JZ raw HC column is mentioned but detailed machine-readable source layout and paid/OT decomposition are not shown. Current staged source is a CLI design assumption, **not** manual instruction. **TD-003**.
6. Dayforce refresh in Excel happens outside the Python CLI; cannot assume fresh data. **TD-007**.
7. All SAP DTP names, ADSO deletions/activations and post-load SQL checks belong to **BW processes outside scope**. They provide reconciliation context but are not calls implemented in Python.

The business owner must resolve ambiguities with real sanitized files and approved templates before operational certification. See [EP-0001](../exec-plans/active/EP-0001-source-contract-certification.md).
