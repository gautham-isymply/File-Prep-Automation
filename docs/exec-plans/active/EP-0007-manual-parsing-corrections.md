# EP-0007 â€” prepare every manual source using its documented method

**State:** active — engineering corrections implemented; real source/schema certification blocked  
**Updated:** 2026-11-26  
**Owner:** unassigned  
**Linked debt:** TD-001, TD-003/004/005/007/008/009/010/015/016, TD-018/019/020/021

## Objective

An operator can prepare each of the manual's ten file workflows with explicit source contracts, trace every transformation to the manual, and compare the result with an independently prepared expected file. The source-contract primitives and supported safeguards are implemented with synthetic tests. Real inputs, missing business decisions and destination schemas remain uncertified; see the implementation checkpoint below.

## Baseline and scope

Reviewed the actual `C:\Users\DELL\Downloads\FactoryInsights_MANUAL_LOAD_Process.docx` read-only on 2026-11-26. SHA-256: `DDB3FB34EFEE12FF15B21D4AA62385B15F099803D440A70341E1587C1315674D`.

Evidence pointers below use **P numbers**, the one-based positions of direct `w:body/w:p` elements in `word/document.xml`, including empty paragraphs. These are reproducible XML paragraph positions, not Word page numbers. Existing page pointers remain in the [manual evidence map](../../references/MANUAL_EVIDENCE.md). Inspected embedded Reno, JZ and SSI screenshots as well as text. Source text describes eight process headings: SGP, GBR, CBG, CCB, Reno, JZ-BUS/JZ-DAT, Dayforce, Taiwan. CBG and Dayforce each have two input workflows, giving ten existing profile IDs; JZ produces five category records across two plants through one profile.

The document's instructions are evidence about a business procedure. They are not authorization to execute emails, load dummy hours, delete SAP records, run DTPs, activate ADSOs, refresh Excel connections or update PBI. This plan covers local file parsing/preparation and source reconciliation only. Existing source workbooks remain read-only. The initial manual review changed no runtime behavior; the subsequent implementation checkpoint records code/YAML/test changes. Existing uncommitted work is preserved.

## Current repository facts

### Implementation checkpoint — 2026-11-26

- Added per-column hours units and blocking ambiguous fractions; finite/grouped-number validation; Reno DMY/comma contract with audited explicit blank/status policies and missing-day blocks.
- Added first-column/declared-column summary rules, repeated-header and explicit table boundaries, skipped-row audit, stronger Core headers and numeric metric validation. Core department filters remain explicitly unconfirmed. SSI ambiguous slash dates block under conservative auto parsing.
- Added requested-week metrics without trimming outputs, exact Dayforce code/label filters/exclusion, hash-bound external refresh attestations required in normal/strict mode, source hashes/date ranges, full expected-week Taiwan continuity and duplicate-date warnings. CCB replacements are revalidated; Reg and both OT components are reported.
- Added optional raw JZ extraction behind a reviewed custom cell contract (separate Paid/OT cells, exact labels/source week, provenance); default profile remains staged with no guessed HC map.
- Added reconcile command/local audit module with matching-period/contract/evidence gates; documented in ADR-0006 and operations/report contracts. Updated all ten mirrored profile pairs and process pages.
- Migrated CLI options to Annotated form and cleaned touched-file lint; full Ruff now passes. Tests and packaging evidence are in the execution log.

### Reviewed baseline before implementation

- Ten profile pairs live in `config/profiles/` and `src/factoryprep/profiles/`; both copies must remain identical.
- Eight profiles use [tabular.py](../../../src/factoryprep/pipelines/tabular.py); [reno.py](../../../src/factoryprep/pipelines/reno.py) aggregates dates; [jz.py](../../../src/factoryprep/pipelines/jz.py) accepts normalized staging only.
- [transform.py](../../../src/factoryprep/transform.py) supplies date/number/duration parsing. `parse_number` removes commas, so text `8,75` becomes 875. `excel_hours` assumes unformatted fractions are days and warns, but normal mode can still write output.
- Reno `_dates_in_row` uses MDY for text, although its manual screenshot displays DMY. Reno skips blank daily cells, initializes missing day totals to zero, and rejects `term` as numeric text. These are current behaviors, not approved business rules.
- Tabular summary detection skips a row if **any** cell equals a total marker; it does not establish a verified data-table boundary. Core requires only `Pay Rate`; its hours metrics sum only already-numeric values.
- `_calculate_metrics` has category filters but no date-window predicate. Dayforce monthly files therefore produce category/location totals across the retained month rather than the requested weekly reconciliation window.
- Dayforce cost-center matching uses normalized substring containment, including the exclusion code. Header references verify names/order only, not destination data types.
- Existing tests are synthetic. See [current state](../../progress/CURRENT_STATE.md) and [EP-0001](EP-0001-source-contract-certification.md) for certification prerequisites; this plan supplies the concrete correction backlog for that certification work.

