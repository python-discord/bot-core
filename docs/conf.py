# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import contextlib
import functools
import os.path
import shutil
import sys
from pathlib import Path

import git
import releases
import sphinx.util.logging
import tomli
from sphinx.application import Sphinx

logger = sphinx.util.logging.getLogger(__name__)

# Handle the path not being set correctly in actions.
sys.path.insert(0, os.path.abspath(".."))

from docs import utils  # noqa: E402

# -- Project information -----------------------------------------------------

project = "Pydis Core"
copyright = "2021, Python Discord"
author = "Python Discord"

REPO_LINK = "https://github.com/python-discord/bot-core"

PROJECT_ROOT = Path(__file__).parent.parent
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
    "sphinx_multiversion",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates", "pages"]

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

# Html files under pages/ are rendered separately and added to the final build
html_additional_pages = {
    file.removesuffix(".html"): file
    for file in utils.get_recursive_file_uris(Path("pages"), "*.html")
}

html_title = f"{project} v{version}"
html_short_title = project

html_logo = "https://raw.githubusercontent.com/python-discord/branding/main/logos/logo_full/logo_full.min.svg"
html_favicon = html_logo

static = Path("_static")
html_css_files = utils.get_recursive_file_uris(static, "*.css")
html_js_files = utils.get_recursive_file_uris(static, "*.js")

utils.build_api_doc()


def skip(*args) -> bool:
    """Things that should be skipped by the autodoc generation."""
    name = args[2]
    would_skip = args[4]

    if name in (
        "__weakref__",
    ):
        return True
    return would_skip


def post_build(_: Sphinx, exception: Exception) -> None:
    """Clean up and process files after the build has finished."""
    if exception:
        # Don't accidentally supress exceptions
        raise exception from None

    build_folder = PROJECT_ROOT / "docs" / "build"
    main_build = build_folder / "main"

    if main_build.exists() and not (build_folder / "index.html").exists():
        # We don't have an index in the root folder, add a redirect
        shutil.copy((main_build / "index_redirect.html"), (build_folder / "index.html"))
        shutil.copytree((main_build / "_static"), (build_folder / "_static"), dirs_exist_ok=True)
        (build_folder / ".nojekyll").touch(exist_ok=True)


def setup(app: Sphinx) -> None:
    """Add extra hook-based autodoc configuration."""
    app.connect("autodoc-skip-member", skip)
    app.connect("build-finished", post_build)
    app.add_role("literal-url", utils.emphasized_url)

    # Add a `breaking` role to the changelog
    releases.ISSUE_TYPES["breaking"] = "F50F10"  # This is the hex for a light red color
    releases.reorder_release_entries = utils.reorder_release_entries
    app.add_role("breaking", releases.issues_role)


ignored_modules = [
    "async_rediscache",
]

# nitpick raises warnings as errors. This regex tells nitpick to ignore any warnings that match this regex.
# This is a workaround for modules that do not have docs that can be linked out to.
nitpick_ignore_regex = [
    ("py:.*", "|".join([f".*{entry}.*" for entry in ignored_modules])),
]

# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for napoleon extension ------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_attr_annotations = True


# -- Options for extlinks extension ------------------------------------------
extlinks = {
    "repo-file": (f"{REPO_LINK}/blob/main/%s", "repo-file %s")
}


# -- Options for intersphinx extension ---------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "discord": ("https://discordpy.readthedocs.io/en/latest/", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "statsd": ("https://statsd.readthedocs.io/en/v3.3/", ("_static/statsd_additional_objects.inv", None)),
}


# -- Options for the linkcode extension --------------------------------------
linkcode_resolve = functools.partial(utils.linkcode_resolve, REPO_LINK)


# -- Options for releases extension ------------------------------------------
releases_github_path = REPO_LINK.removeprefix("https://github.com/")
releases_release_uri = f"{REPO_LINK}/releases/tag/v%s"


def _releases_setup(app: Sphinx) -> dict:
    """Wrap the default setup of releases to declare it as parallel-read safe."""
    _original_releases_setup(app)
    return {"parallel_read_safe": True}


_original_releases_setup = releases.setup
releases.setup = _releases_setup


# -- Options for the multiversion extension ----------------------------------
# Filter out older versions, and don't build branches other than main
# unless `BUILD_DOCS_FOR_HEAD` env variable is True.
smv_remote_whitelist = "origin"
smv_latest_version = "main"

smv_branch_whitelist = "main"
if os.getenv("BUILD_DOCS_FOR_HEAD", "False").lower() == "true":
    if not (branch := os.getenv("BRANCH_NAME")):
        with contextlib.suppress(git.InvalidGitRepositoryError):
            branch = git.Repo(PROJECT_ROOT).active_branch.name


    if branch:
        logger.info(f"Adding branch {branch} to build whitelist.")
        smv_branch_whitelist = f"main|{branch}"

smv_tag_whitelist = r"v(?!([0-6]\.)|(7\.[0-1]\.0))"  # Don't include any versions prior to v7.1.1
