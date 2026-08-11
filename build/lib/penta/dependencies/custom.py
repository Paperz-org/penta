from copy import copy
from typing import (
    TYPE_CHECKING,
    Generic,
    List,
    Optional,
    TypeVar,
    cast,
    get_args,
    get_origin,
)

import pydantic
from pydantic import BaseModel, TypeAdapter

from penta.compatibility.util import UNION_TYPES
from penta.dependencies.depends import _Depends
from penta.errors import ValidationError
from penta.types import DictStrAny

if TYPE_CHECKING:
    from penta.signature.parser import Parameter  # pragma: no cover

T = TypeVar("T")


class BaseCustom(_Depends[..., Optional[T]], Generic[T]):
    """
    Base class for the dependencies penta resolves itself out of the request
    (headers, query string, ...) instead of delegating to a user provided callable.

    A subclass locates its raw value in the request and hands it to `build()`; the type
    it has to build is the annotation of the view parameter, which is only known once
    the view signature is parsed (see `configure()`).
    """

    #: where the value comes from, as reported in the errors ("header", "query", ...)
    source: str = "dependency"

    def __init__(
        self,
        *,
        use_cache: bool = True,
        cast: bool = False,
    ) -> None:
        # `cast` is off by default: the value is validated by `build()` against the
        # annotation of the view parameter, fast-depends must not validate it again.
        # The bound method carries the signature fast-depends resolves: everything the
        # subclass needs (the request, ...) is injected into `__call__`.
        super().__init__(self.__call__, use_cache=use_cache, cast=cast)
        self.param_name: Optional[str] = None
        self.required = True
        self.annotation_type: object = str
        self.default: Optional[object] = None
        self._adapter: TypeAdapter[object] = TypeAdapter(str)

    def configured_for(self, param: "Parameter") -> "BaseCustom[T]":
        """
        A copy of the dependency, bound to the view parameter it annotates.

        A copy, because the same instance is shared by every view using the annotation
        it is declared in: `Token = Annotated[str, Header("X-Token")]` is one `Header`,
        and each parameter it annotates has a name and a type of its own.
        """
        bound = copy(self)
        if bound.param_name is None:
            bound.param_name = param.name
        bound.annotation_type = _concrete_type(param.annotation_type)
        bound._adapter = TypeAdapter(bound.annotation_type)
        if param.default is not param.empty:
            bound.default = param.default
        # what fast-depends calls is the bound method of the copy, not of the original
        bound.dependency = bound.__call__
        return bound

    @property
    def is_model(self) -> bool:
        """Whether the view expects the whole source to be validated as a model."""
        return isinstance(self.annotation_type, type) and issubclass(
            self.annotation_type, BaseModel
        )

    def build(self, raw_value: object) -> T:
        """
        Validate a raw value coming from the request against the type the view expects.
        """
        try:
            return cast(T, self._adapter.validate_python(raw_value))
        except pydantic.ValidationError as e:
            raise ValidationError(self._errors(e)) from e

    def missing(self) -> Optional[T]:
        """
        The value to inject when the request carries nothing for this dependency.
        """
        if self.default is not None:
            return cast(T, self.default)
        if self.required:
            raise ValidationError([
                {
                    "type": "missing",
                    "loc": [self.source, self.param_name],
                    "msg": "Field required",
                }
            ])
        return None

    def _errors(self, error: pydantic.ValidationError) -> List[DictStrAny]:
        "The pydantic errors, located where the value was read from"
        return [
            {
                "type": details["type"],
                "loc": [self.source, self.param_name, *details["loc"]],
                "msg": details["msg"],
            }
            for details in error.errors()
        ]


def _concrete_type(annotation: object) -> object:
    """
    The type used to build the value of the dependency.

    `Optional[X]` (and more generally `Union[X, None]`) is resolved to `X`: `None` is
    what the dependency returns when it has no value, not something it builds.
    """
    if get_origin(annotation) in UNION_TYPES:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return args[0]
    return annotation
