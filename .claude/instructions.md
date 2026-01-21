# Claude Code Instructions for p6-craps-py

## Project Overview

**p6-craps-py** is a Python-based craps (casino dice game) simulator focused on statistical analysis, betting strategy evaluation, and comprehensive simulation capabilities.

### Technology Stack
- **Python**: 3.14.2 (strict requirement)
- **Package Manager**: uv (never use pip directly)
- **Testing**: pytest, pytest-cov
- **Type Checking**: pyre-check, pyre-extensions
- **Formatters**: black (120 char line length), isort (black profile)
- **Linters**: flake8, pylint, pydocstyle
- **Security**: bandit, detect-secrets, pip-audit
- **CLI**: docopt for argument parsing
- **VCS**: git with comprehensive pre-commit hooks

### Project Structure
```
p6-craps-py/
├── bin/
│   └── script.py          # CLI entrypoint
├── p6_craps/              # Core package
│── tests/                 # Test suite (mirrors p6_craps structure)
├── pyproject.toml         # Project configuration
├── uv.lock                # Locked dependencies
└── .pre-commit-config.yaml # Quality gates
```

## Core Architecture

### Game Engine (p6_craps/engine.py)

The craps engine implements a minimal state machine:

**Key Classes:**

**Key Patterns:**
```python
# Immutable dataclass with slots
@dataclass(slots=True, frozen=True)
class Roll:
    d1: int
    d2: int

    @property
    def total(self) -> int:
        return self.d1 + self.d2

# Dependency injection for testability
class CrapsEngine:
    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng: random.Random = rng or random.Random()
```

### Craps Rules Implementation

**COME_OUT Phase:**
- 7 or 11: Pass Line wins
- 2, 3, or 12: Pass Line loses (craps)
- 4, 5, 6, 8, 9, 10: Establish point → POINT_ON

**POINT_ON Phase:**
- Roll the point: Pass Line wins → COME_OUT
- Roll a 7: Pass Line loses (seven out) → COME_OUT
- Any other: Continue rolling

## SDLC Requirements

### Code Quality Standards

**1. Mandatory Pre-Commit Hooks**

ALL commits must pass these checks (in order):
```bash
uv run pre-commit run --all-files
```

Hooks executed:
1. **black** - Code formatting (120 char line length)
2. **isort** - Import sorting (black profile)
3. **flake8** - Style guide enforcement
4. **pydocstyle** - Docstring validation
5. **pylint** - Static code analysis
6. **yamllint** - YAML file validation
7. **bandit** - Security vulnerability scanning
8. **detect-secrets** - Secret detection
9. **codespell** - Spell checking
10. **pytest** - Test suite execution (-v --no-cov)

**2. Code Style Requirements**

```python
"""Module-level docstring REQUIRED.

Explain the module's purpose and key components.
"""

from __future__ import annotations  # REQUIRED for type hints

import enum
import random
from dataclasses import dataclass
from typing import Optional, List

# Use enums for state/types
class Phase(enum.Enum):
    """Craps table phase."""
    COME_OUT = "come_out"
    POINT_ON = "point_on"

# Immutable dataclasses with slots
@dataclass(slots=True, frozen=True)
class Roll:
    """A single dice roll.

    Attributes:
        d1: First die value (1-6).
        d2: Second die value (1-6).
    """
    d1: int
    d2: int

    @property
    def total(self) -> int:
        """Return the sum of both dice."""
        return self.d1 + self.d2

# Type hints REQUIRED
def calculate_bet(bankroll: int, min_bet: int) -> int:
    """Calculate bet amount based on bankroll.

    Args:
        bankroll: Current player bankroll in dollars.
        min_bet: Minimum allowed bet amount.

    Returns:
        Bet amount in dollars.

    Raises:
        ValueError: If bankroll is negative or less than min_bet.
    """
    if bankroll < 0:
        raise ValueError("Bankroll cannot be negative")
    if bankroll < min_bet:
        raise ValueError(f"Bankroll {bankroll} below minimum bet {min_bet}")
    return min_bet
```

