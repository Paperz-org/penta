from enum import Enum
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import Any, FrozenSet

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from pydantic import BaseModel
from pydantic_core import Url

__all__ = [
    "PentaJSONEncoder",
    "Response",
    "codes_1xx",
    "codes_2xx",
    "codes_3xx",
    "codes_4xx",
    "codes_5xx",
]


class PentaJSONEncoder(DjangoJSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, BaseModel):
            return o.model_dump()
        if isinstance(o, Url):
            return str(o)
        if isinstance(o, (IPv4Address, IPv4Network, IPv6Address, IPv6Network)):
            return str(o)
        if isinstance(o, Enum):
            return str(o)
        return super().default(o)


class Response(JsonResponse):
    def __init__(self, data: Any, **kwargs: Any) -> None:
        super().__init__(data, encoder=PentaJSONEncoder, safe=False, **kwargs)


def resp_codes(from_code: int, to_code: int) -> FrozenSet[int]:
    return frozenset(range(from_code, to_code + 1))


# most common http status codes
codes_1xx = resp_codes(100, 101)
codes_2xx = resp_codes(200, 206)
codes_3xx = resp_codes(300, 308)
codes_4xx = resp_codes(400, 412) | frozenset({416, 418, 425, 429, 451})
codes_5xx = resp_codes(500, 504)
