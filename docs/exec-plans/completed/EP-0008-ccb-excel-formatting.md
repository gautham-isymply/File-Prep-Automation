# EP-0008 — CCB Excel formatting

**State:** completed  
**Updated:** 2026-11-26  
**Owner:** unassigned

## Objective

CCB output has Number-formatted hours and Row Labels fill colours available for colour filtering.

## Baseline and scope

User reported General formatting and missing colour filters. Presentation only; no hours, correction, row-rule or diagnostic changes. No BW integration.

## Current repository facts

Writer previously set date formats only; copied no fills or filters. Local metadata inspection found 11 static solid RGB Row Labels fills and no conditional formatting. Source filter ended at row 819 despite 2677 source rows. Original output had no fills or AutoFilter.

## Unknowns and human decisions

Manual does not specify decimal precision; use two-decimal Number display (0.00) without rounding stored values. Conditional-formatting rules, font colours and general workbook styling are not copied. Destination certification remains under EP-0001.

## Milestones / Progress

- [x] M1 — inspect writer/local workbook metadata without logging employee values.
- [x] M2 — profile-controlled formats, fill columns and AutoFilter; mirrored YAMLs and regression cases.
- [x] M3 — full checks, local regeneration/value comparison, source hash and documentation.

## Step-by-step design

CellValue carries source fills. prepare_tabular maps configured fills using canonical headers and retained source-row origins. Prepared carries output formats, fills and AutoFilter flag. Writer applies explicit formats and an unfiltered full-table AutoFilter. Config validates these options. Both CCB profiles select four 0.00 formats and Row Labels fills; other profiles keep existing defaults.

## Verification and acceptance

Run uv run pytest -q, uv run python scripts/check_docs.py and uv run ruff check src tests. Synthetic tests reload XLSX to check numeric types, unrounded values, date format, RGB fills after summary/blank removal, alias/dropped-column mapping, full filter range and source hash. Regenerate user's local output; compare all values to previous output and source digest before/after. Do not commit raw files.

## Evidence / execution log

2026-11-26: initial targeted run exposed None fills on empty read-only cells; guarded it. Targeted suite then passed, 5 tests. Full suite: 540 passed in 21.27s; Ruff passed. User local prepare command exited 0; all 2676 output data rows retained exact previous values, source SHA256 unchanged, four hours columns are 0.00, 11 source RGB fills preserved and AutoFilter is A1:H2677. Direct StyleProxy list comparison initially failed in the verification script; comparing copied fill objects confirmed equality. Excel UI was not exercised.

## Decisions

2026-11-26 — Keep static fill cues; clear active criteria as manual instructs. Enable filtering over full output instead of copying source's stale partial range. Display precision does not change stored hours.

## Risks / rollback

Saved XLSX metadata can be checked; Excel UI acceptance remains an operator check. Revert CCB output options for old presentation. Source remains read-only and output is replaced only after a successful gate.

## Next step

Operator can reopen the regenerated workbook to confirm Excel colour-filter UI. No required implementation work remains.