**3. Testing Requirements**

```python
"""Test module for craps engine."""

import pytest
import random
from p6_craps.engine import CrapsEngine, Roll, Phase, PassLineOutcome

class TestCrapsEngine:
    """Test suite for CrapsEngine."""

    def test_initial_state_is_come_out(self):
        """New engine should start in COME_OUT phase."""
        engine = CrapsEngine()
        assert engine.phase == Phase.COME_OUT
        assert engine.point is None
        assert engine.completed_points == 0

    def test_deterministic_behavior_with_seeded_rng(self):
        """Engine with same seed should produce same results."""
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        engine1 = CrapsEngine(rng=rng1)
        engine2 = CrapsEngine(rng=rng2)

        result1 = engine1.roll()
        result2 = engine2.roll()

        assert result1.roll.d1 == result2.roll.d1
        assert result1.roll.d2 == result2.roll.d2

    @pytest.mark.parametrize("d1,d2,expected", [
        (3, 4, 7),
        (5, 6, 11),
        (1, 1, 2),
    ])
    def test_roll_total_calculation(self, d1, d2, expected):
        """Roll.total should sum both dice correctly."""
        roll = Roll(d1=d1, d2=d2)
        assert roll.total == expected

    def test_come_out_seven_wins_pass_line(self):
        """Rolling 7 on come-out should win pass line."""
        engine = CrapsEngine()
        result = engine.apply_roll(Roll(d1=3, d2=4))  # 7

        assert result.pass_line_outcome == PassLineOutcome.WIN
        assert engine.phase == Phase.COME_OUT
        assert engine.point is None

    def test_point_established_on_valid_number(self):
        """Rolling 4-6, 8-10 on come-out establishes point."""
        engine = CrapsEngine()
        result = engine.apply_roll(Roll(d1=2, d2=2))  # 4

        assert result.phase_after == Phase.POINT_ON
        assert engine.point == 4
        assert result.pass_line_outcome == PassLineOutcome.NONE
```

**Test Execution:**
```bash
# Run tests with coverage
uv run pytest -v --cov=p6_craps --cov-report=html

# Run tests without coverage (faster, used in pre-commit)
PYTHONPATH=. uv run pytest -v --no-cov

# Run specific test file
uv run pytest tests/test_engine.py -v

# Run specific test
uv run pytest tests/test_engine.py::TestCrapsEngine::test_initial_state -v
```

### Development Workflow

**Setup:**
```bash
# Clone repository
git clone <repo-url>
cd p6-craps-py

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

**Development Cycle:**
```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes (TDD approach)
# - Write failing test
# - Implement feature
# - Make test pass
# - Refactor

# 3. Run full validation
uv run pre-commit run --all-files

# 4. Commit (pre-commit runs automatically)
git add .
git commit -m "feat: add new betting strategy"

# 5. Push and create PR
git push origin feature/your-feature
```

**Dependency Management:**
```bash
# Add production dependency
uv add <package>

# Add development dependency
uv add --dev <package>

# Update dependencies
uv lock --upgrade

# Security audit
uv run pip-audit
```

### Security Best Practices

**1. Input Validation:**
```python
def validate_bet_amount(amount: int, max_bet: int) -> None:
    """Validate bet amount with comprehensive checks."""
    if not isinstance(amount, int):
        raise TypeError(f"Bet must be int, got {type(amount)}")
    if amount <= 0:
        raise ValueError(f"Bet must be positive, got {amount}")
    if amount > max_bet:
        raise ValueError(f"Bet {amount} exceeds maximum {max_bet}")
```

**2. No Secrets in Code:**
```python
import os

# ✅ Load from environment
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable required")

# ❌ NEVER hardcode
# api_key = "sk_live_..."
```

**3. Safe Random Number Generation:**
```python
import random
import secrets

# For game mechanics (simulation)
rng = random.Random()
dice_roll = rng.randint(1, 6)

