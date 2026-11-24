# ADR-0002 — Profile/pipeline separation

**Status:** accepted  
**Date:** 2026-11-23 (recorded from inspected baseline)  
**Source:** existing v0.1.0 behavior and the uploaded manual; this is a recorded present-state decision, not evidence of prior historical approvals.

## Context

Supported source shapes share dates/columns while JZ maps business categories. Forcing all into declarative transforms would obscure business intent.

## Decision

Use YAML per profile, generic tabular processor and a dedicated JZ processor. Keep common input/output/quality orchestration in engine.

## Consequences and follow-up

Easy to add similar sources; uncommon shapes require code and tests. Current YAML validation remains shallow (TD-002).

See [design](../DESIGN.md), [debt](../exec-plans/tech-debt-tracker.md) and [current state](../progress/CURRENT_STATE.md).

2026-11-24: retired workflow details removed at user request; see [ADR-0006](ADR-0006-supported-scope.md). Remaining decision semantics are retained.
