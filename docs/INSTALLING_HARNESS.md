# Installing the harness documentation

Two archives can be produced from this repo snapshot:

- **Integrated project:** unpacks as `factoryprep/` with existing v0.1.0 source code, profiles, tests, examples and the full documentation.
- **Docs-only overlay:** unpacks as `factoryprep/` with `AGENTS.md`, `ARCHITECTURE.md`, `docs/`, and `scripts/check_docs.py`; copy these into an existing FactoryPrep v0.1.0 checkout. Existing code/config/test files remain untouched.

Start with `AGENTS.md`, then `docs/index.md` and `docs/progress/CURRENT_STATE.md`. The package does not contain the original factory manual or raw production data.

## Check after unzipping

```bash
uv sync --extra dev
uv run python scripts/check_docs.py
uv run pytest -q
```

`uv.lock` was not present in the initial supplied project. Generating one requires access to package registry and should be committed when available. If working offline with existing local dependencies, `PYTHONPATH=src python -m pytest -q` and `python scripts/check_docs.py` can be used.

The docs checker compares the two local profile directories; when using the docs-only overlay on an unrelated project, expect a failure until that repo has the eight supported profiles in both locations. It does not certify business accuracy.
