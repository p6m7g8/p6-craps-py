# Codex Agent Instructions for p6-craps-py

This repository uses strict SDLC and quality gates. Read `AI_CONTEXT.md` first for authoritative project
context, architecture patterns, and domain rules.

## Project Snapshot

- **Domain**: Craps (casino dice game) simulator with statistical analysis and betting strategies.
- **Python**: 3.14.2 (exact version required).
- **Package manager**: `uv` (never use `pip` directly).
- **CLI**: `bin/script.py` using `docopt`.
- **Tests**: `pytest` with coverage expectations (80% minimum, 90% target).

## SDLC Flow (Required)

1. **Understand**: Read `AI_CONTEXT.md` and relevant modules before changing behavior.
2. **Plan**: Describe intended changes, risks, and test impact.
3. **Implement**: Follow code patterns (immutable dataclasses, enums, DI, pure functions).
4. **Validate**: Add/adjust tests for every public API or behavior change.
5. **Quality Gates**: Ensure all pre-commit hooks pass.
6. **Report**: State commands run and remaining steps for verification.

## Quality Gates (All Must Pass Before Commit)

Run:
```bash
uv run pre-commit run --all-files
```

Hooks include:
1. `black` (120 char line length)
2. `isort` (black profile)
3. `flake8`
4. `pydocstyle`
5. `pylint`
6. `yamllint`
7. `bandit`
8. `detect-secrets`
9. `codespell`
10. `pytest -v --no-cov`

## Testing Standards

- Add tests for all public APIs and edge cases.
- Cover error paths and boundary conditions.
- Use deterministic tests (seeded `random.Random` when applicable).
- Keep tests fast and behavior-focused.

Common commands:
```bash
PYTHONPATH=. uv run pytest -v --no-cov
uv run pytest -v --cov=p6_craps
```

## Coding Standards

- **Type hints** on all functions and methods.
- **Docstrings** required for modules, public classes, and public functions (Google style).
- Use `from __future__ import annotations` at top of modules.
- Prefer **immutable dataclasses** with `slots=True, frozen=True`.
- Use **enums** for state/constants.
- Inject RNGs and other dependencies (no global state).
- Validate inputs; raise clear `ValueError`/`TypeError`.
- Never use `eval`, `exec`, or unsafe deserialization on untrusted input.
- Use logging instead of `print`.

## CLI Changes (docopt)

- Update `__doc__` in `bin/script.py` when adding CLI flags.
- Keep `Usage:` and `Options:` in sync with `main()` behavior.
- Add tests for new flags/paths.

## Security and Compliance

- No secrets in code or tests.
- Use env vars for configuration.
- Run security checks when touching sensitive areas:
  - `uv run bandit -r p6_craps`
  - `uv run detect-secrets scan`
  - `uv run pip-audit`

## Commits and PRs

- Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `style:`, `perf:`, `chore:`.
- Explain **why** and **how** in PR descriptions.
- Include exact verification commands.
