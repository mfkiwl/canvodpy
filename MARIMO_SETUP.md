# Marimo Setup for canVODpy Documentation

## What Changed

Switched from Jupyter notebooks to **marimo** for interactive documentation and examples.

### Why Marimo?

- ✅ **Reactive**: Cells automatically re-run when dependencies change
- ✅ **Python files**: Notebooks are `.py` files (better for version control)
- ✅ **Git-friendly**: Easy to diff, merge, and review
- ✅ **Clean execution**: No hidden state, cells run in dependency order
- ✅ **Modern UI**: Better developer experience than Jupyter

## Installation

Marimo is now included in the `dev` dependency group:

```bash
uv sync
```

## Running Examples

### canvod-readers

```bash
# Navigate to package
cd packages/canvod-readers

# Edit mode (interactive development)
just marimo
# or
uv run marimo edit docs/examples.py

# Presentation mode (read-only, for demos)
just marimo-present
# or
uv run marimo run docs/examples.py
```

## Creating New Marimo Notebooks

### Quick Start

```bash
# Create new notebook
uv run marimo new my_notebook.py

# Or convert from Jupyter
uv run marimo convert notebook.ipynb > notebook.py
```

### Structure

Marimo notebooks are Python files with a special structure:

```python
import marimo

app = marimo.App()

@app.cell
def __():
    import marimo as mo
    return mo,

@app.cell
def __(mo):
    mo.md("# My Title")
    return

@app.cell
def __():
    x = 42
    return x,

@app.cell
def __(x):
    print(f"The answer is {x}")
    return

if __name__ == "__main__":
    app.run()
```

## Key Features

### 1. Reactive Execution

When you change a cell, all dependent cells automatically re-run:

```python
@app.cell
def __():
    x = 10
    return x,

@app.cell
def __(x):
    # This automatically updates when x changes
    y = x * 2
    return y,
```

### 2. Rich Output

```python
@app.cell
def __(mo):
    mo.md(r"""
    # Markdown with math

    $$E = mc^2$$
    """)
    return
```

### 3. Interactive Widgets

```python
@app.cell
def __(mo):
    slider = mo.ui.slider(0, 100, value=50)
    slider
    return slider,

@app.cell
def __(slider):
    print(f"Slider value: {slider.value}")
    return
```

### 4. Dataframe Explorer

```python
@app.cell
def __(ds, mo):
    # Automatically creates interactive table
    mo.ui.dataframe(ds.to_dataframe())
    return
```

## Best Practices

### 1. One Return Statement Per Cell

```python
@app.cell
def __():
    import pandas as pd
    import numpy as np
    return pd, np
```

### 2. Explicit Dependencies

Marimo tracks dependencies automatically:

```python
@app.cell
def __(pd):  # Depends on pd from previous cell
    df = pd.DataFrame({'a': [1, 2, 3]})
    return df,
```

### 3. Use `mo.md()` for Documentation

```python
@app.cell
def __(mo):
    mo.md(
        r"""
        ## Section Title

        Explain your code here with **markdown**.
        """
    )
    return
```

### 4. Organize Cells Logically

- Imports at the top
- Setup/configuration
- Main logic
- Visualization
- Summary

## Converting Existing Jupyter Notebooks

If you have existing Jupyter notebooks:

```bash
# Convert to marimo
uv run marimo convert docs/index.ipynb > docs/examples.py

# Edit and refine
uv run marimo edit docs/examples.py
```

## Integration with Documentation

Marimo notebooks can be:

1. **Run directly**: `marimo edit docs/examples.py`
2. **Exported to HTML**: `marimo export html docs/examples.py`
3. **Used in CI/CD**: Run notebooks as tests
4. **Shared as scripts**: They're just Python files!

## VSCode Integration

Marimo works great in VSCode:

1. **Edit in browser**: Run `marimo edit` and it opens in your browser
2. **Version control**: It's a `.py` file, so git diff works perfectly
3. **Linting**: Ruff and other tools work normally
4. **Type checking**: But we exclude them from ty checks (they have special syntax)

## Resources

- [Marimo Documentation](https://docs.marimo.io/)
- [Marimo GitHub](https://github.com/marimo-team/marimo)
- [Examples Gallery](https://marimo.io/gallery)

## Next Steps

Create marimo notebooks for other packages:

```bash
cd packages/canvod-grids
uv run marimo new docs/examples.py

cd packages/canvod-vod
uv run marimo new docs/examples.py

# ... etc
```