## Unknowns and human decisions

Obtain sanitized raw files and approved prepared examples for all ten workflows, including multi-tab invoices, real timecard structure and both monthly Dayforce files. Record source version, worksheet, header row, locale, numeric units, expected period, output schema/types and independently calculated totals. Required decisions are assigned to the business/source owner, currently unassigned:

1. GBR: identify raw Excel duration versus already-converted decimal hours, including unformatted fractional values.
2. SSI: resolve YMD wizard instruction versus `03/14/2026` screenshot content. Do not choose a new locale by trial and error.
3. CCB: approve a unique record key and old/new value for the example correction; confirm whether `Dept` and `CC` really denote the same field.
4. Reno: confirm DMY text, decimal-comma representation, `term` meaning, blank-day meaning and where Saturday data comes from. Screenshot source dates are 2026-02-28 through 2026-03-06 (Saturdayâ€“Friday), while output dates are 2026-03-01 through 2026-03-07. Do not shift dates or fabricate the final Saturday.
5. JZ: provide actual HC invoice-hours cells and separately approved Paid/OT sourcing. Neither duplicate invoice hours into both fields nor assume OT zero. Confirm source week: email image says WE 2/27, text uses 2/28, and template screenshot displays 2/15 dates.
6. Dayforce: approve refresh evidence and exact code/label grammar; define how a requested week intersects monthly data without trimming the monthly prepared file.
7. Taiwan: approve date locale, CSV encoding/order/precision and expected date calendar, including nonproduction days.
8. All profiles: approve complete destination schemas and source duplicate keys. SAP aggregate duplicate keys in the manual must not be reused blindly for employee-level source rows.

The supplied DOCX has broken image references `rId1729903030`, `rId1181404668`, `rId1666860692` to absent `/media/image2d.png`, `/media/image2e.png`, `/media/image2f.png`. They affect Core preparation/pivot/filter evidence (P175/P210/P215). The Core department filter at P211 is not enumerated in available text. Obtain repaired evidence or an owner-approved list; do not invent departments. Do not commit confidential extracted screenshots.

## Milestones / Progress

- [x] M0 â€” inspect supplied manual text, relevant available screenshots, profile YAMLs, processing code and current tests; write this correction plan.
- [ ] M1 â€” capture approved source contracts and independently prepared expected outputs; resolve the decisions above per profile, allowing independent profiles to proceed.
- [ ] M2 â€” implement explicit numeric/date/row-boundary and diagnostic-window primitives with focused regression cases.
- [ ] M3 â€” apply the ten process corrections below, one workflow at a time; update its runbook, mirrored YAMLs and meaningful tests together.
- [ ] M4 â€” compare real sanitized fixtures end to end, record output cells/bytes and totals, and obtain source-owner acceptance under EP-0001.
- [ ] M5 â€” rebuild executable after code/config acceptance and rerun standalone smoke; record ten embedded profiles. Current binaries predate restored workflows.

## Step-by-step design

### 1. SGP attendance â€” `sgp` (P15â€“35)

**Manual facts:** save as Excel; set `DATE` display to `yyyymmdd`; remove `SCHEDULED START TIME` and `SCHEDULED END TIME` if present. Source reconciliation selects DAYFORCEUC1 1000, 1025, 1050, 1075, 1300, 1320, 1330, 1340, 1350; paid=NORM and OT=OT.

**Implemented:** required DATE/NORM/OT, YMD parsing, real Excel dates with custom format, optional column drops and diagnostic code filters.

**Proposed correction:** certify actual date cell types and full header/column order before tightening source aliases. Preserve Excel date cells because the manual requests cell formatting; only change to eight-character text if the destination contract requires it. Keep all source records regardless of reconciliation codes. Apply the approved diagnostic period and independently verify filtered NORM/OT.

