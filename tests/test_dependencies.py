"""
Tests for the dependency injection (fast-depends) integration.

Views never receive the request as a positional argument: penta resolves it - like any
other dependency - from the signature of the view.
"""

from typing import List, Optional

import pytest
from django.http import HttpRequest
from typing_extensions import Annotated

from penta import Field, Penta, Router, Schema
from penta.context import get_request
from penta.dependencies import Depends, RequestDependency
from penta.dependencies.header import Header as HeaderDependency
from penta.dependencies.query_params import QueryParams as QueryParamsDependency
from penta.request import Request
from penta.testing import TestAsyncClient, TestClient

router = Router()


# --------------------------------------------------------------------------------------
# the request itself
# --------------------------------------------------------------------------------------


@router.get("/request/implicit")
def request_implicit(request):
    "django-ninja style: a parameter named `request` is the request"
    return {"path": request.path}


@router.get("/request/annotated")
def request_annotated(request: Request):
    return {"path": request.path}


@router.get("/request/http-request")
def request_http_request(incoming: HttpRequest):
    "any parameter annotated with an HttpRequest (subclass) receives the request"
    return {"path": incoming.path}


@router.get("/request/dependency")
def request_dependency(request: RequestDependency):
    return {"path": request.path}


@router.get("/request/with-params/{item_id}")
def request_with_params(request: Request, item_id: int, q: str = "default"):
    return {"method": request.method, "item_id": item_id, "q": q}


@router.get("/request/none")
def request_none():
    "the request is optional"
    return {"path": None}


# --------------------------------------------------------------------------------------
# user defined dependencies
# --------------------------------------------------------------------------------------


def get_token(request: RequestDependency) -> str:
    return request.headers.get("X-Token", "anonymous")


def get_user(token: Annotated[str, Depends(get_token)]) -> str:
    return f"user:{token}"


@router.get("/depends/annotated")
def depends_annotated(request, user: Annotated[str, Depends(get_user)], q: int = 1):
    return {"user": user, "q": q}


@router.get("/depends/default")
def depends_default(user=Depends(get_user)):
    return {"user": user}


class SomePayload(Schema):
    name: str


@router.post("/depends/with-body/{item_id}")
def depends_with_body(
    request: Request,
    item_id: int,
    payload: SomePayload,
    user: Annotated[str, Depends(get_user)],
):
    return {"item_id": item_id, "name": payload.name, "user": user}


# --------------------------------------------------------------------------------------
# penta provided dependencies
# --------------------------------------------------------------------------------------


@router.get("/header/required")
def header_required(token: Annotated[str, HeaderDependency("X-Token")]):
    return {"token": token}


@router.get("/header/typed")
def header_typed(version: Annotated[int, HeaderDependency("X-Version")]):
    return {"version": version, "type": type(version).__name__}


@router.get("/header/optional")
def header_optional(
    token: Annotated[
        Optional[str], HeaderDependency("X-Token", required=False)
    ] = "fallback",
):
    return {"token": token}


class HeadersSchema(Schema):
    x_token: str = Field(alias="X-Token")


@router.get("/header/model")
def header_model(headers: Annotated[HeadersSchema, HeaderDependency()]):
    return {"token": headers.x_token}


@router.get("/query/required")
def query_required(q: Annotated[str, QueryParamsDependency("q")]):
    return {"q": q}


@router.get("/query/typed")
def query_typed(page: Annotated[int, QueryParamsDependency()]):
    return {"page": page, "type": type(page).__name__}


@router.get("/query/list")
def query_list(ids: Annotated[List[int], QueryParamsDependency("id")]):
    return {"ids": ids}


@router.get("/query/optional")
def query_optional(
    q: Annotated[Optional[str], QueryParamsDependency(required=False)] = None,
):
    return {"q": q}


class FiltersSchema(Schema):
    search: str
    tags: List[str] = []


@router.get("/query/model")
def query_model(filters: Annotated[FiltersSchema, QueryParamsDependency()]):
    return {"search": filters.search, "tags": filters.tags}


api = Penta(urls_namespace="test_dependencies")
api.add_router("", router)
client = TestClient(api)


@pytest.mark.parametrize(
    "path",
    [
        "/request/implicit",
        "/request/annotated",
        "/request/http-request",
        "/request/dependency",
    ],
)
def test_request_is_injected(path):
    response = client.get(path)
    assert response.status_code == 200, response.content
    assert response.json() == {"path": path}


def test_request_with_params():
    response = client.get("/request/with-params/42?q=hello")
    assert response.status_code == 200, response.content
    assert response.json() == {"method": "GET", "item_id": 42, "q": "hello"}


def test_view_without_request():
    assert client.get("/request/none").json() == {"path": None}


def test_request_is_not_a_query_param():
    "the injected parameters must not leak into the OpenAPI schema"
    schema = api.get_openapi_schema(path_prefix="")
    assert schema["paths"]["/request/implicit"]["get"].get("parameters") == []
    assert schema["paths"]["/depends/annotated"]["get"]["parameters"] == [
        {
            "in": "query",
            "name": "q",
            "schema": {"default": 1, "title": "Q", "type": "integer"},
            "required": False,
        }
    ]


