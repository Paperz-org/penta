from penta.dependencies.request import RequestDependency
from penta.signature.parser import Parameter, Signature


def create_signature_with_auto_dependencies(signature: Signature) -> Signature:
    """
    Create a new instance of the signature with the auto dependencies (request, settings, app, state).
    """
    parameters = []

    def _parameter(param: Parameter, annotation: type) -> Parameter:
        return Parameter(name=param.name, kind=param.kind, default=param.default, annotation=annotation)
    

    for _, param in signature.parameters.items():

        if param.is_request:
            parameters.append(_parameter(param, RequestDependency))

        #elif param.is_header:
        #    parameters.append(_parameter(param, HeaderDependency))
        #elif param.is_query_params:
        #    parameters.append(_parameter(param, QueryParamsDependency))
        else:
            parameters.append(param)

    return Signature(parameters)
