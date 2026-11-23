# ADR-0005 — Do not guess JZ raw HC extraction

**Status:** accepted  
**Date:** 2026-11-23 (recorded from inspected baseline)  
**Source:** existing v0.1.0 behavior and the uploaded manual; this is a recorded present-state decision, not evidence of prior historical approvals.

## Context

Manual asks to use HC invoice hours and copy five Direct Hours groups into paid/OT template but does not define raw workbook cells or reliable paid-vs-OT split.

## Decision

Current `jz` processor requires pre-normalized source with `Category`, `Paid Hours`, `OT Hours`; maps five categories to fixed target profit centers and flags `PROVISIONAL_SOURCE_SCHEMA`.

## Consequences and follow-up

Direct preparation from raw user workbook remains incomplete; actual source and business-approved mapping are prerequisites (TD-003).

See [design](../DESIGN.md), [debt](../exec-plans/tech-debt-tracker.md) and [current state](../progress/CURRENT_STATE.md).
