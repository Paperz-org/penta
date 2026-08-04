from typing import Annotated, Any, List

from penta.compatibility.fast_depends import Dependency
from penta.signature.parser import Parameter, Signature

__all__: List[str] = [
    "create_signature_with_auto_dependencies",
    "custom_dependency_parameter",
    "dependency_parameter",
    "dependency_parameters",
    "is_request_parameter",
    "request_parameter",
    "resolve_dependencies",
]


def request_parameter(name: str, kind: Any = Parameter.KEYWORD_ONLY) -> Parameter:
    """
    Build a parameter resolved by the dependency injection with the current request.
    """
    # Imported here to avoid a circular import at module load time.
    from penta.dependencies.request import RequestDependency

    return Parameter(name=name, kind=kind, annotation=RequestDependency)


def is_request_parameter(param: Parameter) -> bool:
    """
    Whether the parameter should receive the current request.

    Both the explicit annotation (`request: Request` / `request: HttpRequest`) and the
    django-ninja convention (a parameter simply named `request`) are supported.
    """
    if param.is_request:
        return True
    return param.name == "request" and param.annotation is Parameter.empty


def dependency_parameter(param: Parameter) -> Parameter:
    """
    Bind a `Depends(...)` to the parameter it resolves.

    Whether it was declared as an annotation or as a default, the parameter ends up
    annotated with the dependency, so that everything is passed to the view by keyword.
    """
    annotation = param.annotation_type if param.is_annotated else Any
    if annotation is Parameter.empty:
        annotation = Any
    return Parameter(
        name=param.name,
        kind=Parameter.KEYWORD_ONLY,
        annotation=Annotated[annotation, resolve_dependencies(param.dependency)],
    )


def custom_dependency_parameter(param: Parameter) -> Parameter:
    """
    Bind a penta dependency (`Header`, `QueryParams`, ...) to the parameter it annotates.

    The parameter keeps the dependency but loses its type: the dependency validates the
    value it builds against the annotation itself, fast-depends must not do it again
    (re-validating an already built model would resolve its fields a second time).
    """
    dependency = param.custom_dependency
    dependency.configure(param)
    return Parameter(
        name=param.name,
        kind=Parameter.KEYWORD_ONLY,
        annotation=Annotated[object, resolve_dependencies(dependency)],
    )


def dependency_parameters(dependency: Dependency) -> List[Parameter]:
    """
    What a dependency, and everything it depends on, reads from the request.

    Those are the parameters penta has to parse and pass along - a dependency asks for
    a query parameter, a path parameter or a body the way a view does - as opposed to
    the ones resolved by the injection (the request, and the nested dependencies).
    """
    from penta.signature.utils import get_typed_signature

    parameters = []
    for param in get_typed_signature(dependency.dependency).parameters.values():
        if is_request_parameter(param) or param.is_response:
            continue
        if param.is_depends:
            if not param.is_custom_depends:
                parameters.extend(dependency_parameters(param.dependency))
            continue
        if param.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
            continue
        parameters.append(param)

    return parameters


def resolve_dependencies(dependency: Dependency) -> Dependency:
    """
    Make a dependency ask for what penta can resolve on its own.

    A dependency is a plain callable: it declares the request the way a view does
    (`def get_user(request: Request)`), and penta has to turn that parameter into a
    dependency too, down the whole tree. The callable itself is never touched: it is the
    user's, and the same one can serve several views.
    """
    from penta.dependencies.depends import _Depends
    from penta.signature.utils import get_typed_signature, wrap_with_signature

    signature = get_typed_signature(dependency.dependency)
    resolved_signature = create_signature_with_auto_dependencies(signature)
    if resolved_signature == signature:
        return dependency

    return _Depends(
        wrap_with_signature(dependency.dependency, resolved_signature),
        use_cache=dependency.use_cache,
        cast=dependency.cast,
    )


def create_signature_with_auto_dependencies(signature: Signature) -> Signature:
    """
    Create a new instance of the signature where the parameters penta knows how to
    resolve on its own (the request, and the dependencies needing it) are replaced by
    their dependency.
    """
    parameters = []

    for param in signature.parameters.values():
        if is_request_parameter(param):
            parameters.append(request_parameter(param.name, param.kind))
        elif param.is_depends:
            parameters.append(_with_resolved_dependency(param))
        else:
            parameters.append(param)

    return Signature(parameters)


def _with_resolved_dependency(param: Parameter) -> Parameter:
    """
    The same parameter, resolving what its dependency needs from penta.

    The dependency stays where it was declared - a default or an annotation - so that
    the parameter keeps its place in the signature it belongs to.
    """
    resolved = resolve_dependencies(param.dependency)
    if resolved is param.dependency:
        return param
    if isinstance(param.default, Dependency):
        return param.replace(default=resolved)
    return param.replace(annotation=Annotated[param.annotation_type, resolved])
