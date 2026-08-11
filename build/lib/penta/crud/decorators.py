"""
Decorators adapting the views a ViewSet builds to the model it serves.

Renaming parameters is used for example to give the `pk_field` parameter the real pk
field name, so that the path and the swagger documentation use it.
"""

import inspect
from functools import wraps
from typing import Any, Callable, TypeVar

from penta.signature.utils import with_signature

TCallable = TypeVar("TCallable", bound=Callable[..., object])


def bind_annotations(func: TCallable, **annotations: type) -> TCallable:
    """
    Give the parameters of a view the concrete types penta builds its schemas from.

    A ViewSet is written against the type variables of its class (`payload:
    CreateSchemaType`); the schemas they stand for are only known once the ViewSet is
    instantiated, so the views are annotated with them here, at build time.
    """
    func.__annotations__.update(annotations)
    return func


def _rename_parameter(
    rename_map: dict[str, str], *, is_async: bool
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Common implementation for parameter renaming decorators.

    Args:
        rename_map (dict[str, str]): Dictionary where key is the old parameter name and value is the new name.
        is_async (bool): Whether the decorator is for async functions.

    Returns:
        Callable: Decorator function.

    Raises:
        ValueError: If more than one parameter is being renamed or if the parameter doesn't exist.
    """
    if len(rename_map) != 1:
        msg = "Only one parameter can be renamed at a time"
        raise ValueError(msg)

    # Get the old name and new name from the rename map
    old_name, new_name = rename_map.popitem()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Get the current signature
        sig = inspect.signature(func)

        # Validate that the parameter exists
        if old_name not in sig.parameters:
            msg = f"Parameter '{old_name}' not found in function signature"
            raise ValueError(msg)

        # Modify the function's signature
        new_params = [
            param.replace(name=new_name) if param.name == old_name else param
            for param in sig.parameters.values()
        ]
        new_sig = sig.replace(parameters=new_params)

        with_signature(func, new_sig)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:  # type: ignore
            # Rename the keyword argument if present
            if new_name in kwargs:
                kwargs[old_name] = kwargs.pop(new_name)
            return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:  # type: ignore
            # Rename the keyword argument if present
            if new_name in kwargs:
                kwargs[old_name] = kwargs.pop(new_name)
            return await func(*args, **kwargs)

        return async_wrapper if is_async else wrapper

    return decorator


def async_rename_parameter(
    **rename_map: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to rename a single parameter in an async function's signature and adjust kwargs when called.

    Args:
        **rename_map: Single keyword argument mapping old parameter name to new name.

    Returns:
        Callable: Decorator function.

    Raises:
        ValueError: If more than one parameter is being renamed or if the parameter doesn't exist.
    """
    return _rename_parameter(rename_map, is_async=True)


def rename_parameter(
    **rename_map: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to rename a single parameter in a synchronous function's signature and adjust kwargs when called.

    Args:
        **rename_map: Single keyword argument mapping old parameter name to new name.

    Returns:
        Callable: Decorator function.

    Raises:
        ValueError: If more than one parameter is being renamed or if the parameter doesn't exist.
    """
    return _rename_parameter(rename_map, is_async=False)
