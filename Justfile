# ============================================================================
# canVODpy Monorepo - Root Justfile
# ============================================================================

# ANSI color codes
GREEN := '\033[0;32m'
BOLD := '\033[1m'
NORMAL := '\033[0m'

# Default command lists all available recipes
_default:
    @just --list --unsorted

alias c := clean
alias d := dist
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
    uv run pytest tests/

# run tests for all supported Python versions
testall:
    uv run --python=3.13 pytest

# run all formatting, linting, and testing commands
ci PYTHON="3.13":
    uv run --python={{ PYTHON }} ruff format .
    uv run --python={{ PYTHON }} ruff check . --fix
    uv run --python={{ PYTHON }} ty check .
    uv run --python={{ PYTHON }} pytest tests/

# ============================================================================
# Utilities
# ============================================================================

# setup the pre-commit hooks
hooks:
    uvx pre-commit install

# print the current status of the project
status:
    @echo "canVODpy Monorepo"
    @echo "Running on: `uname`"

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
# Version Management
# ============================================================================
# Note: Version management should be done at the package level
# Use: just build-package <package-name>
# Workspace root does not have a version

# [confirm("Do you really want to bump? (y/n)")]
# [private]
# prompt-confirm:

# bump the version, commit and add a tag <major|minor|patch|...>
# bump INCREMENT="patch": && tag
#     @uv version --bump {{ INCREMENT }} --dry-run
#     @just prompt-confirm
#     uv version --bump {{ INCREMENT }}

# tag the latest version
# tag VERSION=`uv version --short`:
#     git add pyproject.toml
#     git add uv.lock
#     git commit -m "Bumped version to {{VERSION}}"
#     git tag -a "v{{VERSION}}"
#     @echo "{{ GREEN }}{{ BOLD }}Version has been bumped to {{VERSION}}.{{ NORMAL }}"

# ============================================================================
# Building & Distribution
# ============================================================================

# build the source distribution and wheel file
dist:
    uv build

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

# preview the documentation locally (serve the myst website)
docs:
    uv run myst

# ============================================================================
# Dependency Analysis
# ============================================================================

# generate ALL dependency graphs (per-package + cross-package + API) using pydeps
deps-all:
    @echo "{{ GREEN }}{{ BOLD }}Generating comprehensive dependency graphs...{{ NORMAL }}"
    @python3 scripts/generate_all_graphs.py --type all --open
    @echo "{{ GREEN }}{{ BOLD }}✨ Open dependency-graphs/index.html to view all graphs{{ NORMAL }}"

# generate internal dependency graph for specific package
deps-package PACKAGE:
    @python3 scripts/generate_all_graphs.py --type internal --package {{PACKAGE}}
    @echo "{{ GREEN }}{{ BOLD }}✅ Created dependency-graphs/{{PACKAGE}}-internal.svg{{ NORMAL }}"

# generate cross-package dependency graph
deps-cross:
    @python3 scripts/generate_all_graphs.py --type cross-package
    @echo "{{ GREEN }}{{ BOLD }}✅ Created dependency-graphs/cross-package-dependencies.svg{{ NORMAL }}"

# generate API orchestration graph (how umbrella uses everything)
deps-api:
    @python3 scripts/generate_all_graphs.py --type api
    @echo "{{ GREEN }}{{ BOLD }}✅ Created dependency-graphs/api-orchestration.svg{{ NORMAL }}"

# quick dependency overview (package-level metrics)
deps-report:
    @python3 scripts/analyze_dependencies.py --format report

# generate dependency graph (Mermaid format)
deps-mermaid:
    python3 scripts/analyze_dependencies.py --format mermaid

# ============================================================================
# Initialization
# ============================================================================

# initialize a git repo and add all files
init: sync
    git init --initial-branch=main
    git add .
    git commit -m "initial commit"
    @echo "{{ GREEN }}{{ BOLD }}Git has been initialized{{ NORMAL }}"
