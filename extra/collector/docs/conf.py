# Configuration file for the Sphinx documentation builder.

project = "BallsDex Collector"
copyright = "2026, flare"
author = "flare"
release = "0.0.2"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "myst_parser",
]

myst_enable_extensions = ["dollarmath"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "source_repository": "https://github.com/flaree/ballsdex-collector",
    "source_branch": "master",
    "source_directory": "docs/",
}