@pytest.mark.parametrize(
    "path, headers, expected",
    [
        ("/depends/annotated?q=5", {"X-Token": "abc"}, {"user": "user:abc", "q": 5}),
        ("/depends/annotated", {}, {"user": "user:anonymous", "q": 1}),
        ("/depends/default", {"X-Token": "abc"}, {"user": "user:abc"}),
    ],
)
def test_depends(path, headers, expected):
    response = client.get(path, headers=headers)
    assert response.status_code == 200, response.content
    assert response.json() == expected


def test_depends_with_penta_params():
    response = client.post(
        "/depends/with-body/1",
        json={"name": "penta"},
        headers={"X-Token": "abc"},
    )
    assert response.status_code == 200, response.content
    assert response.json() == {"item_id": 1, "name": "penta", "user": "user:abc"}


@pytest.mark.parametrize(
    "path, headers, expected_status, expected",
    [
        ("/header/required", {"X-Token": "abc"}, 200, {"token": "abc"}),
        (
            "/header/required",
            {},
            422,
            {
                "detail": [
                    {
                        "type": "missing",
                        "loc": ["header", "X-Token"],
                        "msg": "Field required",
                    }
                ]
            },
        ),
        ("/header/typed", {"X-Version": "3"}, 200, {"version": 3, "type": "int"}),
        (
            "/header/typed",
            {"X-Version": "not-a-number"},
            422,
            {
                "detail": [
                    {
                        "type": "int_parsing",
                        "loc": ["header", "X-Version"],
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                    }
                ]
            },
        ),
        ("/header/optional", {}, 200, {"token": "fallback"}),
        ("/header/optional", {"X-Token": "abc"}, 200, {"token": "abc"}),
        ("/header/model", {"X-Token": "abc"}, 200, {"token": "abc"}),
    ],
)
def test_header_dependency(path, headers, expected_status, expected):
    response = client.get(path, headers=headers)
    assert response.status_code == expected_status, response.content
    assert response.json() == expected


@pytest.mark.parametrize(
    "path, expected_status, expected",
    [
        ("/query/required?q=hello", 200, {"q": "hello"}),
        (
            "/query/required",
            422,
            {
                "detail": [
                    {"type": "missing", "loc": ["query", "q"], "msg": "Field required"}
                ]
            },
        ),
        ("/query/typed?page=3", 200, {"page": 3, "type": "int"}),
        ("/query/list?id=1&id=2", 200, {"ids": [1, 2]}),
        ("/query/optional", 200, {"q": None}),
        ("/query/optional?q=hello", 200, {"q": "hello"}),
        (
            "/query/model?search=penta&tags=a&tags=b",
            200,
            {"search": "penta", "tags": ["a", "b"]},
        ),
    ],
)
def test_query_params_dependency(path, expected_status, expected):
    response = client.get(path)
    assert response.status_code == expected_status, response.content
    assert response.json() == expected


def test_get_request_outside_of_a_request():
    with pytest.raises(RuntimeError):
        get_request()


def test_view_registered_twice():
    "penta must not alter the view: the same function can serve several operations"
    reused_router = Router()

    def view(request, q: int = 0):
        return {"q": q, "type": type(q).__name__}

    reused_router.add_api_operation("/first", ["GET"], view)
    reused_router.add_api_operation("/second", ["GET"], view)

    reused_client = TestClient(reused_router)
    for path in ("/first", "/second"):
        response = reused_client.get(f"{path}?q=3")
        assert response.status_code == 200, response.content
        assert response.json() == {"q": 3, "type": "int"}


def test_depends_signature_is_flattened():
    "`Depends.__signature__` exposes what the whole dependency tree needs"

    def inner(a: int, b: str = "b"):
        return a

    def outer(value: Annotated[int, Depends(inner)], c: float = 1.0):
        return value

    signature = Depends(outer).__signature__

    assert list(signature.parameters) == ["a", "value", "b", "c"]


# --------------------------------------------------------------------------------------
# async
# --------------------------------------------------------------------------------------

async_router = Router()


@async_router.get("/request")
async def async_request(request: Request):
    return {"path": request.path}


@async_router.get("/depends")
async def async_depends(request, user: Annotated[str, Depends(get_user)]):
    return {"user": user}


async_api = Penta(urls_namespace="test_dependencies_async")
async_api.add_router("", async_router)
async_client = TestAsyncClient(async_api)


@pytest.mark.asyncio
async def test_async_request_is_injected():
    response = await async_client.get("/request")
    assert response.status_code == 200, response.content
    assert response.json() == {"path": "/request"}


@pytest.mark.asyncio
async def test_async_depends():
    response = await async_client.get("/depends", headers={"X-Token": "abc"})
    assert response.status_code == 200, response.content
    assert response.json() == {"user": "user:abc"}