**Acceptance:** expected row count unchanged; exactly the two named optional columns disappear; all other approved columns/values preserved; DATE cell type/display matches approved example; selected/unselected department rows prove filters do not delete data. Extend `tests/test_profiles.py` and `tests/test_validation_matrix.py` only for missing real-layout cases. Runbook: [sgp](../../processes/sgp.md).

### 2. GBR WorkSegments â€” `gbr` (P75â€“125)

**Manual facts:** DATEIN/DATEOUT parse DMY then display `yyyymmdd`; convert REGHOURS/O1HOURS/O2HOURS from Excel time to decimal hours by multiplying underlying day durations by 24 and pasting values. The worksheet formula text contains a reversed-looking assignment at P111; do not copy that typo. Reconcile the same department set as SGP, excluding PTO/PARENTAL LEAVE/UNPAID TIME; paid=REGHOURS, OT=O1HOURS+O2HOURS.

**Implemented gap:** format/fraction heuristic can convert decimal `0.5` to 12 with a warning while permitting output.

**Proposed correction:** add an explicit approved hours-encoding contract in `gbr.yaml`, config validation and `transform.py`; distinguish Excel durations, clock text and already-decimal hours. Ambiguous units must block the affected run until resolved. Prevent double conversion of previously prepared files. Keep leave exclusions diagnostic. Preserve numeric precision before approved output rounding.

**Acceptance:** duration 0.5 dayâ†’12h, decimal 0.5hâ†’0.5h, 1.25 daysâ†’30h, clock values and zero are independently checked; unknown encoding blocks; DMY dates cannot swap month/day; combined OT reconciles. Extend duration cases in `tests/test_operations.py` and profile round trips. Runbook: [gbr](../../processes/gbr.md). TD-004.

### 3. CBG Starline Core2 â€” `cbg_core` (P169â€“175, P209â€“220)

**Manual facts:** copy data only, omitting decorative headings and totals, into `Core`; format Pay Rate numeric. Reconcile Hours/Units by Pay Code REG/OT under the department filter, then combine with SSI totals.

**Implemented gaps:** one-column header signature is weak; any-cell total-marker heuristic can remove legitimate data or retain footers; text Hours/Units are not parsed for metrics; department filter is absent.

**Proposed correction:** pin approved sheet/header signature and data boundaries using repaired evidence plus actual invoice layout. Classify summaries using designated label/key columns, never arbitrary cell content; audit skipped rows and their reasons. Validate Hours/Units numerically when used for reconciliation. Add only the approved department list. Preserve unrelated invoice tabs in the source and emit only the prepared Core table.

**Acceptance:** decorative titles, repeated headers, subtotals and trailing notes are handled explicitly; valid detail containing a total-like word is retained; every included Hours/Units cell participates or raises an issue. Numeric Pay Rate and selected REG/OT match independent totals. Runbook: [cbg_core](../../processes/cbg_core.md). TD-001/019/021.

### 4. CBG Starline SSI â€” `cbg_starline` (P181â€“220)

**Manual facts:** strip preamble and trailer; Text to Columns using semicolon; select YMD in wizard; display W/E Date as `m/d/yyyy`; delete Shift; make BRD numeric. Reconcile CHARGECODE 1000/1025/1050/1075/1300/1330, Straight Hrs and Overtime Hrs.

**Implemented gaps/assumptions:** MDY is configured despite YMD instruction; nonblank semicolon suffix fails safely; generic summary heuristics; hours used in metrics may remain text.

**Proposed correction:** resolve locale before changing configuration; validate real dates including ambiguous days. Establish exact detail boundaries and numeric reconciliation fields. Keep rejecting extra nonblank delimiter content unless an approved field-splitting contract preserves it. Produce independent Core/SSI component totals and an explicit combined CBG reconciliation artifact for the same week, without merging their different output schemas or introducing SAP calls.

**Acceptance:** approved ambiguous date examples parse correctly; extra delimiter data never disappears; no Shift; numeric BRD; all detail rows preserved; Core REG + SSI Straight and Core OT + SSI Overtime equal independently computed CBG totals. Runbook: [cbg_starline](../../processes/cbg_starline.md). TD-009/019/021.

### 5. CCB weekly summary â€” `ccb` (P258â€“278, P312â€“314)

