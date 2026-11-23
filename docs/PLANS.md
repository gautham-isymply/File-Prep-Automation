# ExecPlan protocol for FactoryPrep

Use a self-contained plan when a change alters several modules, adds a new processing strategy, changes numeric semantics or requires real-world fixture certification. A small documentation typo or isolated test fix does not need an ExecPlan.

## Create / execute / close

1. Copy the [plan template](exec-plans/TEMPLATE.md) to `exec-plans/active/EP-NNNN-short-name.md`. Give it a stable ID and exact acceptance checks. Begin with *what the operator can now do*, not proposed classes.
2. On every milestone, update `Progress` checkboxes plus dated `Evidence` (commands, test results, sample names and discrepancies), `Decisions`, `Surprises`, and `Next step`. Avoid relying on earlier chat history.
3. Implement in small testable steps. All plan assumptions must be reproducible from repo files or explicitly marked as unresolved external inputs.
4. If discovering unplanned risk, add a `TD-...` item in debt tracker and reference it from the ExecPlan. Changing an established architectural boundary requires an ADR.
5. Mark complete and move to `exec-plans/completed/` **only** when each acceptance condition is evidenced, documentation/process contracts are updated, and current state/log are refreshed. Otherwise keep the plan active/blocked.

## Required plan sections

`Objective`, `Baseline and scope`, `Current repository facts`, `Unknowns and human decisions`, `Milestones / Progress`, `Step-by-step design`, `Verification and acceptance`, `Evidence / execution log`, `Decisions`, `Risks / rollback`, `Next step`.

Do not make speculative acceptance claims. Keep the plan internally navigable and restartable by an agent with only that plan and the checked-in repository; important details should be stated inline, with links to authoritative code/config. Long narratives belong in the plan, not `AGENTS.md`.

This is a local adaptation of OpenAI's published ExecPlan convention. See [harness references](references/HARNESS_REFERENCES.md).
