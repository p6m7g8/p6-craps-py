# Gemini Instructions for p6-craps-py

Use this file as the authoritative Gemini guidance for this repository. For full context and domain rules,
read `AI_CONTEXT.md` first.

## Project Context

- **Purpose**: Craps simulator for statistical analysis and strategy evaluation.
- **Python**: 3.14.2 (strict requirement).
- **Package manager**: `uv` only.
- **CLI**: `bin/script.py` with `docopt`.
- **Tests**: `pytest` with coverage requirements (80% minimum, 90% target).

## SDLC Requirements

Follow this flow for any change:
1. **Read**: `AI_CONTEXT.md` and related modules.
2. **Design**: Explain intended behavior and test impact.
3. **Implement**: Use established patterns (immutable dataclasses, enums, DI, pure functions).
4. **Test**: Add or update deterministic tests for new or changed behavior.
5. **Verify**: Run required quality gates.
6. **Document**: Note commands used and remaining verification steps.

## Quality Gates

Always pass the full pre-commit suite:
```bash
uv run pre-commit run --all-files
```

This includes `black`, `isort`, `flake8`, `pydocstyle`, `pylint`, `yamllint`, `bandit`, `detect-secrets`,
`codespell`, and `pytest -v --no-cov`.

## Testing Standards

- All public APIs must have tests.
- Cover error paths, boundaries, and edge cases.
- Prefer `pytest` parametrization and fixtures.
- Ensure deterministic behavior with seeded `random.Random` when needed.

Commands:
```bash
PYTHONPATH=. uv run pytest -v --no-cov
uv run pytest -v --cov=p6_craps
```

## Coding Conventions

- Add `from __future__ import annotations` to modules.
- Use `@dataclass(slots=True, frozen=True)` for immutable data models.
- Use enums for state or constant sets.
- Inject dependencies (e.g., RNG) instead of global state.
- Validate all external inputs and raise clear exceptions.
- Avoid `eval`, `exec`, or unsafe deserialization.
- Use logging, not `print`.
- Keep diffs minimal and focused.

## CLI Updates

- Update `Usage:` and `Options:` in `bin/script.py` docstring when changing flags.
- Keep `main()` behavior aligned with the docstring.
- Add tests for new CLI behavior.

## Security

- No secrets in code or tests.
- Use env vars for configuration.
- Run security scans when modifying core logic or IO:
  - `uv run bandit -r p6_craps`
  - `uv run detect-secrets scan`
  - `uv run pip-audit`

## Commit/PR Guidance

- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `style:`, `perf:`, `chore:`.
- Explain **why** and **how** in PRs.
- Include exact verification commands.
