from contextvars import ContextVar

from penta.request import Request


request = ContextVar("request", default=None)


def get_request():
    return request.get() or Request()
