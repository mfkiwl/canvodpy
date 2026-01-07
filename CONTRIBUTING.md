# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

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

1. Fork the `canvodpy` repo on GitHub.

2. Clone your fork locally:

   ```sh
   git clone git@github.com:your_name_here/canvodpy.git
   cd canvodpy
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
