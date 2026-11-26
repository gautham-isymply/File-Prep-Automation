# ADR-0006 — explicit source contracts and local combined audits

**Status:** accepted for implementation; real source certification remains open  
**Date:** 2026-11-26

## Context

The manual review exposed ambiguous durations/locales, broad row/code matching and monthly totals compared with weekly examples. Missing source evidence cannot justify invented hours or SAP integrations. ADR-0005's raw-JZ prohibition remains applicable to unverified original HC layouts.

## Decision

Add validated profile contracts for locale/units/table boundaries and optional approved raw-JZ cell extraction. The bundled JZ profile remains staging; raw extraction requires distinct Paid/OT cells, exact labels and source-week verification. This capability does not supply or certify the missing HC mapping.

Keep parsing in existing pipelines/helpers. Add `reconcile.py` as a local report-combination module invoked by a thin CLI command. It combines only successful, scoped, matching-week component reports with confirmed filters; US reports also require source-bound external refresh attestations. Combined output is a separate source audit, never a destination load or certification.

## Consequences

Ambiguous fractions, SSI slash dates and Reno blank/status cells block until their contracts are explicit. Dayforce preparation requires an owner attestation tied to source bytes. Ordinary preparation can retain monthly records while weekly diagnostics use only the requested period. Core's missing department filter keeps combined CBG acceptance blocked by default. Existing scripts must pass --week-ending for weekly metrics and source evidence for Dayforce.

## Evidence

[EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md), [manual correction tests](../../tests/test_manual_corrections.py), [report contract](../quality/REPORT_CONTRACT.md). All test fixtures are synthetic; actual source/destination approval remains EP-0001.