**Manual facts:** use highlight to identify one 65.8â†’75.8 regular-hours correction; clear filters; make Reg/OT1.5/OT2/Total numeric; remove Notes. Reconciliation CCs: 3600161001/1002/1003/1004/1005 and 3600171000/1003/1004/1005; paid=Reg, OT=OT1.5+OT2.

**Implemented:** row-keyed overrides with expected old value; warning on 65.8; four conversions; Notes removal; provisional Dept/CC alias; total mismatch diagnostic.

**Proposed correction:** certify header identity and a unique source key for a separately reviewed override. Highlight/color is supporting evidence, not a reusable business key. If the key is missing/duplicate or old value differs, block correction. Apply to candidate output only; audit before/after value and provenance. Do not recalculate Total automatically or globally replace 65.8. Resolve mismatches with owner. Keep CC reconciliation separate from output retention.

**Acceptance:** approved single-row correction changes exactly one value; a second legitimate 65.8 remains unchanged; stale/duplicate key fails; numeric hours and absence of Notes match manual output. Runbook: [ccb](../../processes/ccb.md). TD-005.

### 6. Reno Temp Timecards â€” `reno` (P342â€“352; images rId41/rId42)

**Manual facts:** sum employees for each date and put daily totals into seven Sundayâ€“Saturday template rows. Screenshot template uses PAC/3601/Reno, NV/PDU/3600 and OT zero. Source screenshot has DMY dates, `8,75`, `5,5`, `term`, blank cells, employee totals and agency labels. Source and template date windows differ as recorded above.

**Proposed correction (P0):** make source locale and decimal separator explicit in mirrored `reno.yaml` and config validation. Preserve native numeric Excel cells; parse approved decimal-comma text locally (8,75â†’8.75), without changing thousands-separator behavior globally. Configure date-header scanning with approved DMY rather than hardcoded MDY. Recognize the two header rows and approved employee/detail range. Require date-based alignment to the requested Sundayâ€“Saturday window; obtain the missing Saturday from an approved source or block. `term`, blanks and nonworking days need explicit owner-approved handling with source-cell audit; never silently turn missing evidence into zero. Keep OT zero only under the approved template contract.

**Acceptance:** exact raw layout fixture, DMY ambiguous/unambiguous dates, comma decimals, status tokens, missing Saturday, extra prior Saturday, employee/agency totals and multiple sheets. Missing dates/status decisions block; totals cannot double-count summary rows. Only after evidence approval compare seven output dates and independently summed values. Screenshot Monday total 25 is illustrative, not a general constant. Runbook: [reno](../../processes/reno.md). TD-018/010.

### 7. JZ-BUS and JZ-DAT â€” `jz` (P397â€“410; images rId44/rId46)

**Manual facts:** extract invoice-hours context from HC in Labour In Plant Support; map Direct Hours (Starline)â†’BUSWAY, (Cables)â†’COP, (Fibra)â†’FIB, (Connectors)â†’RAC, (Servertech)â†’DAT. Sunday date represents requested week. Template shows BUS/3618 for BUSWAY and DAT/3614 for the other four, Santa Teresa/company 3600, separate Paid and OT fields.

**Implemented gap:** only normalized Category/Paid Hours/OT Hours staging works; this is not direct parsing of the received workbook.

**Proposed correction:** after owner supplies raw sheet/HC locations, week identity and Paid/OT derivation, add explicit raw extraction in `pipelines/jz.py` with an approved source mode. Keep staging clearly named/documented for compatibility. Verify unique category occurrence and preserve cell provenance into five mapped records. Reject missing/duplicate/unknown categories or mismatched week. No paid/OT inference from invoice hours and no hardcoded screenshot hours/dates.

**Acceptance:** real-shaped raw fixture produces exactly five approved rows and independently verified Paid/OT per category, plant and week. Negative fixtures for raw/staging confusion, shifted sections, missing HC and absent paid/OT rule block output. Runbook: [jz](../../processes/jz.md). TD-003/010.

### 8. Dayforce OData CCB â€” `dayforce_ccb` (P453â€“482)

**Manual facts:** refreshed monthly file; inspect minimum Pay_Date; remove Cost_center `3600172100 > Receiving Farmingdale`. For weekly reconciliation use DPC CCB, direct-labor codes 1000â€“1005; Normal by Reg and OT 1.5.

