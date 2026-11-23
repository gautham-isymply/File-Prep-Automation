# ADR-0003 — Fail-safe output and reviewed corrections

**Status:** accepted  
**Date:** 2026-11-23 (recorded from inspected baseline)  
**Source:** existing v0.1.0 behavior and the uploaded manual; this is a recorded present-state decision, not evidence of prior historical approvals.

## Context

Unattended normalizing of ambiguous time fractions or replacing all CCB values of 65.8 risks wrong hours. Persisted prior output can be mistaken for new output.

## Decision

Source remains read-only. ERROR blocks; `--strict` blocks WARNING. Candidate emitted through temporary output path only after gate; manual corrections require unique row-key + expected old value. JSON report captures issues.

## Consequences and follow-up

Warnings in normal mode still permit candidate; a failed run leaves previous candidate intact. Operators must check status, not filename existence (TD-012).

See [design](../DESIGN.md), [debt](../exec-plans/tech-debt-tracker.md) and [current state](../progress/CURRENT_STATE.md).
