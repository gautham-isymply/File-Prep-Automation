# Core beliefs / engineering invariants

1. **Business correctness beats automatic completion.** Ambiguous dates, labels, category mappings or hours should cause findings; never invent figures.
2. **Config is declarative; code owns parsing.** Reviewed YAML describes one source; only truly different shapes warrant a new processor module.
3. **One quality contract across inputs.** Every run attempts to produce a machine-readable issue report; severity and provenance are first-class.
4. **Preserve evidence.** Never overwrite inputs, discard unexpectedly filtered rows, or mutate manual examples without an exact approved override.
5. **Separate observed facts from proposed improvements.** Source manual is not an executable schema and may contradict itself.
6. **Retrieve progressively.** Agent first reads `AGENTS.md` → relevant process → exact code/config/tests. Avoid creating global prompt bloat.
7. **Work is test-backed and logged.** Verified progress is recorded in `docs/progress/`; complex work has a self-contained ExecPlan.
8. **Boundaries are more important than style.** Keep CLI, I/O, business pipelines, data models, and quality gate separable.

These are repo-local engineering rules, inspired by the harness-engineering method; they are not claims that OpenAI supplied or endorsed this implementation. See [harness references](../references/HARNESS_REFERENCES.md).