**Proposed correction:** require external refreshed-export evidence as an operator prerequisite, without implementing refresh. Record source date min/max and requested reconciliation week. Replace substring exclusion with approved exact code/label parsing; ambiguous code/label blocks. Audit excluded row origins/count/hours. Apply weekly predicates to diagnostics only; retain the rest of the monthly file. Minimum date is metadata here; it never triggers deletion outside the candidate file.

**Acceptance:** intended Receiving Farmingdale records alone are removed, similar longer codes retained, label mismatch blocks, monthly rows outside the week remain while weekly totals exclude them. Runbook: [dayforce_ccb](../../processes/dayforce_ccb.md). TD-007/016/020.

### 9. Dayforce OData non-CCB â€” `dayforce_non_ccb` (P472â€“482)

**Manual facts:** diagnostic locations DPC BUS/DPC PAC; cost centers `1000 > Direct Labour`, `1000 > Straights`, `1025 > Plugs`, `1050 > Fittings`, `1075 > Small Parts Assembly`, `1300 > Machine Shop`, `1330 > Powdercoat`; weekly Pay_Date; Normal for Reg/OT 1.5. Combine both Dayforce files for US reconciliation.

**Proposed correction:** share approved exact cost-center parsing and weekly metrics with CCB. Preserve every non-CCB monthly row; the manual specifies no non-CCB preparation deletion. Produce separate CCB/non-CCB and combined US totals with matching week and refresh evidence. Combined artifact is a proposed local audit output, not an existing feature.

**Acceptance:** lookalike codes/labels do not match; all monthly rows retained; Reg/OT and location/date filtering match independent weekly sums; combined totals equal component totals for the same period. Runbook: [dayforce_non_ccb](../../processes/dayforce_non_ccb.md). TD-007/016/020.

### 10. Taiwan production hours â€” `taiwan` (P494â€“535)

**Manual facts:** verify dates, null/negative anomalies and missing dates; file carries earned, paid and overtime hours. Later earned-hours and paid/OT SAP routes are distinct downstream processes, not additional parsing profiles.

**Implemented assumptions:** four required fields, MDY Date, UTF-8 BOM CSV and current date rendering; missing-date check covers only observed minimum through maximum, warns and does not fill.

**Proposed correction:** approve full source/target schema, locale, numeric precision and CSV conventions before altering these defaults. Compare against an explicit expected period/calendar to detect missing boundary days as well as interior gaps. Identify duplicate dates without deleting legitimate records until grain is approved. Missing dates remain issues, never synthesized zero-hour rows; decide warning/blocking policy with owner. One prepared source remains sufficient unless approved file contracts require separate exports.

**Acceptance:** exact CSV bytes/parsed fields match approved example; null/negative/invalid dates block; first/last/interior missing days and duplicates are reported under the approved calendar. Independent Earn/Paid/OT sums preserve source values. Runbook: [taiwan](../../processes/taiwan.md). TD-008/015.

### Cross-process procedure inventory

| Manual procedure | Handling in correction plan |
|---|---|
| Weekly one-week-lag receipt and Monday load; Sunday evening EST reminder (P2â€“5) | Record reporting period explicitly; do not infer current period from filename or run date. Scheduling and reminders are outside preparation scope. |
| Missing-file dummy hours, indicator and later replacement (P4â€“5) | Document external business procedure only. Missing input produces a blocked/missing-input result; no invented zero-hour file. |
| Source reconciliation and duplicate SQL after loads | Implement local source totals and approved source-key diagnostics only. Database duplicate checks and destination comparisons require external evidence and remain outside integration scope. |
| CCB and Dayforce selective SAP deletions; all DTP executions/ADSO activations | External operational steps; no implementation. |
| Taiwan earned versus paid/OT downstream paths and PBI check | Retain all three source measures and provide totals; no SAP/PBI integration. |

### Implementation order and edit boundaries

