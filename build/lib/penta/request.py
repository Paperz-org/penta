from django.core.handlers.asgi import ASGIRequest
from django.http import QueryDict


class Request(ASGIRequest):
    """
    The request penta injects into the views.

    Django builds a `WSGIRequest`/`ASGIRequest`; penta re-tags it as a `Request` before
    running an operation, so a view can annotate its request parameter with this class.
    """

    def query_params(self) -> QueryDict:
        return self.GET
