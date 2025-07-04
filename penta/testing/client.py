from json import dumps as json_dumps
from json import loads as json_loads
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from unittest.mock import Mock
from urllib.parse import urljoin

from django.http import QueryDict, StreamingHttpResponse
from django.http.request import HttpHeaders, HttpRequest

from penta import Penta, Router
from penta.responses import PentaJSONEncoder
from penta.responses import Response as HttpResponse


def build_absolute_uri(location: Optional[str] = None) -> str:
    base = "http://testlocation/"

    if location:
        base = urljoin(base, location)

    return base


# TODO: this should be changed
# maybe add here urlconf object and add urls from here
class PentaClientBase:
    __test__ = False  # <- skip pytest

    def __init__(
        self,
        router_or_app: Union[Penta, Router],
        headers: Optional[Dict[str, str]] = None,
        COOKIES: Optional[Dict[str, str]] = None,
    ) -> None:
        self.headers = headers or {}
        self.cookies = COOKIES or {}
        self.router_or_app = router_or_app

    def get(
        self, path: str, data: Optional[Dict] = None, **request_params: Any
    ) -> "PentaResponse":
        return self.request("GET", path, data, **request_params)

    def post(
        self,
        path: str,
        data: Optional[Dict] = None,
        json: Any = None,
        **request_params: Any,
    ) -> "PentaResponse":
        return self.request("POST", path, data, json, **request_params)

    def patch(
        self,
        path: str,
        data: Optional[Dict] = None,
        json: Any = None,
        **request_params: Any,
    ) -> "PentaResponse":
        return self.request("PATCH", path, data, json, **request_params)

    def put(
        self,
        path: str,
        data: Optional[Dict] = None,
        json: Any = None,
        **request_params: Any,
    ) -> "PentaResponse":
        return self.request("PUT", path, data, json, **request_params)

    def delete(
        self,
        path: str,
        data: Optional[Dict] = None,
        json: Any = None,
        **request_params: Any,
    ) -> "PentaResponse":
        return self.request("DELETE", path, data, json, **request_params)

    def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        json: Any = None,
        **request_params: Any,
    ) -> "PentaResponse":
        if json is not None:
            request_params["body"] = json_dumps(json, cls=PentaJSONEncoder)
        if data is None:
            data = {}
        if self.headers or request_params.get("headers"):
            request_params["headers"] = {
                **self.headers,
                **request_params.get("headers", {}),
            }
        if self.cookies or request_params.get("COOKIES"):
            request_params["COOKIES"] = {
                **self.cookies,
                **request_params.get("COOKIES", {}),
            }
        func, request, kwargs = self._resolve(method, path, data, request_params)
        return self._call(func, request, kwargs)  # type: ignore

    @property
    def urls(self) -> List:
        if not hasattr(self, "_urls_cache"):
            self._urls_cache: List
            if isinstance(self.router_or_app, Penta):
                self._urls_cache = self.router_or_app.urls[0]
            else:
                api = Penta()
                self.router_or_app.set_api_instance(api)
                self._urls_cache = list(self.router_or_app.urls_paths(""))
        return self._urls_cache

    def _resolve(
        self, method: str, path: str, data: Dict, request_params: Any
    ) -> Tuple[Callable, Mock, Dict]:
        url_path = path.split("?")[0].lstrip("/")
        for url in self.urls:
            match = url.resolve(url_path)
            if match:
                request = self._build_request(method, path, data, request_params)
                return match.func, request, match.kwargs
        raise Exception(f'Cannot resolve "{path}"')

    def _build_request(
        self, method: str, path: str, data: Dict, request_params: Any
    ) -> Mock:
        request = Mock(spec=HttpRequest)
        request.method = method
        request.path = path
        request.body = ""
        request.COOKIES = {}
        request._dont_enforce_csrf_checks = True
        request.is_secure.return_value = False
        request.build_absolute_uri = build_absolute_uri

        request.auth = None
        request.user = Mock()
        if "user" not in request_params:
            request.user.is_authenticated = False
            request.user.is_staff = False
            request.user.is_superuser = False

        request.META = request_params.pop("META", {"REMOTE_ADDR": "127.0.0.1"})
        request.FILES = request_params.pop("FILES", {})

        request.META.update(
            {
                f"HTTP_{k.replace('-', '_')}": v
                for k, v in request_params.pop("headers", {}).items()
            }
        )

        request.headers = HttpHeaders(request.META)

        if isinstance(data, QueryDict):
            request.POST = data
        else:
            request.POST = QueryDict(mutable=True)

            if isinstance(data, (str, bytes)):
                request_params["body"] = data
            elif data:
                for k, v in data.items():
                    request.POST[k] = v

        if "?" in path:
            request.GET = QueryDict(path.split("?")[1])
        else:
            query_params = request_params.pop("query_params", None)
            if query_params:
                query_dict = QueryDict(mutable=True)
                for k, v in query_params.items():
                    if isinstance(v, list):
                        for item in v:
                            query_dict.appendlist(k, item)
                    else:
                        query_dict[k] = v
                request.GET = query_dict
            else:
                request.GET = QueryDict()

        for k, v in request_params.items():
            setattr(request, k, v)
        return request


class TestClient(PentaClientBase):
    def _call(self, func: Callable, request: Mock, kwargs: Dict) -> "PentaResponse":
        return PentaResponse(func(request, **kwargs))


class TestAsyncClient(PentaClientBase):
    async def _call(
        self, func: Callable, request: Mock, kwargs: Dict
    ) -> "PentaResponse":
        return PentaResponse(await func(request, **kwargs))


class PentaResponse:
    def __init__(self, http_response: Union[HttpResponse, StreamingHttpResponse]):
        self._response = http_response
        self.status_code = http_response.status_code
        self.streaming = http_response.streaming
        if self.streaming:
            self.content = b"".join(http_response.streaming_content)  # type: ignore
        else:
            self.content = http_response.content  # type: ignore[union-attr]
        self._data = None

    def json(self) -> Any:
        return json_loads(self.content)

    @property
    def data(self) -> Any:
        if self._data is None:  # Recomputes if json() is None but cheap then
            self._data = self.json()
        return self._data

    def __getitem__(self, key: str) -> Any:
        return self._response[key]

    def __getattr__(self, attr: str) -> Any:
        return getattr(self._response, attr)
