from typing import Generator, Generic, Optional, Tuple, TypeVar, get_origin

from django.http import QueryDict
from pydantic import BaseModel

from penta.dependencies.custom import BaseCustom
from penta.dependencies.request import RequestDependency

T = TypeVar("T")

ITERABLES = (list, tuple, set)


class QueryParams(BaseCustom[T], Generic[T]):
    """
    Inject a query parameter:

        @api.get("/")
        def view(page: Annotated[int, QueryParams()]):
            ...

    When the annotated type is a pydantic model, the whole query string is validated
    against it. A collection type collects every occurrence of the parameter
    (`?id=1&id=2`), any other type takes the last one.
    """

    source = "query"

    def __init__(self, param_name: Optional[str] = None, required: bool = True):
        super().__init__()
        self.param_name = param_name
        self.required = required

    def __call__(self, request: RequestDependency) -> Optional[T]:
        query_params = request.GET

        if self.is_model:
            return self.build(dict(self._model_values(query_params)))

        if self.param_name and self.param_name in query_params:
            if is_iterable_type(self.annotation_type):
                return self.build(query_params.getlist(self.param_name))
            return self.build(query_params[self.param_name])

        return self.missing()

    def _model_values(
        self, query_params: QueryDict
    ) -> Generator[Tuple[str, object], None, None]:
        """
        What the annotated model expects: Django keeps every occurrence of a parameter,
        so only its collection fields get the whole list.
        """
        model = self.annotation_type
        assert isinstance(model, type) and issubclass(model, BaseModel)

        for field_name, field in model.model_fields.items():
            name = field.alias or field_name
            if name not in query_params:
                continue
            if is_iterable_type(field.annotation):
                yield name, query_params.getlist(name)
            else:
                yield name, query_params[name]


def is_iterable_type(annotation: object) -> bool:
    """Whether the annotation collects several values (`List[int]`, `list`, ...)."""
    origin = get_origin(annotation) or annotation
    return isinstance(origin, type) and issubclass(origin, ITERABLES)
