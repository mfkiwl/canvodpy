# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# Add source to path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# -- Project information -----------------------------------------------------
project = "canvod-readers"
copyright = "2025, Nicolas François Bader, TU Wien"
author = "Nicolas François Bader"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",  # MyST Markdown parser
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.napoleon",  # Support NumPy/Google docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Link to other docs
    "sphinx_design",  # Cards, grids, tabs
]

# MyST configuration
myst_enable_extensions = [
    "colon_fence",  # ::: directive syntax
    "deflist",  # Definition lists
    "fieldlist",  # Field lists
    "html_image",  # HTML image support
    "linkify",  # Auto-link URLs
    "replacements",  # Text replacements
    "smartquotes",  # Smart quotes
    "tasklist",  # Task lists with checkboxes
]

myst_heading_anchors = 3  # Auto-generate anchors for h1, h2, h3

# Napoleon configuration (NumPy style docstrings)
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc configuration
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# Templates and static files
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Source file suffix
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Master document
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_title = "canvod-readers"

html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#0066cc",
        "color-brand-content": "#0066cc",
    },
    "dark_css_variables": {
        "color-brand-primary": "#3399ff",
        "color-brand-content": "#3399ff",
    },
}

html_static_path = []  # No custom static files yet

# Add any paths that contain custom static files (such as style sheets)
# html_static_path = ['_static']

# If true, links to the reST sources are added to the pages
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer
html_show_sphinx = True

# Output file base name for HTML help builder
htmlhelp_basename = "canvod-readersdoc"
