"""Utils for manipulating functions."""

from __future__ import annotations

import functools
import inspect
import types
import typing

__all__ = [
    "GlobalNameConflictError",
    "command_wraps",
    "get_arg_value",
    "get_arg_value_wrapper",
    "get_bound_args",
    "update_wrapper_globals",
]


if typing.TYPE_CHECKING:
    from collections.abc import Callable, Sequence, Set as AbstractSet
    _P = typing.ParamSpec("_P")
    _R = typing.TypeVar("_R")

Argument = int | str
BoundArgs = typing.OrderedDict[str, typing.Any]
Decorator = typing.Callable[[typing.Callable], typing.Callable]
ArgValGetter = typing.Callable[[BoundArgs], typing.Any]


class GlobalNameConflictError(Exception):
    """Raised on a conflict between the globals used to resolve annotations of a wrapped function and its wrapper."""


def get_arg_value(name_or_pos: Argument, arguments: BoundArgs) -> typing.Any:
    """
    Return a value from `arguments` based on a name or position.

    Arguments:
        arguments: An ordered mapping of parameter names to argument values.
    Returns:
        Value from `arguments` based on a name or position.
    Raises:
        TypeError: `name_or_pos` isn't a str or int.
        ValueError: `name_or_pos` does not match any argument.
    """
    if isinstance(name_or_pos, int):
        # Convert arguments to a tuple to make them indexable.
        arg_values = tuple(arguments.items())
        arg_pos = name_or_pos

        try:
            _name, value = arg_values[arg_pos]
        except IndexError:
            raise ValueError(f"Argument position {arg_pos} is out of bounds.")
        else:
            return value
    elif isinstance(name_or_pos, str):
        arg_name = name_or_pos
        try:
            return arguments[arg_name]
        except KeyError:
            raise ValueError(f"Argument {arg_name!r} doesn't exist.")
    else:
        raise TypeError("'arg' must either be an int (positional index) or a str (keyword).")


def get_arg_value_wrapper(
    decorator_func: typing.Callable[[ArgValGetter], Decorator],
    name_or_pos: Argument,
    func: typing.Callable[[typing.Any], typing.Any] | None = None,
) -> Decorator:
    """
    Call `decorator_func` with the value of the arg at the given name/position.

    Arguments:
        decorator_func: A function that must accept a callable as a parameter to which it will pass a mapping of
            parameter names to argument values of the function it's decorating.
        name_or_pos: The name/position of the arg to get the value from.
        func: An optional callable which will return a new value given the argument's value.

    Returns:
        The decorator returned by `decorator_func`.
    """
    def wrapper(args: BoundArgs) -> typing.Any:
        value = get_arg_value(name_or_pos, args)
        if func:
            value = func(value)
        return value

    return decorator_func(wrapper)


def get_bound_args(func: typing.Callable, args: tuple, kwargs: dict[str, typing.Any]) -> BoundArgs:
    """
    Bind `args` and `kwargs` to `func` and return a mapping of parameter names to argument values.

    Default parameter values are also set.

    Args:
        args: The arguments to bind to ``func``
        kwargs: The keyword arguments to bind to ``func``
        func: The function to bind ``args`` and ``kwargs`` to
    Returns:
        A mapping of parameter names to argument values.
    """
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    return bound_args.arguments


def update_wrapper_globals(
    wrapper: Callable[_P, _R],
    wrapped: Callable[_P, _R],
    *,
    ignored_conflict_names: AbstractSet[str] = frozenset(),
) -> Callable[_P, _R]:
    r"""
    Create a copy of ``wrapper``\, the copy's globals are updated with ``wrapped``\'s globals.

    For forwardrefs in command annotations, discord.py uses the ``__global__`` attribute of the function
    to resolve their values. This breaks for decorators that replace the function because they have
    their own globals.

    .. warning::
        This function captures the state of ``wrapped``\'s module's globals when it's called;
        changes won't be reflected in the new function's globals.

    Args:
        wrapper: The function to wrap.
        wrapped: The function to wrap with.
        ignored_conflict_names: A set of names to ignore if a conflict between them is found.

    Raises:
        :exc:`GlobalNameConflictError`:
            If ``wrapper`` and ``wrapped`` share a global name that's also used in ``wrapped``\'s typehints,
            and is not in ``ignored_conflict_names``.
    """
    wrapped = typing.cast(types.FunctionType, wrapped)
    wrapper = typing.cast(types.FunctionType, wrapper)

    annotation_global_names = (
        ann.split(".", maxsplit=1)[0] for ann in wrapped.__annotations__.values() if isinstance(ann, str)
    )
    # Conflicting globals from both functions' modules that are also used in the wrapper and in wrapped's annotations.
    shared_globals = (
        set(wrapper.__code__.co_names)
        & set(annotation_global_names)
        & set(wrapped.__globals__)
        & set(wrapper.__globals__)
        - ignored_conflict_names
    )
    if shared_globals:
        raise GlobalNameConflictError(
            f"wrapper and the wrapped function share the following "
            f"global names used by annotations: {', '.join(shared_globals)}. Resolve the conflicts or add "
            f"the name to the `ignored_conflict_names` set to suppress this error if this is intentional."
        )

    new_globals = wrapper.__globals__.copy()
    new_globals.update((k, v) for k, v in wrapped.__globals__.items() if k not in wrapper.__code__.co_names)
    return types.FunctionType(
        code=wrapper.__code__,
        globals=new_globals,
        name=wrapper.__name__,
        argdefs=wrapper.__defaults__,
        closure=wrapper.__closure__,
    )


def command_wraps(
    wrapped: Callable[_P, _R],
    assigned: Sequence[str] = functools.WRAPPER_ASSIGNMENTS,
    updated: Sequence[str] = functools.WRAPPER_UPDATES,
    *,
    ignored_conflict_names: AbstractSet[str] = frozenset(),
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    r"""
    Update the decorated function to look like ``wrapped``\, and update globals for discord.py forwardref evaluation.

    See :func:`update_wrapper_globals` for more details on how the globals are updated.

    Args:
        wrapped: The function to wrap with.
        assigned: Sequence of attribute names that are directly assigned from ``wrapped`` to ``wrapper``.
        updated: Sequence of attribute names that are ``.update``d on ``wrapper`` from the attributes on ``wrapped``.
        ignored_conflict_names: A set of names to ignore if a conflict between them is found.

    Returns:
        A decorator that behaves like :func:`functools.wraps`,
        with the wrapper replaced with the function :func:`update_wrapper_globals` returned.
    """
    def decorator(wrapper: Callable[_P, _R]) -> Callable[_P, _R]:
        return functools.update_wrapper(
            update_wrapper_globals(wrapper, wrapped, ignored_conflict_names=ignored_conflict_names),
            wrapped,
            assigned,
            updated,
        )

    return decorator