# For security (tokens, session IDs)
token = secrets.token_hex(16)
```

**4. Security Scanning:**
```bash
# Run security checks
uv run bandit -r p6_craps
uv run detect-secrets scan --all-files
uv run pip-audit
```

### Performance Considerations

**1. Use Efficient Data Structures:**
```python
# ✅ Use slots for memory efficiency
@dataclass(slots=True, frozen=True)
class Roll:
    d1: int
    d2: int

# ✅ Use sets for membership testing
POINT_NUMBERS = {4, 5, 6, 8, 9, 10}
if total in POINT_NUMBERS:
    ...

# ✅ Use generators for large datasets
def simulate_rolls(n: int):
    """Generate n rolls lazily."""
    for _ in range(n):
        yield roll_dice()
```

**2. Profile Before Optimizing:**
```bash
# CPU profiling
python -m cProfile -s cumulative bin/script.py

# Memory profiling
python -m memory_profiler bin/script.py
```

## Common Tasks

### Adding a New Module

1. Create module in `p6_craps/`
2. Add module-level docstring
3. Import in `p6_craps/__init__.py`
4. Create corresponding test file in `tests/`
5. Add to `__all__` if public API
6. Run pre-commit to validate

### Adding a New Feature

1. Write failing tests first (TDD)
2. Implement feature
3. Ensure all tests pass
4. Update documentation
5. Run full pre-commit validation
6. Create PR with clear description

### Modifying the CLI

1. Update `__doc__` string in `bin/script.py` (docopt usage)
2. Update `main()` function logic
3. Add tests for new CLI behavior
4. Update README.md if needed
5. Validate with pre-commit

### Adding a Dependency

1. Evaluate necessity (minimize dependencies)
2. Check license compatibility
3. Add with uv: `uv add <package>`
4. Run `uv run pip-audit` to check for CVEs
5. Update documentation if public API changed

## Code Review Checklist

Before requesting review, verify:

**Functionality:**
- [ ] Feature works as intended
- [ ] Edge cases handled
- [ ] Error messages are clear

**Testing:**
- [ ] Tests added/updated for changes
- [ ] All tests pass
- [ ] Coverage maintained or improved
- [ ] Tests are deterministic

**Code Quality:**
- [ ] Follows existing patterns
- [ ] Type hints present
- [ ] Docstrings added/updated
- [ ] No commented-out code
- [ ] No debug print statements

**Quality Gates:**
- [ ] `uv run pre-commit run --all-files` passes
- [ ] All 10 pre-commit hooks succeed
- [ ] No linting errors
- [ ] Security scans clean

**Documentation:**
- [ ] README updated if needed
- [ ] CHANGELOG updated (if applicable)
- [ ] Inline comments for non-obvious logic

**Git:**
- [ ] Conventional commit messages
- [ ] Logical commit structure
- [ ] Branch up to date with main

## Conventional Commits

Use these commit prefixes:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `style:` Formatting changes
- `perf:` Performance improvements
- `chore:` Maintenance tasks
- `ci:` CI/CD changes

Examples:
```bash
git commit -m "feat: add Martingale betting strategy"
git commit -m "fix: prevent negative bankroll in Player class"
git commit -m "test: add edge case tests for seven-out scenario"
git commit -m "docs: update README with simulation usage"
```

## Anti-Patterns to Avoid

**DON'T:**
- ❌ Use pip (use uv instead)
- ❌ Skip pre-commit hooks with `--no-verify`
- ❌ Commit without running tests
- ❌ Leave commented-out code
- ❌ Use print() for logging (use logging module)
- ❌ Hardcode configuration values
- ❌ Catch exceptions without handling them
- ❌ Modify production code without tests
- ❌ Copy-paste code (refactor instead)
- ❌ Ignore type hints
- ❌ Use mutable default arguments

**DO:**
- ✅ Use uv for all package management
- ✅ Run pre-commit before pushing
- ✅ Write tests first (TDD)
- ✅ Use type hints everywhere
- ✅ Use `from __future__ import annotations`
- ✅ Use dataclasses with slots and frozen
- ✅ Inject dependencies for testability
- ✅ Keep functions small and focused
- ✅ Use meaningful variable names
- ✅ Document non-obvious decisions

## Quick Reference Commands

```bash
# Setup
uv sync                                      # Install dependencies
uv run pre-commit install                    # Install pre-commit hooks

