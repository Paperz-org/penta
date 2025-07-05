import inspect
from typing import TYPE_CHECKING, Annotated, cast, get_args, get_origin

if TYPE_CHECKING:
    from penta.dependencies.depends import _Depends

from django.http import HttpRequest


class Parameter(inspect.Parameter):
    """
    A custom parameter class that extends inspect.Parameter to add Unchained-specific functionality.
    """

    @property
    def is_annotated(self) -> bool:
        """Check if the parameter is annotated."""
        return (
            hasattr(self.annotation, "__origin__")
            and get_origin(self.annotation) is Annotated
        )

    @property
    def is_request(self) -> bool:
        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, HttpRequest)
        return issubclass(self.annotation, HttpRequest)

    @property
    def is_header(self) -> bool:
        from penta.dependencies.header import Header

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, Header)
        return issubclass(self.annotation, Header)

    @property
    def is_query_params(self) -> bool:
        from penta.dependencies.query_params import QueryParams

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, QueryParams)
        return issubclass(self.annotation, QueryParams)

    @property
    def is_depends(self) -> bool:
        """Check if the parameter is a depends parameter."""
        from penta.dependencies.depends import _Depends

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, _Depends)
        return isinstance(self.default, _Depends)

    @property
    def dependency(self) -> "_Depends":
        if not self.is_depends:
            raise ValueError(
                "Parameter is not a Depends and don't have any dependency function associated"
            )

        from penta.dependencies.depends import _Depends

        depend: _Depends
        if self.is_annotated:
            _, depend = get_args(self.annotation)
        else:
            depend = self.default

        return depend

    @property
    def is_custom_depends(self) -> bool:
        """Check if the parameter is a custom depends parameter."""
        from penta.dependencies.custom import BaseCustom

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, BaseCustom)
        return issubclass(self.annotation, BaseCustom)

    @classmethod
    def from_parameter(cls, param: inspect.Parameter) -> "Parameter":
        """Create an UnchainedParam instance from an inspect.Parameter."""
        return cls(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=param.annotation,
        )


class Signature(inspect.Signature):
    parameters: dict[str, Parameter]

    def __init__(
        self,
        parameters=None,
        return_annotation=inspect.Signature.empty,
        __validate_parameters__=True,
    ) -> None:
        if parameters is not None:
            parameters = [
                Parameter.from_parameter(p) if not isinstance(p, Parameter) else p
                for p in parameters
            ]
        super().__init__(
            parameters=parameters,
            return_annotation=return_annotation,
            __validate_parameters__=__validate_parameters__,
        )

    @classmethod
    def from_callable(
        cls, obj, *, follow_wrapped=True, globals=None, locals=None, eval_str=False
    ):
        sig = super().from_callable(
            obj,
            follow_wrapped=follow_wrapped,
            globals=globals,
            locals=locals,
            eval_str=eval_str,
        )
        parameters: list[Parameter] = []
        for p in sig.parameters.values():
            if p.is_depends:
                parameters.extend(
                    cls.from_callable(p.dependency.dependency).parameters.values()
                )
            else:
                parameters.append(
                    Parameter.from_parameter(p) if not isinstance(p, Parameter) else p
                )

        parameters = _resolve_duplicate_parameters(parameters)

        return cls(parameters=parameters, return_annotation=sig.return_annotation)


def _resolve_duplicate_parameters(parameters: list[Parameter]) -> list[Parameter]:
    """
    Group parameters by name and ensure duplicates are identical.
    Returns a list of unique parameters.
    """

    parameter_groups: dict[str, list[Parameter]] = {}

    for parameter in parameters:
        parameter_groups.setdefault(parameter.name, []).append(parameter)

    resolved_parameters = []
    for name, variants in parameter_groups.items():
        if not variants:
            return True

        # TODO: need to be enhance, with taking account subtypes for example
        if len(variants) > 1 and not all(param == variants[0] for param in variants):
            raise ValueError(
                f"Duplicated parameter '{name}' with different signatures: {variants}"
            )
        resolved_parameters.append(variants[0])

    return resolved_parameters
