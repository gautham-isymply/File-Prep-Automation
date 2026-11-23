# Harness-engineering method references

This repository's structure is **inspired by**, not copied from or endorsed by, published OpenAI engineering guidance. Content here is applied to a local Python CLI project.

## Primary sources

1. [OpenAI — Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026): short `AGENTS.md` as map; repository-local `docs/` knowledge base; active/completed ExecPlans and tech debt; progressive disclosure; mechanical architecture/document freshness checks.
2. [OpenAI Cookbook — Using PLANS.md for multi-hour problem solving](https://github.com/openai/openai-cookbook/blob/main/articles/codex_exec_plans.md): self-contained living plans, exact acceptance criteria, progress and decision logs.
3. [OpenAI Cookbook — Iterating Development Workflows with Codex](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex): initial repository instructions and durable build/evidence logs as workflow tools.

## Local implementation of ideas

- `AGENTS.md` maps to [doc router](../index.md) rather than duplicating instructions.
- `docs/exec-plans/` and [debt](../exec-plans/tech-debt-tracker.md) hold restartable work state.
- `docs/processes/` provides each business workflow's precise source/target/config surface.
- `scripts/check_docs.py` mechanically checks references, profile docs and YAML mirrors. It is a starting guardrail, not full enforcement.
- `docs/progress/` stores evidence so another agent can resume without chat memory.

Read primary sources when changing harness policy, but agents can execute this repo using only its own checked-in conventions.
