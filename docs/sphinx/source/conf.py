# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
import os

sys.path.insert(0, os.path.abspath("./extensions/"))
sys.path.insert(0, os.path.abspath("../../.."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import caterpillar

project = "Caterpillar"
author = caterpillar.__author__
copyright = f"2024, {author}"
release = version = caterpillar.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "breathe",
    "c_annotations",
    "sphinx_copybutton"
]

templates_path = ["_templates"]
exclude_patterns = []


# The master toctree document.
master_doc = "index"

# The suffix of source filenames.
source_suffix = ".rst"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

refcount_file = '../../../src/capi.dat'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_theme_options = {
    "show_nav_level": 4,
    "navbar_end": ["navbar-icon-links", "theme-switcher"],
    "collapse_navigation": False,
    "github_url": "https://github.com/MatrixEditor/caterpillar",
    "logo": {
        "text": f"Caterpillar {version}",
    },
    "announcement": "https://raw.githubusercontent.com/MatrixEditor/caterpillar/master/docs/sphinx/source/_templates/announcement.html",
}
html_sidebars = {
  "installing/index": [],
}

# -- Options for C++ Docs -----------------------------------------------------
breathe_default_project = "caterpillar"
breathe_projects = {"caterpillar": "../../doxygen/build/xml/"}
