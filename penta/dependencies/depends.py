from inspect import _empty, signature
from typing import Any, Callable, TypeVar

from fast_depends.dependencies import model
from typing_extensions import ParamSpec

from penta.signature import Signature
from penta.signature.parser import Parameter

T = TypeVar("T")
P = ParamSpec("P")


class _Depends(model.Depends):
    def __init__(
        self,
        dependency: Callable[P, T],
        *,
        use_cache: bool = True,
        cast: bool = True,
    ) -> None:
        super().__init__(dependency, use_cache=use_cache, cast=cast)

    @property
    def __signature__(self) -> Signature:
        """
        Build a flattened signature that includes parameters from the main dependency
        and all nested dependencies, handling duplicates and proper parameter ordering.
        """
        dependency_signature = Signature.from_callable(self.dependency)
        parameters: list[Parameter] = []

        # Extract all parameters from main dependency and nested dependencies
        for param in dependency_signature.parameters.values():
            if param.is_depends:
                parameters.extend(signature(param.dependency).parameters.values())
            parameters.append(param)

        # Validate and resolve duplicate parameters
        resolved_parameters = self._resolve_duplicate_parameters(parameters)

        parameters_without_default = [
            param for param in resolved_parameters if param.default is _empty
        ]
        parameters_with_default = [
            param for param in resolved_parameters if param.default is not _empty
        ]

        # Sort each group by parameter kind for consistent ordering
        parameters_without_default.sort(key=lambda x: x.kind)
        parameters_with_default.sort(key=lambda x: x.kind)

        parameters = parameters_without_default + parameters_with_default
        # Create the final signature
        try:
            return dependency_signature.replace(
                parameters=parameters,
                return_annotation=dependency_signature.return_annotation,
            )
        except ValueError as e:
            # Provide more context for signature creation errors
            raise ValueError(
                f"Failed to create signature with parameters {[p.name for p in parameters]}: {e}"
            ) from e

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.dependency(*args, **kwargs)


def Depends(
    dependency: Callable[P, T],
    *,
    use_cache: bool = True,
    cast: bool = True,
) -> _Depends:
    return _Depends(
        dependency=dependency,
        use_cache=use_cache,
        cast=cast,
    )
