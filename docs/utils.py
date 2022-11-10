"""Utilities used in generating docs."""

import ast
import importlib.util
import inspect
import os
import subprocess
import types
import typing
from pathlib import Path

import docstring_parser
import docutils.nodes
import docutils.parsers.rst.states
import git
import releases
import sphinx.util.logging

logger = sphinx.util.logging.getLogger(__name__)


def get_build_root() -> Path:
    """Get the project root folder for the current build."""
    root = Path.cwd()
    if root.name == "docs":
        root = root.parent
    return root


def is_attribute(module: types.ModuleType, parameter: str) -> bool:
    """Returns true if `parameter` is an attribute of `module`."""
    docs = docstring_parser.parse(inspect.getdoc(module), docstring_parser.DocstringStyle.GOOGLE)
    for param in docs.params:
        # The docstring_parser library can mis-parse arguments like `arg (:obj:`str`)` as `arg (`
        # which would create a false-negative below, so we just strip away the extra parenthesis.
        if param.args[0] == "attribute" and param.arg_name.rstrip(" (") == parameter:
            return True

    return False


def linkcode_resolve(repo_link: str, domain: str, info: dict[str, str]) -> typing.Optional[str]:
    """
    Function called by linkcode to get the URL for a given resource.

    See for more details:
    https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html#confval-linkcode_resolve
    """
    if domain != "py":
        raise Exception("Unknown domain passed to linkcode function.")

    symbol_name = info["fullname"]

    build_root = get_build_root()

    # Import the package to find files
    origin = build_root / info["module"].replace(".", "/")
    search_locations = []

    if origin.is_dir():
        search_locations.append(origin.absolute().as_posix())
        origin = origin / "__init__.py"
    else:
        origin = Path(origin.absolute().as_posix() + ".py")
        if not origin.exists():
            raise Exception(f"Could not find `{info['module']}` as a package or file.")

    # We can't use a normal import (importlib.import_module), because the module can conflict with another copy
    # in multiversion builds. We load the module from the file location instead
    spec = importlib.util.spec_from_file_location(info["module"], origin, submodule_search_locations=search_locations)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    symbol = [module]
    for name in symbol_name.split("."):
        try:
            symbol.append(getattr(symbol[-1], name))
        except AttributeError as e:
            # This could be caused by trying to link a class attribute
            if is_attribute(symbol[-1], name):
                break
            else:
                raise e

        symbol_name = name

    try:
        lines, start = inspect.getsourcelines(symbol[-1])
        module = inspect.getmodule(symbol[-1])
        end = start + len(lines)
    except TypeError:
        # Find variables by parsing the ast
        source = ast.parse(inspect.getsource(symbol[-2]))
        while isinstance(source.body[0], ast.ClassDef):
            source = source.body[0]

        pos = _global_assign_pos(source, symbol_name)
        if pos is None:
            raise Exception(f"Could not find symbol `{symbol_name}` in {module.__name__}.")
        else:
            start, end = pos
        _, offset = inspect.getsourcelines(symbol[-2])
        if offset != 0:
            offset -= 1
        start += offset
        end += offset

    file = Path(inspect.getfile(module)).relative_to(build_root).as_posix()

    try:
        sha = git.Repo(build_root).commit().hexsha
    except git.InvalidGitRepositoryError:
        # We are building a historical version, no git data available
        sha = build_root.name

    url = f"{repo_link}/blob/{sha}/{file}#L{start}"
    if end != start:
        url += f"-L{end}"

    return url


class NodeWithBody(typing.Protocol):
    """An AST node with the body attribute."""

    body: list[ast.AST]


def _global_assign_pos(ast_: NodeWithBody, name: str) -> typing.Union[tuple[int, int], None]:
    """
    Find the first instance where the `name` global is defined in `ast_`.

    Check top-level assignments and assignments nested in top-level if blocks.
    """
    for ast_obj in ast_.body:
        if isinstance(ast_obj, ast.Assign):
            names = []
            for target in ast_obj.targets:
                if isinstance(target, ast.Tuple):
                    names.extend([name.id for name in target.elts if isinstance(name, ast.Name)])
                else:
                    if isinstance(target, ast.Name):
                        names.append(target.id)

            if name in names:
                return ast_obj.lineno, ast_obj.end_lineno

        elif isinstance(ast_obj, ast.If):
            pos_in_if = _global_assign_pos(ast_obj, name)
            if pos_in_if is not None:
                return pos_in_if


