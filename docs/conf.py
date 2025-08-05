import os, sys, datetime

# -- Project setup --
project = "SelfbotV2"
author = "Bjarnos"
copyright = f"{datetime.datetime.now().year}, {author}"
release = "0.1.0"

# -- Path setup --
sys.path.insert(0, os.path.abspath(".."))

# -- General config --
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",      # Google/NumPy-style docstrings
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages"
]

templates_path = ["_templates"]
exclude_patterns = []

# -- HTML output --
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
