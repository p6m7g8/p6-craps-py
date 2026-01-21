# Copilot instructions for this repository

This repository is a **uv-based Python CLI template** that is evolving into a craps simulator.

- Main entrypoint: `bin/script.py`
- CLI uses `docopt` to parse arguments.
- Current flags: `--debug` and `--verbose`
- Core package: `p6_craps/` (engine, players, strategy, etc.)
- Tests live under `tests/` and use `pytest`.

## Environment and setup

- Use **Python 3.14.0**.
- Use `uv` for dependency management and execution.

### Standard commands

- Install dependencies: `uv sync`
- Run full pre-commit (format, lint, tests):  
  `uv run pre-commit run --all-files`
- Run tests directly (if needed):  
  `PYTHONPATH=. uv run pytest -v --no-cov`
- Run the CLI (normal):  
  `uv run python bin/script.py`
- Run the CLI (debug/verbose):  
  `uv run python bin/script.py --debug`  
  `uv run python bin/script.py --verbose`

When you propose changes that require running code or tests, prefer these commands.

## Project structure expectations

- Keep the main CLI entrypoint at `bin/script.py`.
- Put reusable logic in the `p6_craps` package instead of expanding `bin/script.py`.
- Keep tests in `tests/` and mirror the structure of the code under test.

## Coding style, linting, and docstrings

Code must pass:

- `black`, `isort`
- `flake8`
- `pylint`
- `pydocstyle`
- `yamllint` (for YAML files)
- `pytest`

Docstrings are **required** for:

- Public **modules** (top of each `.py` file)
- Public **classes**
- Public **functions** and **methods**

Docstrings should:

- Be concise but descriptive.
- Explain what the function/class/module does and important arguments/returns.
- Be consistent with the existing style in the repo.

Use the full pre-commit pipeline locally:

```bash
uv run pre-commit run --all-files
```

and ensure it passes before assuming a change is acceptable.

## How to modify the CLI

- The `__doc__` string in `bin/script.py` defines the CLI usage for `docopt`.
- When adding or changing CLI options:
  - Update the `Usage:` and `Options:` sections in `__doc__`.
  - Keep the behavior in `main()` in sync with the docstring.
  - Add or update tests that cover new options or behaviors.
  - Ensure any new functions/classes/modules have docstrings that satisfy pydocstyle/pylint.

## Tests and quality

- For any non-trivial change, add or update tests in `tests/`.
- Keep tests:
  - Fast
  - Deterministic
  - Focused on behavior, not implementation details
- Use `pytest` idioms (fixtures, parametrization) instead of inventing custom test harnesses.

## What **not** to do by default

- Do **not** introduce new dependencies unless necessary. If you must, favor well-known, maintained libraries.
- Do **not** change existing public CLI flags without updating docs and tests.
- Do **not** reformat the entire repo just to satisfy a style preference; keep diffs minimal and focused.

## Pull request behavior

When drafting PRs or suggested changes:

- Use clear, concise language.
- Explain **why** a change is needed, not just **what** was changed.
- Include the exact commands to verify the changes (e.g. `uv run pre-commit run --all-files`).
- If you touch tests, mention how coverage or behavior improved.
