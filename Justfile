# ============================================================================
# canVODpy Monorepo - Root Justfile
# ============================================================================

# Default command lists all available recipes
_default:
    @just --list --unsorted

alias c := clean
alias h := hooks
alias q := check
alias t := test

# ============================================================================
# Code Quality (All Packages)
# ============================================================================

# lint python code using ruff
[private]
check-lint:
    uv run ruff check . --fix

# format python code using ruff
[private]
check-format:
    uv run ruff format .

# run the type checker ty
[private]
check-types:
    uv run ty check

# lint, format with ruff and type-check with ty (all packages)
check: check-lint check-format check-types

# ============================================================================
# Testing (All Packages)
# ============================================================================

# run tests with coverage for all packages
test:
    uv run pytest

# ============================================================================
# Utilities
# ============================================================================

# setup the pre-commit hooks
hooks:
    uvx pre-commit install

# clean all python build/compilation files and directories
clean: clean-build clean-pyc clean-test

# remove build artifacts
[private]
clean-build:
    rm -fr build/
    rm -fr _build/
    rm -fr dist/
    rm -fr .eggs/
    find . -name '*.egg-info' -exec rm -fr {} +
    find . -name '*.egg' -exec rm -f {} +

# remove Python file artifacts
[private]
clean-pyc:
    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f {} +
    find . -name '__pycache__' -exec rm -fr {} +

# remove test and coverage artifacts
[private]
clean-test:
    rm -f .coverage
    rm -fr htmlcov/
    rm -fr .pytest_cache

# install all packages in workspace
sync:
    uv sync

# ============================================================================
# Per-Package Commands
# ============================================================================

# run check for a specific package
check-package PACKAGE:
    cd packages/{{PACKAGE}} && uv run ruff check . --fix && uv run ruff format . && uv run ty check

# run tests for a specific package
test-package PACKAGE:
    cd packages/{{PACKAGE}} && uv run pytest

# build a specific package
build-package PACKAGE:
    cd packages/{{PACKAGE}} && uv build

# ============================================================================
# Documentation
# ============================================================================

# preview the documentation locally
docs:
    uv run myst