def cleanup() -> None:
    """Remove unneeded autogenerated doc files, and clean up others."""
    included = __get_included()

    for file in (get_build_root() / "docs" / "output").iterdir():
        if file.name in ("pydis_core.rst", "pydis_core.exts.rst", "pydis_core.utils.rst") and file.name in included:
            content = file.read_text(encoding="utf-8").splitlines(keepends=True)

            # Rename the extension to be less wordy
            # Example: pydis_core.exts -> pydis_core Exts
            title = content[0].split()[0].strip().replace("pydis_core.", "").replace(".", " ").title()
            title = f"{title}\n{'=' * len(title)}\n\n"
            content = title, *content[3:]

            file.write_text("".join(content), encoding="utf-8")

        elif file.name in included:
            # Clean up the submodule name so it's just the name without the top level module name
            # example: `pydis_core.regex module` -> `regex`
            lines = file.read_text(encoding="utf-8").splitlines(keepends=True)
            lines[0] = lines[0].replace("module", "").strip().split(".")[-1] + "\n"
            file.write_text("".join(lines))

        else:
            # These are files that have not been explicitly included in the docs via __all__
            file.unlink()
            continue

        # Take the opportunity to configure autodoc
        content = file.read_text(encoding="utf-8").replace("undoc-members", "special-members")
        file.write_text(content, encoding="utf-8")


def build_api_doc() -> None:
    """Generate auto-module directives using apidoc."""
    cmd = os.getenv("APIDOC_COMMAND") or "sphinx-apidoc -o docs/output pydis_core -feM"
    cmd = cmd.split()

    build_root = get_build_root()
    output_folder = build_root / cmd[cmd.index("-o") + 1]

    if output_folder.exists():
        logger.info(f"Skipping api-doc for {output_folder.as_posix()} as it already exists.")
        return

    result = subprocess.run(cmd, cwd=build_root, stdout=subprocess.PIPE, check=True, env=os.environ)
    logger.debug("api-doc Output:\n" + result.stdout.decode(encoding="utf-8") + "\n")

    cleanup()


def __get_included() -> set[str]:
    """Get a list of files that should be included in the final build."""

    def get_all_from_module(module_name: str) -> set[str]:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            return set()
        _modules = {module.__name__ + ".rst"}

        if hasattr(module, "__all__"):
            for sub_module in module.__all__:
                _modules.update(get_all_from_module(sub_module))

        return _modules

    return get_all_from_module("pydis_core")


def reorder_release_entries(release_list: list[releases.Release]) -> None:
    """
    Sort `releases` based on `release.type`.

    This is meant to be used as an override for `releases.reorder_release_entries` to support
    custom types.
    """
    order = {"breaking": 0, "feature": 1, "bug": 2, "support": 3}
    for release in release_list:
        release["entries"].sort(key=lambda entry: order[entry.type])


def emphasized_url(
    name: str, rawtext: str, text: str, lineno: int, inliner: docutils.parsers.rst.states.Inliner, *__
) -> tuple[list, list]:
    """
    Sphinx role to add hyperlinked literals.

    ReST: :literal-url:`Google <https://google.com>`
    Markdown equivalent: [`Google`](https://google.com)

    Refer to https://docutils.sourceforge.io/docs/howto/rst-roles.html for details on the input and output.
    """
    arguments = text.rsplit(maxsplit=1)
    if len(arguments) != 2:
        message = inliner.reporter.error(
            f"`{name}` expects a message and a URL, formatted as: :{name}:`message <url>`",
            line=lineno
        )
        problem = inliner.problematic(text, rawtext, message)
        return [problem], [message]

    message, url = arguments
    url: str = url[1:-1]  # Remove the angled brackets off the start and end

    literal = docutils.nodes.literal(rawtext, message)
    return [docutils.nodes.reference(rawtext, "", literal, refuri=url)], []


def get_recursive_file_uris(folder: Path, match_pattern: str) -> list[str]:
    """Get the URI of any file relative to folder which matches the `match_pattern` regex."""
    return [file.relative_to(folder).as_posix() for file in folder.rglob(match_pattern)]
