# AI Assistant Context for p6-craps-py

> **Purpose**: This document provides essential context for any AI coding assistant working with the p6-craps-py project. Read this first before making changes.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [SDLC Standards](#sdlc-standards)
5. [Code Patterns](#code-patterns)
6. [Quality Gates](#quality-gates)
7. [Domain Knowledge](#domain-knowledge)
8. [Common Tasks](#common-tasks)
9. [Quick Reference](#quick-reference)

## Project Overview

**p6-craps-py** is a Python-based craps (casino dice game) simulator with focus on:
- Statistical analysis of game outcomes
- Betting strategy evaluation
- Monte Carlo simulations
- Performance analysis

**Project Goals:**
- Accurate craps rules implementation
- Comprehensive testing (90%+ coverage)
- High code quality and maintainability
- Security best practices
- Performance optimization for large simulations

**License**: Apache 2.0
**Author**: Philip M. Gollucci <pgollucci@p6m7g8.com>
**Python Version**: 3.14.2 (strict requirement)

## Technology Stack

### Core Dependencies
- **Python**: 3.14.2 (exact version required)
- **Package Manager**: uv (NOT pip)
- **CLI Framework**: docopt
- **Testing**: pytest, pytest-cov
- **Type Checking**: pyre-check, pyre-extensions

### Development Tools
- **Formatters**: black (120 char), isort (black profile)
- **Linters**: flake8, pylint, pydocstyle
- **Security**: bandit, detect-secrets, pip-audit
- **Quality**: yamllint, codespell, pre-commit

### Development Workflow
```bash
# Package management
uv sync                  # Install dependencies
uv add <pkg>             # Add dependency
uv add --dev <pkg>       # Add dev dependency
uv lock --upgrade        # Update dependencies

# Testing
PYTHONPATH=. uv run pytest -v --no-cov     # Fast tests
uv run pytest -v --cov=p6_craps            # With coverage

# Quality gates
uv run pre-commit run --all-files          # Run all hooks

# CLI execution
uv run python bin/script.py --debug        # Debug mode
```

## Architecture

### Module Organization

```
p6_craps/
├── __init__.py         # Package exports
tests/
```

### Key Design Patterns

**1. Immutable Dataclasses with Slots**
```python
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Roll:
    """Immutable dice roll."""
    d1: int
    d2: int

    @property
    def total(self) -> int:
        return self.d1 + self.d2
```

**Benefits:**
- Memory efficiency (35-40% reduction with slots)
- Immutability prevents bugs
- Thread-safe
- Hashable (can use in sets/dict keys)

**2. Enums for State/Type Constants**
```python
import enum

class Phase(enum.Enum):
    """Craps table phase."""
    COME_OUT = "come_out"
    POINT_ON = "point_on"
```

**Benefits:**
- Type safety
- IDE autocomplete
- Clear intent
- Prevents magic strings

**3. Dependency Injection**
```python
import random
from typing import Optional

class CrapsEngine:
    """Core craps game engine."""

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        """Initialize engine with optional RNG for deterministic testing."""
        self._rng: random.Random = rng or random.Random()
```

**Benefits:**
- Testability (inject seeded RNG)
- Flexibility
- No global state
- Reproducible tests

**4. Pure Functions**
```python
def calculate_payout(bet: Bet, outcome: PassLineOutcome) -> int:
    """Pure function: same inputs always produce same output."""
    if outcome == PassLineOutcome.WIN:
        return bet.total_wagered * 2
    return 0
```

**Benefits:**
- Easy to test
- Easy to reason about
- No side effects
- Parallelizable

## SDLC Standards

### Pre-Commit Quality Gates

**ALL commits must pass these 10 checks:**

1. **black** - Code formatting (120 char line length)
2. **isort** - Import sorting (black profile)
3. **flake8** - Style guide enforcement (PEP 8)
4. **pydocstyle** - Docstring validation
5. **pylint** - Static code analysis
6. **yamllint** - YAML file validation
7. **bandit** - Security vulnerability scanning
8. **detect-secrets** - Secret detection
9. **codespell** - Spell checking
10. **pytest** - Test suite execution (-v --no-cov)

**Run before committing:**
```bash
uv run pre-commit run --all-files
```

### Testing Standards

**Requirements:**
- Minimum 80% code coverage (target 90%+)
- All public APIs must have tests
- All error paths must be tested
- Edge cases and boundary conditions covered
- Deterministic tests (use seeded Random instances)

**Test Structure:**
```python
"""Tests for module_name."""

import pytest
import random
from p6_craps.module import Class


class TestClass:
    """Test suite for Class."""

    def test_behavior_under_condition(self):
        """Should do X when Y happens."""
        # Arrange
        obj = Class(param=value)

        # Act
        result = obj.method()

        # Assert
        assert result == expected

    @pytest.mark.parametrize("input,expected", [
        (1, 10),
        (2, 20),
        (3, 30),
    ])
    def test_multiple_cases(self, input, expected):
        """Test multiple scenarios."""
        assert calculate(input) == expected
```

### Security Standards

**Input Validation:**
```python
def validate_input(value: int, min_val: int, max_val: int) -> None:
    """Validate input with comprehensive checks."""
    if not isinstance(value, int):
        raise TypeError(f"Expected int, got {type(value)}")
    if value < min_val:
        raise ValueError(f"Value {value} below minimum {min_val}")
    if value > max_val:
        raise ValueError(f"Value {value} exceeds maximum {max_val}")
```

**Security Checks:**
```bash
uv run bandit -r p6_craps              # Security scan
uv run detect-secrets scan             # Secret detection
uv run pip-audit                       # Dependency CVEs
```

**Rules:**
- NEVER hardcode secrets
- ALWAYS validate inputs
- NO use of eval(), exec(), pickle on untrusted data
- Use environment variables for configuration
- Follow principle of least privilege

## Code Patterns

### Complete Example: Adding a New Feature

**1. Module File (p6_craps/strategy.py)**
```python
"""Betting strategy implementations.

This module provides various betting strategies for the craps simulator:
- FlatBetStrategy: Constant bet amount
- MartingaleStrategy: Double after loss
- ParetoStrategy: Follow 80/20 principle
"""

from __future__ import annotations  # REQUIRED

from dataclasses import dataclass
from typing import Protocol


class BettingStrategy(Protocol):
    """Protocol for betting strategies."""

    def calculate_bet(self, bankroll: int, consecutive_losses: int) -> int:
        """Calculate next bet amount.

        Args:
            bankroll: Current player bankroll in dollars.
            consecutive_losses: Number of consecutive losses.

        Returns:
            Bet amount in dollars.
        """
        ...


@dataclass(slots=True, frozen=True)
class FlatBetStrategy:
    """Constant bet amount strategy.

    Attributes:
        bet_amount: Fixed amount to bet each round.
    """

    bet_amount: int

    def __post_init__(self) -> None:
        """Validate bet amount."""
        if self.bet_amount <= 0:
            raise ValueError(f"Bet amount must be positive, got {self.bet_amount}")

    def calculate_bet(self, bankroll: int, consecutive_losses: int) -> int:
        """Calculate next bet (always returns fixed amount).

        Args:
            bankroll: Current bankroll (must be positive).
            consecutive_losses: Ignored for flat betting.

        Returns:
            Fixed bet amount (or bankroll if less than bet amount).

        Raises:
            ValueError: If bankroll is negative.
        """
        if bankroll < 0:
            raise ValueError(f"Bankroll cannot be negative, got {bankroll}")
        return min(self.bet_amount, bankroll)


@dataclass(slots=True, frozen=True)
class MartingaleStrategy:
    """Martingale strategy - double bet after each loss.

    WARNING: High risk of ruin. Requires large bankroll.

    Attributes:
        base_bet: Initial bet amount.
        max_bet: Maximum bet (safety limit).
    """

    base_bet: int
    max_bet: int

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.base_bet <= 0:
            raise ValueError(f"Base bet must be positive, got {self.base_bet}")
        if self.max_bet < self.base_bet:
            raise ValueError(f"Max bet {self.max_bet} below base bet {self.base_bet}")

    def calculate_bet(self, bankroll: int, consecutive_losses: int) -> int:
        """Calculate next bet based on losses.

        Bet doubles after each loss: base_bet * 2^losses

        Args:
            bankroll: Current bankroll.
            consecutive_losses: Number of consecutive losses.

        Returns:
            Calculated bet amount (capped by max_bet and bankroll).

        Raises:
            ValueError: If bankroll is negative or consecutive_losses negative.
        """
        if bankroll < 0:
            raise ValueError(f"Bankroll cannot be negative, got {bankroll}")
        if consecutive_losses < 0:
            raise ValueError(f"Losses cannot be negative, got {consecutive_losses}")

        bet = self.base_bet * (2 ** consecutive_losses)
        return min(bet, self.max_bet, bankroll)
```

**2. Test File (tests/test_strategy.py)**
```python
"""Tests for betting strategy implementations."""

import pytest
from p6_craps.strategy import FlatBetStrategy, MartingaleStrategy


class TestFlatBetStrategy:
    """Test suite for FlatBetStrategy."""

    def test_returns_fixed_amount(self):
        """Should return same bet regardless of losses."""
        strategy = FlatBetStrategy(bet_amount=10)
        assert strategy.calculate_bet(100, 0) == 10
        assert strategy.calculate_bet(100, 5) == 10

    def test_respects_bankroll_limit(self):
        """Should not exceed available bankroll."""
        strategy = FlatBetStrategy(bet_amount=50)
        assert strategy.calculate_bet(30, 0) == 30

    def test_raises_on_negative_bet(self):
        """Should reject negative bet amounts."""
        with pytest.raises(ValueError, match="positive"):
            FlatBetStrategy(bet_amount=-10)

    def test_raises_on_zero_bet(self):
        """Should reject zero bet amount."""
        with pytest.raises(ValueError, match="positive"):
            FlatBetStrategy(bet_amount=0)

    def test_raises_on_negative_bankroll(self):
        """Should reject negative bankroll."""
        strategy = FlatBetStrategy(bet_amount=10)
        with pytest.raises(ValueError, match="negative"):
            strategy.calculate_bet(-10, 0)


class TestMartingaleStrategy:
    """Test suite for MartingaleStrategy."""

    def test_initial_bet_is_base(self):
        """First bet should equal base bet."""
        strategy = MartingaleStrategy(base_bet=10, max_bet=1000)
        assert strategy.calculate_bet(100, 0) == 10

    @pytest.mark.parametrize("losses,expected", [
        (0, 10),
        (1, 20),
        (2, 40),
        (3, 80),
        (4, 160),
    ])
    def test_doubles_after_each_loss(self, losses, expected):
        """Should double bet after each consecutive loss."""
        strategy = MartingaleStrategy(base_bet=10, max_bet=1000)
        assert strategy.calculate_bet(1000, losses) == expected

    def test_respects_max_bet_limit(self):
        """Should not exceed maximum bet."""
        strategy = MartingaleStrategy(base_bet=10, max_bet=50)
        # After 10 losses, bet would be 10240, but capped at 50
        assert strategy.calculate_bet(10000, 10) == 50

    def test_respects_bankroll_limit(self):
        """Should not exceed available bankroll."""
        strategy = MartingaleStrategy(base_bet=10, max_bet=1000)
        assert strategy.calculate_bet(30, 5) == 30  # Would be 320, but only 30 available

    def test_raises_on_invalid_config(self):
        """Should reject invalid configuration."""
        with pytest.raises(ValueError):
            MartingaleStrategy(base_bet=-10, max_bet=100)

        with pytest.raises(ValueError):
            MartingaleStrategy(base_bet=100, max_bet=50)

    def test_raises_on_negative_inputs(self):
        """Should reject negative inputs."""
        strategy = MartingaleStrategy(base_bet=10, max_bet=100)

        with pytest.raises(ValueError, match="negative"):
            strategy.calculate_bet(-10, 0)

        with pytest.raises(ValueError, match="negative"):
            strategy.calculate_bet(100, -1)
```

## Quality Gates

### Checklist Before Commit

- [ ] All tests pass: `uv run pytest -v --cov=p6_craps`
- [ ] Coverage maintained/improved (90%+ target)
- [ ] Type hints added to all functions
- [ ] Docstrings added/updated (Google style)
- [ ] Input validation in place
- [ ] No hardcoded values (use constants.py)
- [ ] No commented-out code
- [ ] No print() statements (use logging)
- [ ] Security scan passes: `uv run bandit -r p6_craps`
- [ ] No secrets: `uv run detect-secrets scan`
- [ ] Pre-commit passes: `uv run pre-commit run --all-files`

### Conventional Commits

Format: `<type>: <description>`

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `style:` Formatting
- `perf:` Performance
- `chore:` Maintenance

**Examples:**
```bash
git commit -m "feat: add Martingale betting strategy"
git commit -m "fix: prevent negative bankroll in Player class"
git commit -m "test: add edge cases for seven-out scenario"
git commit -m "docs: update README with simulation usage"
git commit -m "perf: optimize roll generation with cached RNG"
```

## Domain Knowledge

### Craps Rules

**COME_OUT Phase** (start of new betting round):
- Roll 7 or 11: **Pass Line WINS** (natural)
- Roll 2, 3, or 12: **Pass Line LOSES** (craps)
- Roll 4, 5, 6, 8, 9, 10: **Establish POINT** → Move to POINT_ON phase

**POINT_ON Phase** (point established):
- Roll the point number: **Pass Line WINS** → Return to COME_OUT
- Roll a 7: **Pass Line LOSES** (seven out) → Return to COME_OUT
- Roll any other number: **Continue rolling** (stay in POINT_ON)

### Craps Terminology

- **Come-out roll**: First roll of a new round
- **Point**: Target number (4, 5, 6, 8, 9, or 10)
- **Natural**: 7 or 11 on come-out (instant win)
- **Craps**: 2, 3, or 12 on come-out (instant loss)
- **Seven out**: Rolling 7 during point-on (ends round, pass line loses)
- **Pass Line**: Main bet type (currently implemented)
- **House edge**: Casino's mathematical advantage (~1.41% for pass line)

### Betting Strategies

**Implemented:**
- Pass Line betting (basic)

**To Implement:**
- Flat betting: Fixed amount each bet
- Martingale: Double after each loss
- Reverse Martingale (Paroli): Double after each win
- D'Alembert: Increase by 1 unit after loss, decrease after win
- Fibonacci: Follow Fibonacci sequence
- Kelly Criterion: Bet proportion based on edge and odds

## Common Tasks

### Adding a New Module

1. Create file in `p6_craps/`
2. Add module-level docstring
3. Add `from __future__ import annotations`
4. Implement with proper patterns
5. Create test file in `tests/`
6. Update `p6_craps/__init__.py`
7. Run `uv run pre-commit run --all-files`

### Adding a New Dependency

1. Evaluate necessity
2. Check license and security
3. Add: `uv add <package>` or `uv add --dev <package>`
4. Audit: `uv run pip-audit`
5. Update imports in code
6. Run tests: `uv run pytest -v`

### Fixing a Bug

1. Write failing test that reproduces bug
2. Fix implementation
3. Verify test now passes
4. Run full test suite
5. Run pre-commit hooks
6. Commit: `fix: description of bug fixed`

### Optimizing Performance

1. Profile first: `python -m cProfile -s cumulative bin/script.py`
2. Identify bottleneck
3. Optimize specific hotspot
4. Benchmark improvement
5. Ensure tests still pass
6. Document optimization
7. Commit: `perf: description of optimization`

## Quick Reference

### Essential Commands

```bash
# Development
uv sync                                    # Install dependencies
uv run pytest -v --cov=p6_craps           # Run tests with coverage
uv run pre-commit run --all-files         # Run all quality gates
uv run python bin/script.py --debug       # Run CLI in debug mode

# Code Quality
uv run black .                             # Format code
uv run isort .                             # Sort imports
uv run flake8                              # Lint
uv run pylint p6_craps bin                # Static analysis
uv run pydocstyle p6_craps                # Docstring check
uv run pyre check                          # Type check

# Security
uv run bandit -r p6_craps                 # Security scan
uv run detect-secrets scan                # Secret detection
uv run pip-audit                           # Dependency audit

# Dependencies
uv add <package>                           # Add production dependency
uv add --dev <package>                     # Add dev dependency
uv lock --upgrade                          # Update dependencies
uv tree                                    # Show dependency tree
```

### File Templates

**New Module Template:**
```python
"""One-line summary of module purpose.

Detailed description of what this module provides and how it fits
into the overall architecture.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional

# Imports from project
from .constants import CONSTANT_NAME


# Your code here...
```

**New Test Template:**
```python
"""Tests for module_name.

This module tests the behavior of module_name including:
- Basic functionality
- Edge cases
- Error conditions
"""

import pytest
import random

from p6_craps.module_name import ClassName


class TestClassName:
    """Test suite for ClassName."""

    def test_basic_behavior(self):
        """Should do X when Y."""
        # Your test here...
        pass
```

## Resources

- **Python 3.14 Docs**: https://docs.python.org/3.14/
- **uv Documentation**: https://docs.astral.sh/uv/
- **pytest Documentation**: https://docs.pytest.org/
- **Black Documentation**: https://black.readthedocs.io/
- **OWASP Python Security**: https://owasp.org/www-project-python-security/
- **Craps Rules**: https://en.wikipedia.org/wiki/Craps

## Summary

When working on p6-craps-py:

1. **Read existing code** before making changes
2. **Follow established patterns** (dataclasses, enums, DI)
3. **Write tests first** (TDD approach)
4. **Validate all inputs** (security)
5. **Use type hints everywhere**
6. **Document with docstrings**
7. **Run pre-commit before pushing**
8. **Make incremental changes**
9. **Think about performance** (but measure first)
10. **Keep it simple** (YAGNI, KISS)

**Core Values:**
- ✅ Correctness (comprehensive tests)
- ✅ Maintainability (clear, documented code)
- ✅ Security (validated inputs, no secrets)
- ✅ Performance (efficient algorithms)
- ✅ Quality (all gates pass)

---

**Last Updated**: 2026-01-20
**Python Version**: 3.14.2
**Project Status**: Active Development

For AI-specific instructions, see:
- `.github/copilot-instructions.md` (GitHub Copilot)
- `.github/agents/*.agent.md` (GitHub Copilot Agents)
- `.claude/instructions.md` (Claude Code)
- `.cursorrules` (Cursor IDE)
- `.aider.conf.yml` (Aider)
