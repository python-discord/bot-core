"""Utilities for loading Discord extensions."""

import importlib
import inspect
import pkgutil
import types
from typing import NoReturn


def unqualify(name: str) -> str:
    """
    Return an unqualified name given a qualified module/package ``name``.

    Args:
        name: The module name to unqualify.

    Returns:
        The unqualified module name.
    """
    return name.rsplit(".", maxsplit=1)[-1]


def ignore_module(module: pkgutil.ModuleInfo) -> bool:
    """Return whether the module with name `name` should be ignored."""
    return any(name.startswith("_") for name in module.name.split("."))


def walk_extensions(module: types.ModuleType) -> frozenset[str]:
    """
    Return all extension names from the given module.

    Args:
        module (types.ModuleType): The module to look for extensions in.

    Returns:
        A set of strings that can be passed directly to :obj:`discord.ext.commands.Bot.load_extension`.
    """

    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)  # pragma: no cover

    modules = set()

    for module_info in pkgutil.walk_packages(module.__path__, f"{module.__name__}.", onerror=on_error):
        if ignore_module(module_info):
            # Ignore modules/packages that have a name starting with an underscore anywhere in their trees.
            continue

        if module_info.ispkg:
            imported = importlib.import_module(module_info.name)
            if not inspect.isfunction(getattr(imported, "setup", None)):
                # If it lacks a setup function, it's not an extension.
                continue

        modules.add(module_info.name)

    return frozenset(modules)
