# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import functools
import sys
from pathlib import Path

import git
import tomli

from docs import utils

# -- Project information -----------------------------------------------------

project = "Bot Core"
copyright = "2021, Python Discord"
author = "Python Discord"

PROJECT_ROOT = Path(__file__).parent.parent
REPO_LINK = "https://github.com/python-discord/bot-core"
SOURCE_FILE_LINK = f"{REPO_LINK}/blob/{git.Repo(PROJECT_ROOT).commit().hexsha}"

sys.path.insert(0, str(PROJECT_ROOT.absolute()))

# The full version, including alpha/beta/rc tags
release = version = tomli.loads(
    (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
)["tool"]["poetry"]["version"]

# -- General configuration ---------------------------------------------------

add_module_names = False

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "releases",
    "sphinx.ext.linkcode",
    "sphinx.ext.githubpages",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

html_theme_options = {
    "light_css_variables": {
        "color-api-name": "var(--color-link)",
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_title = f"{project} v{version}"
html_short_title = project

html_logo = "https://raw.githubusercontent.com/python-discord/branding/main/logos/logo_full/logo_full.min.svg"
html_favicon = html_logo

html_css_files = [
    "changelog.css",
    "logo.css",
]

html_js_files = [
    "changelog.js",
]


def skip(*args) -> bool:
    """Things that should be skipped by the autodoc generation."""
    name = args[2]
    would_skip = args[4]

    if name in (
        "__weakref__",
    ):
        return True
    return would_skip


# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for napoleon extension ------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_attr_annotations = True


# -- Options for releases extension ------------------------------------------
releases_github_path = REPO_LINK.removeprefix("https://github.com/")


# -- Options for extlinks extension ------------------------------------------
extlinks = {
    "repo-file": (f"{REPO_LINK}/blob/main/%s", "repo-file %s")
}


# -- Options for intersphinx extension ---------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "discord": ("https://discordpy.readthedocs.io/en/master/", None),
}


# -- Options for the autodoc extension ---------------------------------------
utils.cleanup()
autodoc_default_options = {
    "members": True,
    "special-members": True,
    "show-inheritance": True,
    "imported-members": False,
    "exclude-members": "__weakref__"
}


# -- Options for the linkcode extension --------------------------------------
linkcode_resolve = functools.partial(utils.linkcode_resolve, SOURCE_FILE_LINK)
