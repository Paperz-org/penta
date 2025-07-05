import inspect
from typing import Annotated, get_args, get_origin

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
        from penta.dependencies import Depends

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, Depends)
        return issubclass(self.annotation, Depends)

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
    ):
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
        parameters = [
            Parameter.from_parameter(p) if not isinstance(p, Parameter) else p
            for p in sig.parameters.values()
        ]
        return cls(parameters=parameters, return_annotation=sig.return_annotation)
