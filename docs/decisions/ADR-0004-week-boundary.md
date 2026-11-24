# ADR-0004 — Weekly boundary Sunday–Saturday

**Status:** accepted with verification needed  
**Date:** 2026-11-23 (recorded from inspected baseline)  
**Source:** existing v0.1.0 behavior and the uploaded manual; this is a recorded present-state decision, not evidence of prior historical approvals.

## Context

Manual introduction says each week starts Sunday and ends Saturday; some later SQL examples show inconsistent dates. The JZ weekly template uses Sunday start.

## Decision

Adopt Saturday `--week-ending`, derive Sunday = ending minus six days. Mark contradictory manual examples as unresolved and avoid BW-range assumptions.

## Consequences and follow-up

Business signoff still required across workflows (TD-010). Never modify source week dates to force example SQL compatibility.

See [design](../DESIGN.md), [debt](../exec-plans/tech-debt-tracker.md) and [current state](../progress/CURRENT_STATE.md).

2026-11-24: retired workflow details removed at user request; see [ADR-0006](ADR-0006-supported-scope.md). Remaining decision semantics are retained.
