# ADR-0006 — Supported workflow scope

**Status:** accepted  
**Date:** 2026-11-24  
**Source:** explicit user request to remove two workflows and all related details.

## Context

The supported inventory is reduced to eight profiles. The request includes source code, configuration, tests, examples, runbooks, and references in shared documents.

## Decision

Support `sgp`, `gbr`, `cbg_core`, `cbg_starline`, `ccb`, `jz`, `dayforce_ccb`, and `dayforce_non_ccb`. Use the generic tabular processor for seven profiles and the dedicated JZ processor for the remaining profile. Preserve shared CSV I/O and validation primitives.

This supersedes the original profile inventory in ADR-0002. Retired details in ADR-0002 and ADR-0004 are removed at the user's explicit request; their remaining decisions are retained. Historical test command evidence stays dated to the original runs. The retired debt ID is reserved and must not be reused.

## Consequences and evidence

Old manifests selecting a retired profile fail with the existing unknown-profile error. No source workbooks or retained business rules change. See [EP-0003](../exec-plans/completed/EP-0003-workflow-scope.md) and [execution evidence](../progress/EXECUTION_LOG.md).
