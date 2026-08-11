from contextvars import ContextVar
from typing import Optional

from penta.request import Request

request: ContextVar[Optional[Request]] = ContextVar("request", default=None)


def get_request() -> Request:
    """
    Return the request currently being handled.

    Used as a dependency, this is how a view (or any of its dependencies) receives the
    request. It is set by the operation before the view is called.
    """
    current_request = request.get()
    if current_request is None:
        raise RuntimeError(
            "No request in the current context: the request can only be injected "
            "while an operation is running."
        )
    return current_request
