# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'stringart'
copyright = '2025, Marco Giunta'
author = 'Marco Giunta'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    # 'nbsphinx',
    "sphinx.ext.mathjax",
    'sphinx_copybutton'
]

myst_enable_extensions = [
    'dollarmath'
]

templates_path = ['_templates']
exclude_patterns = []

import sys
from pathlib import Path

sys.path.insert(0, str(Path('..', 'src').resolve()))

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
# html_theme = "sphinx_rtd_theme"
# html_theme_options = {
#     "collapse_navigation": True,
#     "navigation_depth": 2,
# }
html_static_path = ['_static']