# Development
PYTHONPATH=. uv run pytest -v --no-cov      # Run tests (fast)
uv run pytest -v --cov=p6_craps             # Run tests with coverage
uv run pre-commit run --all-files           # Run all quality gates
uv run python bin/script.py --debug         # Run CLI in debug mode

# Code Quality
uv run black .                               # Format code
uv run isort .                               # Sort imports
uv run flake8                                # Lint code
uv run pylint p6_craps bin                  # Static analysis
uv run pydocstyle p6_craps                  # Check docstrings
uv run pyre check                            # Type checking

# Security
uv run bandit -r p6_craps                   # Security scan
uv run detect-secrets scan --all-files      # Secret detection
uv run pip-audit                             # Dependency audit

# Dependencies
uv add <package>                             # Add dependency
uv add --dev <package>                       # Add dev dependency
uv lock --upgrade                            # Update dependencies
uv tree                                      # Show dependency tree

# Git
git add .
git commit -m "type: description"
git push
```

## Claude Code Specific Tips

**When you assist with this project:**

1. **Always read existing code first** before suggesting changes
2. **Follow the established patterns** (dataclasses, enums, dependency injection)
3. **Write tests alongside implementation** (prefer TDD)
4. **Run validation commands** before considering a change complete
5. **Suggest minimal, focused changes** (one feature at a time)
6. **Explain trade-offs** when multiple approaches exist
7. **Update documentation** when changing behavior
8. **Consider performance** but don't prematurely optimize
9. **Think about security** especially input validation
10. **Maintain backwards compatibility** unless explicitly breaking

**Prefer incremental changes:**
- Small, focused PRs over large rewrites
- Additive changes over deletions
- Clear migration paths for breaking changes

**Communication:**
- Explain WHY, not just WHAT
- Show before/after examples
- Provide verification commands
- Flag potential issues or side effects

## Project-Specific Domain Knowledge

**Craps Terminology:**
- **Come-out roll**: First roll of a new betting round
- **Point**: Target number established on come-out (4, 5, 6, 8, 9, 10)
- **Pass Line**: Main bet that wins on 7/11 during come-out
- **Seven out**: Rolling 7 during point-on (loses pass line)
- **Natural**: Rolling 7 or 11 (immediate win on come-out)
- **Craps**: Rolling 2, 3, or 12 (immediate loss on come-out)

**Betting Strategies (to be implemented):**
- Flat betting: Same amount each bet
- Martingale: Double after loss
- Paroli: Double after win
- D'Alembert: Increment/decrement by fixed amount
- Fibonacci: Follow Fibonacci sequence

## Summary

This is a well-structured Python project with strict quality gates. Always:
1. **Follow existing patterns** (immutable dataclasses, dependency injection, enums)
2. **Write comprehensive tests** (TDD approach preferred)
3. **Pass all pre-commit hooks** before considering work done
4. **Maintain security** (input validation, no secrets, scanning)
5. **Keep code readable** (docstrings, type hints, clear names)

The goal: **Maintainable, tested, secure, performant code**.

## Resources

- **Project Repo**: Check README.md for latest information
- **Pre-commit Config**: `.pre-commit-config.yaml` for quality gates
- **Python Docs**: https://docs.python.org/3.14/
- **uv Docs**: https://docs.astral.sh/uv/
- **pytest**: https://docs.pytest.org/
- **OWASP**: https://owasp.org/www-project-python-security/

---

**Last Updated**: 2026-01-20
**Python Version**: 3.14.2
**Project Status**: Active Development
