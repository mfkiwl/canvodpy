# VSCode Testing Configuration

## Overview

The monorepo now has comprehensive VSCode testing configuration set up for all packages.

## What Was Configured

### 1. Workspace Settings (`canvodpy.code-workspace`)
- **Python Testing**: Enabled pytest with verbose output
- **Test Arguments**: `-v --tb=short --strict-markers --strict-config`
- **Auto Discovery**: Tests automatically discovered when files are saved
- **Python Environment**: Configured to use shared `.venv`
- **File Exclusions**: Hidden `__pycache__`, `.pytest_cache`, `.egg-info` folders

### 2. Package-Level Settings (`.vscode/settings.json` in each package)
Each package folder now has its own testing configuration:
- `packages/canvod-readers/.vscode/settings.json`
- `packages/canvod-aux/.vscode/settings.json`
- `packages/canvod-grids/.vscode/settings.json`
- `packages/canvod-vod/.vscode/settings.json`
- `packages/canvod-store/.vscode/settings.json`
- `packages/canvod-viz/.vscode/settings.json`
- `canvodpy/.vscode/settings.json`

## How to Use

### Running Tests in VSCode

1. **Open Testing Panel**: Click the beaker icon in the left sidebar (or `Cmd+Shift+T`)

2. **Discover Tests**: Click "Refresh Tests" button or save a test file

3. **Run Tests**:
   - Click ▶️ next to any test/file/folder to run it
   - Right-click for more options (debug, run with coverage, etc.)
   - Use keyboard shortcut: `Cmd+;` then `A` to run all tests

4. **Debug Tests**:
   - Click the debug icon next to any test
   - Set breakpoints in your test or source code
   - Step through execution

### Test Discovery

Tests are automatically discovered when:
- You save a file in the `tests/` directory
- You manually refresh the test panel
- You open VSCode

### Test File Naming Convention

VSCode will discover tests following pytest conventions:
- Files: `test_*.py` or `*_test.py`
- Classes: `Test*`
- Functions: `test_*`

## Configuration Details

### Key Settings

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-v", "--tb=short"],
  "python.testing.autoTestDiscoverOnSaveEnabled": true
}
```

### Test Arguments Explained

- `-v`: Verbose output (shows each test name)
- `--tb=short`: Short traceback format (easier to read)
- `--strict-markers`: Fail if unknown markers are used
- `--strict-config`: Fail on config file issues

### Python Environment

Each package's settings point to the shared virtual environment:
```json
"python.defaultInterpreterPath": "${workspaceFolder}/../../.venv/bin/python"
```

## Troubleshooting

### Tests Not Discovered

1. **Reload Window**: `Cmd+Shift+P` → "Developer: Reload Window"
2. **Check Python Path**: Verify `.venv` is activated in the bottom-left of VSCode
3. **Clear Test Cache**: Delete `.pytest_cache` folder and refresh
4. **Check pytest.ini**: Ensure `pytest.ini` is properly configured

### Tests Fail to Run

1. **Check Virtual Environment**: Make sure `uv sync` has been run
2. **Verify Dependencies**: Run `uv sync` to ensure all test dependencies are installed
3. **Check Working Directory**: Ensure tests are run from the package root

### Import Errors

If you see import errors:
1. Make sure you're working in the correct package folder
2. Verify the shared `.venv` contains all packages: `uv sync`
3. Check that namespace packages are installed correctly

## Related Files

- `pytest.ini` - Pytest configuration for each package
- `pyproject.toml` - Package dependencies including test dependencies
- `Justfile` - Task runner with `just test` command

## Tips

1. **Multi-folder workspace**: VSCode treats each package as a separate folder, allowing you to test them independently

2. **Quick test navigation**: Use `Cmd+T` and type the test name to jump to it

3. **Test output**: Click on failed tests to see detailed output and error traces

4. **Coverage**: Install pytest-cov to see code coverage in the test panel

5. **Keyboard shortcuts**:
   - `Cmd+; A` - Run all tests
   - `Cmd+; F` - Run failed tests
   - `Cmd+; L` - Run last test run

## Next Steps

To enhance your testing setup further:

1. **Add coverage**: Use pytest-cov plugin for coverage reports
2. **Add test markers**: Define custom markers in `pytest.ini`
3. **Configure test discovery**: Adjust `testpaths` in `pytest.ini` if needed
4. **Setup continuous testing**: Enable "Run Tests on Save" in VSCode settings