1. **P0:** first resolve Reno locale/date coverage and GBR hours units. Add explicit, structurally validated profile options to `config.py`; implement reusable parsing in `transform.py` and Reno-specific extraction in `reno.py`. Unresolved mappings block rather than guess.
2. **P1:** add audited table-boundary rules and complete numeric metrics for both CBG profiles in `tabular.py`; resolve SSI locale and missing Core filter evidence. Avoid weakening shared behavior for other profiles.
3. **P1:** add date-window predicates and approved exact cost-center parsing for Dayforce diagnostics/exclusion. Add component/combined CBG and US audits in a focused local orchestration/report layer after specifying artifact contracts; keep business extraction out of CLI and IO. Review report-contract changes before implementation.
4. **P1, evidence-dependent:** certify CCB override, implement direct raw JZ only with approved Paid/OT mapping, then certify Taiwan calendar and serialization. SGP can be certified independently with its smaller transformation surface.
5. Per profile, update `docs/processes/<profile>.md`, both YAML copies, meaningful fixture tests, this plan/debt, current state and execution log. Add ADR only if an accepted architecture boundary changes. Do not mark EP-0001 or this implementation complete from planning alone.

## Verification and acceptance

For each corrected workflow, run `validate` and `prepare` with explicit profile/sheet/period and an approved reference, then independently compare output with expected file. Reference headers alone are insufficient. Record SHA-256 before/after for source preservation; exact output names/order/types/date formats, row-level retention/removal ledger, decimal precision, independently computed paid/OT/earned totals, all issues and acceptance owner. Use separate output folders and inspect the current report before accepting a candidate.

Tests must prove the dangerous alternatives fail: ambiguous units/locales, missing dates, lookalike codes, accidental detail-row deletion, guessed corrections and raw JZ without a split. Add representative sanitized fixtures without personal information; use synthetic adversarial fixtures to cover failure cases. Existing tests that codify unsafe heuristics need deliberate updates when approved behavior changes, not blind preservation.

Required handoff checks: `uv run pytest -q`; `uv run python scripts/check_docs.py`; `uv run ruff check src tests`. Use a workspace-local `UV_CACHE_DIR` where needed. Record actual results and inherited lint debt. Implementation acceptance requires all ten workflows' real-source comparisons plus source-owner decisions; the plan-writing task itself is complete when this review is documented and linked.

## Evidence / execution log

- 2026-11-26: read actual DOCX XML and inspected embedded images rId41/rId42 (Reno), rId44/rId46 (JZ), rId27 (SSI); compared mirrored profile definitions, tabular/transform/Reno/JZ code and synthetic test cases. No source-file mutation or parsing implementation changes.
- Confirmed directly in code: comma removal, hardcoded Reno MDY, absence of date predicates in `_calculate_metrics`, broad summary detection and substring cost-center matching. These are code-review findings; no real raw workbook was supplied for end-to-end reproduction.
- Supplied DOCX has missing Core image targets; obtaining those is a source-evidence prerequisite, not a parser defect.
- 2026-11-26 implementation: final synthetic suite **535 passed in 24.28s**; full Ruff **PASS**; details and executable smoke evidence in execution log.
- Handoff command results are recorded in the [execution log](../../progress/EXECUTION_LOG.md).

## Surprises

- Broad summary-marker matching could discard valid detail containing the word Total in a descriptive field. Regression tests now retain that detail while auditing designated summary rows.
- Existing tests encoded unsafe fractional assumptions and omitted reconciliation periods. They now declare duration formatting/periods/evidence explicitly; no production samples were fabricated.
- Full legacy lint could be resolved within touched files using Annotated Typer options and small import/style cleanups; TD-017 now has passing evidence.

## Decisions

- 2026-11-26: keep this detailed correction backlog alongside EP-0001, which owns real-source certification. Do not rewrite completed historical plans.
- 2026-11-26: manual screenshots expose parsing hazards but do not establish reusable business semantics for `term`, blank days, invoice Paid/OT or contradictory date windows. Resolve these explicitly.
- 2026-11-26: ordinary reconciliation filters stay diagnostic; only explicit approved source-preparation exclusions remove candidate rows. All inputs remain immutable.

## Risks / rollback

Shared helper changes can alter unrelated profiles; scope numeric locale/unit options explicitly and cover existing profile round trips. Keep approved prior profiles/expected outputs for rollback. On any ambiguity/error preserve original input and existing target, write an actionable report and do not accept stale output. Confidential screenshots extracted for this review are temporary, not repository evidence assets.

## Next step

Obtain sanitized raw inputs and approved expected outputs under EP-0001, starting with Reno Saturday/status/blank semantics and GBR duration units; supply the missing Core filters and actual JZ Paid/OT cell mapping through reviewed custom profiles. The implementation deliberately blocks unresolved cases. Keep M1/M3/M4 open until real evidence and source-owner acceptance exist.
