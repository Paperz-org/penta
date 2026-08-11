from inspect import Parameter as InspectParameter
from typing import Callable, Generic, List, TypeVar

from typing_extensions import ParamSpec

from penta.compatibility.fast_depends import Dependency, dependency_options
from penta.signature.parser import Parameter, Signature, _resolve_duplicate_parameters

T = TypeVar("T")
P = ParamSpec("P")


class _Depends(Dependency, Generic[P, T]):
    """
    A dependency, parameterized by the signature and the return type of the callable it
    resolves: `Depends(get_user)` is a `_Depends[[Request], User]`.
    """

    dependency: Callable[P, T]

    def __init__(
        self,
        dependency: Callable[P, T],
        *,
        use_cache: bool = True,
        cast: bool = True,
    ) -> None:
        super().__init__(
            dependency, **dependency_options(use_cache=use_cache, cast=cast)
        )

    @property
    def __signature__(self) -> Signature:
        """
        Build a flattened signature that includes parameters from the main dependency
        and all nested dependencies, handling duplicates and proper parameter ordering.
        """
        dependency_signature = Signature.from_callable(self.dependency)
        parameters: List[Parameter] = []

        # Extract all parameters from main dependency and nested dependencies
        for param in dependency_signature.parameters.values():
            if param.is_depends:
                parameters.extend(
                    Signature.from_callable(
                        param.dependency.dependency, flatten_dependencies=True
                    ).parameters.values()
                )
            parameters.append(param)

        # Validate and resolve duplicate parameters
        resolved_parameters = _resolve_duplicate_parameters(parameters)

        parameters_without_default = [
            param
            for param in resolved_parameters
            if param.default is InspectParameter.empty
        ]
        parameters_with_default = [
            param
            for param in resolved_parameters
            if param.default is not InspectParameter.empty
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
) -> _Depends[P, T]:
    return _Depends(
        dependency=dependency,
        use_cache=use_cache,
        cast=cast,
    )
