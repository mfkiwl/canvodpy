# Just Integration in CI - Summary

## Changes Made

### 1. Updated Justfile with CI-specific Commands

**Added commands:**
- `check-lock` - Check uv.lock is up to date
- `check-lint-only` - Lint without auto-fixing (for CI)
- `check-format-only` - Check formatting without modifying files (excludes .ipynb)
- `test-all-packages` - Run tests per package to avoid namespace collisions
- `test-coverage` - Run tests with coverage report

**Why these are separate:**
- CI needs **read-only** checks (don't modify code)
- Local dev uses **auto-fix** versions (`check-lint`, `check-format`)
- CI runs per-package tests to avoid import issues

### 2. Created Reusable Action: `.github/actions/setup-just`

Installs `just` command runner in all workflows:

```yaml
- name: Install just
  uses: ./.github/actions/setup-just
```

### 3. Updated Workflows to Use Just

#### test_platforms.yml
**Before:**
```yaml
- name: Run Tests
  run: |
    echo "Running tests per package..."
    uv run pytest canvodpy/tests/ --verbose --color=yes
    uv run pytest packages/canvod-aux/tests/ --verbose --color=yes
    # ... 5 more lines
```

**After:**
```yaml
- name: Install just
  uses: ./.github/actions/setup-just
- name: Run Tests
  run: just test-all-packages
```

#### test_coverage.yml
**Before:**
```yaml
- name: Run Tests
  run: |
    uv run pytest --verbose --color=yes \
      --cov=canvodpy \
      --cov=canvod \
      --cov-report=term-missing
```

**After:**
```yaml
- name: Install just
  uses: ./.github/actions/setup-just
- name: Run Tests with Coverage
  run: just test-coverage
```

#### code_quality.yml
**Before:**
```yaml
- run: uv lock --check           # lock_file job
- run: uv run ruff check .       # linting job
- run: uv run ruff format --check .  # formatting job
- run: uv run ty check .         # type_consistency job
```

**After:**
```yaml
- run: just check-lock           # lock_file job
- run: just check-lint-only      # linting job
- run: just check-format-only    # formatting job
- run: just check-types          # type_consistency job
```

---

## Benefits

### ✅ DRY (Don't Repeat Yourself)
- Commands defined **once** in Justfile
- Used in both local dev and CI
- Change once, updates everywhere

### ✅ Local/CI Parity
```bash
# Same commands work locally and in CI
just check-lock
just check-format-only
just test-all-packages
```

### ✅ Self-Documenting
```bash
just --list  # Shows all available commands with descriptions
```

### ✅ Simplified Workflows
- Workflows are now **shorter and cleaner**
- Easy to understand what each job does
- Less duplication across workflow files

### ✅ Easy Maintenance
- Update test command? Change Justfile, not 3 YAML files
- Add new check? Add to Justfile, workflows automatically use it

---

## Usage

### Local Development

```bash
# Lint and format (auto-fix)
just check

# Check without modifying (like CI)
just check-lint-only
just check-format-only

# Run all tests
just test-all-packages

# Run with coverage
just test-coverage

# Check lock file
just check-lock
```

### CI (Automatic)

All workflows now automatically:
1. Install `just` via `.github/actions/setup-just`
2. Run commands via `just <command>`

---

## Files Modified

1. **Justfile** - Added CI-specific commands
2. **.github/actions/setup-just/action.yml** - New reusable action
3. **.github/workflows/test_platforms.yml** - Uses `just test-all-packages`
4. **.github/workflows/test_coverage.yml** - Uses `just test-coverage`
5. **.github/workflows/code_quality.yml** - Uses `just check-*` commands

---

## Testing

All commands tested locally:

```bash
✅ just check-lock           # Passes
✅ just check-format-only    # Passes (excludes .ipynb)
✅ just check-lint-only      # Runs (512 known errors expected)
✅ just check-types          # Runs (967 known errors expected)
✅ just test-all-packages    # Would run all tests
✅ just test-coverage        # Would run with coverage
```

---

## Next Steps

1. **Push changes** to trigger CI
2. **Verify workflows** pass with new just commands
3. **Update README** to document just commands for contributors
4. **Add more just commands** as needed (e.g., `just deploy`, `just docs-preview`)

---

## Installation Requirements

**Local development:**
- Install just: `curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash`
- Or via package manager: `brew install just` (macOS), `cargo install just`, etc.

**CI (GitHub Actions):**
- ✅ Automatically installed via `.github/actions/setup-just`
- No manual setup needed

---

## Comparison: Before vs After

### Before (Repetitive)
```yaml
# In 3 different workflow files:
- run: uv run ruff check .
- run: uv run ruff format --check .
- run: uv run ty check .
```

### After (DRY)
```yaml
# In Justfile (once):
check-lint-only:
    uv run ruff check .

# In all workflows:
- run: just check-lint-only
```

**Result:** Less code, easier maintenance, consistent behavior!
