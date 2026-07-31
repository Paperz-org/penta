import asyncio
import inspect
import re
from typing import Any, Callable, ForwardRef, List, Protocol, Set, TypeVar, cast

from django.urls import register_converter
from django.urls.converters import UUIDConverter
from pydantic._internal._typing_extra import eval_type_lenient as evaluate_forwardref

from penta.signature.parser import Parameter, Signature
from penta.types import DictStrAny

__all__ = [
    "get_typed_signature",
    "get_typed_annotation",
    "make_forwardref",
    "get_path_param_names",
    "is_async",
    "with_signature",
]

TCallable = TypeVar("TCallable", bound=Callable[..., Any])


class _HasSignature(Protocol):
    """A callable `inspect.signature()` reports a signature of its own for."""

    __signature__: inspect.Signature


def with_signature(func: TCallable, signature: inspect.Signature) -> TCallable:
    """
    Make `func` report `signature` instead of the one it was defined with.

    This is the documented hook `inspect.signature()` (and everything built on it, from
    penta to fast-depends) reads, which is how a view built at runtime advertises the
    parameters it really takes.
    """
    cast(_HasSignature, func).__signature__ = signature
    return func


def get_typed_signature(call: Callable[..., Any]) -> Signature:
    "Finds call signature and resolves all forwardrefs"
    signature = Signature.from_callable(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    return Signature(typed_params)


def get_typed_annotation(param: inspect.Parameter, globalns: DictStrAny) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = make_forwardref(annotation, globalns)
    return annotation


def make_forwardref(annotation: str, globalns: DictStrAny) -> Any:
    # NOTE: in future versions of pydantic, the import may be changed to:
    # from pydantic._internal._typing_extra import try_eval_type
    # usage:
    # result, _ = try_eval_type(forward_ref, globalns, globalns)
    forward_ref = ForwardRef(annotation)
    return evaluate_forwardref(forward_ref, globalns, globalns)


def get_path_param_names(path: str) -> Set[str]:
    """turns path string like /foo/{var}/path/{int:another}/end to set {'var', 'another'}"""
    return {item.strip("{}").split(":")[-1] for item in re.findall("{[^}]*}", path)}


def is_async(callable: Callable[..., Any]) -> bool:
    return asyncio.iscoroutinefunction(callable)


def has_kwargs(func: Callable[..., Any]) -> bool:
    for param in inspect.signature(func).parameters.values():
        if param.kind == param.VAR_KEYWORD:
            return True
    return False


def get_args_names(func: Callable[..., Any]) -> List[str]:
    "returns list of function argument names"
    return list(inspect.signature(func).parameters.keys())


class UUIDStrConverter(UUIDConverter):
    """Return a path converted UUID as a str instead of the standard UUID"""

    def to_python(self, value: str) -> str:  # type: ignore
        return value  # return string value instead of UUID


register_converter(UUIDStrConverter, "uuidstr")
