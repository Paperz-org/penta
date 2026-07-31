import inspect
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    cast,
    get_args,
    get_origin,
)

if TYPE_CHECKING:
    from penta.dependencies.custom import BaseCustom

from django.http import HttpRequest, HttpResponse
from fast_depends.dependencies import model as fast_depends_model

TMetadata = TypeVar("TMetadata")


class Parameter(inspect.Parameter):
    """
    A custom parameter class that extends inspect.Parameter to add Penta-specific functionality.
    """

    @property
    def is_annotated(self) -> bool:
        """Check if the parameter is annotated."""
        return get_origin(self.annotation) is Annotated

    @property
    def annotation_type(self) -> Any:
        """The "real" annotation of the parameter (`Annotated[T, ...]` -> `T`)."""
        if self.is_annotated:
            return get_args(self.annotation)[0]
        return self.annotation

    @property
    def metadata(self) -> Tuple[Any, ...]:
        """The `Annotated` metadata of the parameter (empty when not annotated)."""
        if self.is_annotated:
            return get_args(self.annotation)[1:]
        return ()

    def _annotated_instance_of(
        self, metadata_type: Type[TMetadata]
    ) -> Optional[TMetadata]:
        """Return the first `Annotated` metadata being an instance of `metadata_type`."""
        for meta in self.metadata:
            if isinstance(meta, metadata_type):
                return meta
        return None

    def _is_subclass(self, *types: type) -> bool:
        annotation = self.annotation_type
        return inspect.isclass(annotation) and issubclass(annotation, types)

    @property
    def is_request(self) -> bool:
        """Check if the parameter expects the current request."""
        return self._is_subclass(HttpRequest)

    @property
    def is_response(self) -> bool:
        """Check if the parameter expects the (temporal) response."""
        return self._is_subclass(HttpResponse)

    @property
    def is_header(self) -> bool:
        from penta.dependencies.header import Header

        return (
            self._annotated_instance_of(Header) is not None
            or isinstance(self.default, Header)
            or self._is_subclass(Header)
        )

    @property
    def is_depends(self) -> bool:
        """Check if the parameter is resolved by the dependency injection."""
        return self._get_dependency() is not None

    def _get_dependency(self) -> Optional[fast_depends_model.Depends]:
        # `fast_depends_model.Depends` is the base class of penta's own `_Depends`,
        # so both `penta.dependencies.Depends` and `fast_depends.Depends` are detected.
        dependency = self._annotated_instance_of(fast_depends_model.Depends)
        if dependency is not None:
            return dependency
        if isinstance(self.default, fast_depends_model.Depends):
            return self.default
        return None

    @property
    def dependency(self) -> fast_depends_model.Depends:
        dependency = self._get_dependency()
        if dependency is None:
            raise ValueError(
                "Parameter is not a Depends and don't have any dependency function associated"
            )
        return dependency

    @property
    def is_custom_depends(self) -> bool:
        """Check if the parameter is resolved by a penta dependency."""
        from penta.dependencies.custom import BaseCustom

        return isinstance(self._get_dependency(), BaseCustom)

    @property
    def custom_dependency(self) -> "BaseCustom[object]":
        """The penta dependency (`Header`, `QueryParams`, ...) resolving the parameter."""
        from penta.dependencies.custom import BaseCustom

        dependency = self._get_dependency()
        if not isinstance(dependency, BaseCustom):
            raise ValueError(
                f"Parameter '{self.name}' is not resolved by a penta dependency"
            )
        return dependency

    @classmethod
    def from_parameter(cls, param: inspect.Parameter) -> "Parameter":
        """Create a penta Parameter instance from an inspect.Parameter."""
        if isinstance(param, cls):
            return param
        return cls(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=param.annotation,
        )


class Signature(inspect.Signature):
    @property
    def parameters(self) -> MappingProxyType[str, Parameter]:
        """The parameters of the signature, all of them penta `Parameter`s."""
        # every parameter is converted when the signature is built (see `__init__`)
        return cast(MappingProxyType[str, Parameter], super().parameters)

    def __init__(
        self,
        parameters: Optional[Sequence[inspect.Parameter]] = None,
        return_annotation: Any = inspect.Signature.empty,
        __validate_parameters__: bool = True,
    ) -> None:
        super().__init__(
            parameters=(
                [Parameter.from_parameter(p) for p in parameters]
                if parameters is not None
                else None
            ),
            return_annotation=return_annotation,
            __validate_parameters__=__validate_parameters__,
        )

    @classmethod
    def from_callable(
        cls,
        obj: Any,
        *,
        follow_wrapped: bool = True,
        globals: Any = None,
        locals: Any = None,
        eval_str: bool = False,
        flatten_dependencies: bool = False,
    ) -> "Signature":
        """
        Build the signature of `obj`.

        When `flatten_dependencies` is True, the parameters of the (nested) dependencies
        are inlined in the resulting signature instead of the `Depends` parameters
        themselves. This is only useful to introspect what a dependency tree needs;
        the runtime injection is done by fast-depends and needs the raw signature.
        """
        sig = super().from_callable(
            obj,
            follow_wrapped=follow_wrapped,
            globals=globals,
            locals=locals,
            eval_str=eval_str,
        )
        parameters: List[Parameter] = []
        for p in sig.parameters.values():
            param = Parameter.from_parameter(p)
            if flatten_dependencies and param.is_depends:
                parameters.extend(
                    cls.from_callable(
                        param.dependency.dependency,
                        flatten_dependencies=True,
                    ).parameters.values()
                )
            else:
                parameters.append(param)

        parameters = _resolve_duplicate_parameters(parameters)

        return cls(parameters=parameters, return_annotation=sig.return_annotation)


def _resolve_duplicate_parameters(parameters: List[Parameter]) -> List[Parameter]:
    """
    Group parameters by name and ensure duplicates are identical.
    Returns a list of unique parameters.
    """

    parameter_groups: Dict[str, List[Parameter]] = {}

    for parameter in parameters:
        parameter_groups.setdefault(parameter.name, []).append(parameter)

    resolved_parameters = []
    for name, variants in parameter_groups.items():
        # TODO: need to be enhance, with taking account subtypes for example
        if len(variants) > 1 and not all(param == variants[0] for param in variants):
            raise ValueError(
                f"Duplicated parameter '{name}' with different signatures: {variants}"
            )
        resolved_parameters.append(variants[0])

    return resolved_parameters
