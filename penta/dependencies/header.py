from typing import Generic, Optional, TypeVar

from penta.dependencies.custom import BaseCustom
from penta.dependencies.request import RequestDependency

T = TypeVar("T")


class Header(BaseCustom[T], Generic[T]):
    """
    Inject a request header:

        @api.get("/")
        def view(token: Annotated[str, Header("X-Token")]):
            ...

    When the annotated type is a pydantic model, the whole headers mapping is validated
    against it.
    """

    source = "header"

    def __init__(self, param_name: Optional[str] = None, required: bool = True):
        super().__init__()
        self.param_name = param_name
        self.required = required

    def __call__(self, request: RequestDependency) -> Optional[T]:
        headers = request.headers

        if self.is_model:
            return self.build(headers)

        if self.param_name and self.param_name in headers:
            return self.build(headers[self.param_name])

        return self.missing()
