# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Development Environment Setup

### Required Tools (Install These First!)

This project requires two external tools that are **not** installed via `uv sync`:

#### 1. uv (Python Package Manager)

**Check if installed:** `uv --version`

**Installation:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Package managers
brew install uv          # macOS
cargo install uv         # Rust
```

📚 [uv documentation](https://docs.astral.sh/uv/)

#### 2. just (Command Runner)

**Check if installed:** `just --version`

**Installation:**
```bash
# Quick install (macOS/Linux)
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash

# Package managers
brew install just        # macOS
cargo install just       # Rust
apt install just         # Ubuntu 23.04+
```

📚 [just documentation](https://github.com/casey/just)

**Why just?** It's used for all development tasks (testing, linting, etc.) and in CI/CD.

---

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/nfb2021/canvodpy/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

canVODpy could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/nfb2021/canvodpy/issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `canvodpy` for local development.

1. **Install required tools** (see "Required Tools" section above):
   - Install `uv` (Python package manager)
   - Install `just` (command runner)

2. Fork the `canvodpy` repo on GitHub.

3. Clone your fork locally:

   ```sh
   git clone git@github.com:your_name_here/canvodpy.git
   cd canvodpy
   ```

4. Verify required tools are installed:

   ```sh
   just check-dev-tools  # Checks uv, just, python3
   ```

4. Install Python dependencies:

   ```sh
   uv sync
   ```

5. Install pre-commit hooks (recommended):

   ```sh
   just hooks
   ```

6. Create a branch for local development:

   ```sh
   git checkout -b name-of-your-bugfix-or-feature
   ```

7. Make your changes and verify them:

   ```sh
   # Run tests
   just test

   # Check code quality (lint + format + type-check)
   just check
   ```

8. Commit your changes using conventional commits:

   ```sh
   git add .
   git commit -m "feat(readers): add support for RINEX 4.0 format"
   # or use interactive helper
   uv run cz commit
   ```

   **Commit Message Format:**
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```

   **Types:**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `refactor`: Code restructure (no behavior change)
   - `test`: Add/modify tests
   - `chore`: Build/tools/dependencies
   - `perf`: Performance improvements
   - `ci`: CI/CD changes

   **Scopes** (monorepo packages):
   - `readers`, `aux`, `grids`, `vod`, `store`, `viz`, `utils`
   - `orchestrator`, `diagnostics`, `ci`, `docs`, `deps`

   **Examples:**
   ```bash
   git commit -m "feat(vod): add tau-omega calculator"
   git commit -m "fix(readers): handle empty RINEX files"
   git commit -m "docs: update installation instructions"
   git commit -m "test(grids): add property tests for equal-area grid"
   git commit -m "feat(viz)!: redesign 3D plotting API"  # ! = breaking change
   ```

   See [Conventional Commits](https://www.conventionalcommits.org/) for details.

9. Push your branch and submit a pull request:

   ```sh
   git push origin name-of-your-bugfix-or-feature
   ```

### Common Development Commands

```bash
# See all available commands
just --list

# Run tests
just test                  # Run all tests
just test-coverage         # With coverage report
just test-package canvod-grids  # Specific package

# Code quality
just check                 # Lint + format + type-check
just check-lint            # Just linting
just check-format          # Just formatting

# Documentation
just docs                  # Preview docs locally
```

3. Install your local copy into a virtualenv. Assuming you have [uv] and [Just] installed:

   ```sh
   # Setup virtual environment
   uv sync

   # Install pre-commit hooks
   just hooks
   ```

4. Create a branch for local development:

   ```sh
   git checkout -b name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

5. When you're done making changes, check that your changes are formatted correctly and pass tests:

   ```sh
   # Lint, format, typecheck and run tests
   just check
   just test

   # Or run full CI suite
   just ci 3.13
   ```

6. Commit your changes and push your branch to GitHub:

   ```sh
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md.
3. The pull request should work for Python 3.13+. Tests run in GitHub Actions on every pull request to the main branch.

## Workspace Development

This project uses a monorepo structure with multiple packages. When developing:

- Work on individual packages in `packages/` or `canvodpy/`
- Run package-specific commands: `just check-package canvod-readers`
- Run workspace-wide commands: `just check`, `just test`
- All packages share a single lockfile and virtual environment

## Code Quality Standards

We use:
- **ruff** for linting and formatting (ALL rules enabled)
- **ty** for type checking
- **pytest** for testing with coverage

Run `just check` before committing to ensure code quality.

## Deploying

A reminder for the maintainers on how to deploy. Make sure all your changes are committed. Then run:

```sh
just bump minor  # possible: major / minor / patch
git push
git push --tags
```

GitHub Actions will automatically publish to PyPI when you push a new tag.

[uv]: https://docs.astral.sh/uv/
[Just]: https://github.com/casey/just
