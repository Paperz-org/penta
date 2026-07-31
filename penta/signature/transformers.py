from typing import Annotated, Any

from penta.signature.parser import Parameter, Signature


def request_parameter(name: str, kind: Any = Parameter.KEYWORD_ONLY) -> Parameter:
    """
    Build a parameter resolved by the dependency injection with the current request.
    """
    # Imported here to avoid a circular import at module load time.
    from penta.dependencies.request import RequestDependency

    return Parameter(name=name, kind=kind, annotation=RequestDependency)


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
        annotation=Annotated[object, dependency],
    )


def is_request_parameter(param: Parameter) -> bool:
    """
    Whether the parameter should receive the current request.

    Both the explicit annotation (`request: Request` / `request: HttpRequest`) and the
    django-ninja convention (a parameter simply named `request`) are supported.
    """
    if param.is_request:
        return True
    return param.name == "request" and param.annotation is Parameter.empty


def create_signature_with_auto_dependencies(signature: Signature) -> Signature:
    """
    Create a new instance of the signature where the parameters penta knows how to
    resolve on its own (currently: the request) are replaced by their dependency.
    """
    parameters = []

    for param in signature.parameters.values():
        if is_request_parameter(param):
            parameters.append(request_parameter(param.name, param.kind))
        else:
            parameters.append(param)

    return Signature(parameters)
