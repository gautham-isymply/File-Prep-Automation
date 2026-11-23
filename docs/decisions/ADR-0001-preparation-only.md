# ADR-0001 — Preparation-only boundary

**Status:** accepted  
**Date:** 2026-11-23 (recorded from inspected baseline)  
**Source:** existing v0.1.0 behavior and the uploaded manual; this is a recorded present-state decision, not evidence of prior historical approvals.

## Context

The user explicitly scoped work to preparing factory files and auditing inconsistencies, not SAP BW. The 39-page manual also contains load DTPs, ADSOs, selective deletions and PBI checks.

## Decision

CLI operates on source files only; no BW network integration, mail reminders, SAP credentials, ADSO deletes, DTP runs or PBI validation. Extract only source-side rules and advisory reconciliation metrics.

## Consequences and follow-up

Cannot attest that data was accepted by BW. Business loading and post-load duplicate SQL stay in source evidence as context, not implementation.

See [design](../DESIGN.md), [debt](../exec-plans/tech-debt-tracker.md) and [current state](../progress/CURRENT_STATE.md).
