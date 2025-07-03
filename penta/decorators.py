from functools import partial
from typing import Any, Callable, Tuple

from penta.operation import Operation
from penta.types import TCallable
from penta.utils import contribute_operation_callback

# Since @api.method decorator is applied to function
# that is not always returns a HttpResponse object
# there is no way to apply some standard decorators form
# django stdlib or public plugins
#
# @decorate_view allows to apply any view decorator to Penta api operation
#
# @api.get("/some")
# @decorate_view(cache_page(60 * 15)) # <-------
# def some(request):
#     ...
#


def decorate_view(*decorators: Callable[..., Any]) -> Callable[[TCallable], TCallable]:
    def outer_wrapper(op_func: TCallable) -> TCallable:
        if hasattr(op_func, "_penta_operation"):
            # Means user used decorate_view on top of @api.method
            _apply_decorators(decorators, op_func._penta_operation)  # type: ignore
        else:
            # Means user used decorate_view after(bottom) of @api.method
            contribute_operation_callback(
                op_func, partial(_apply_decorators, decorators)
            )

        return op_func

    return outer_wrapper


def _apply_decorators(
    decorators: Tuple[Callable[..., Any]], operation: Operation
) -> None:
    for deco in decorators:
        operation.run = deco(operation.run)  # type: ignore
