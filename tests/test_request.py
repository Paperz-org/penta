from typing import Optional

import pytest
from pydantic import ConfigDict

from penta import Body, Cookie, Header, Router, Schema
from penta.dependencies.request import RequestDependency
from penta.testing import TestClient


class OptionalEmptySchema(Schema):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None


class ExtraForbidSchema(Schema):
    model_config = ConfigDict(extra="forbid")
    name: str
    metadata: Optional[OptionalEmptySchema] = None


router = Router()


@router.get("/headers1")
def headers1(request: RequestDependency, user_agent: str = Header(...)):
    return user_agent


@router.get("/headers2")
def headers2(request: RequestDependency, ua: str = Header(..., alias="User-Agent")):
    return ua


@router.get("/headers3")
def headers3(request: RequestDependency, content_length: int = Header(...)):
    return content_length


@router.get("/headers4")
def headers4(
    request: RequestDependency, c_len: int = Header(..., alias="Content-length")
):
    return c_len


@router.get("/headers5")
def headers5(request: RequestDependency, missing: int = Header(...)):
    return missing


@router.get("/cookies1")
def cookies1(request: RequestDependency, weapon: str = Cookie(...)):
    return weapon


@router.get("/cookies2")
def cookies2(request: RequestDependency, wpn: str = Cookie(..., alias="weapon")):
    return wpn


@router.post("/test-schema")
def schema(request: RequestDependency, payload: ExtraForbidSchema = Body(...)):
    return "ok"


client = TestClient(router)


@pytest.mark.parametrize(
    "path,expected_status,expected_response",
    [
        ("/headers1", 200, "Penta"),
        ("/headers2", 200, "Penta"),
        ("/headers3", 200, 10),
        ("/headers4", 200, 10),
        (
            "/headers5",
            422,
            {
                "detail": [
                    {
                        "type": "missing",
                        "loc": ["header", "missing"],
                        "msg": "Field required",
                    }
                ]
            },
        ),
        ("/cookies1", 200, "shuriken"),
        ("/cookies2", 200, "shuriken"),
    ],
)
def test_headers(path, expected_status, expected_response):
    response = client.get(
        path,
        headers={"User-Agent": "Penta", "Content-Length": "10"},
        COOKIES={"weapon": "shuriken"},
    )
    assert response.status_code == expected_status, response.content
    print(response.json())
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "path,json,expected_status,expected_response",
    [
        (
            "/test-schema",
            {"name": "test", "extra_name": "test2"},
            422,
            {
                "detail": [
                    {
                        "type": "extra_forbidden",
                        "loc": ["body", "payload", "extra_name"],
                        "msg": "Extra inputs are not permitted",
                    }
                ]
            },
        ),
        (
            "/test-schema",
            {"name": "test", "metadata": {"extra_name": "xxx"}},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "payload", "metadata", "extra_name"],
                        "msg": "Extra inputs are not permitted",
                        "type": "extra_forbidden",
                    }
                ]
            },
        ),
        (
            "/test-schema",
            {"name": "test", "metadata": "test2"},
            422,
            {
                "detail": [
                    {
                        "type": "model_attributes_type",
                        "loc": ["body", "payload", "metadata"],
                        "msg": "Input should be a valid dictionary or object to extract fields from",
                    }
                ]
            },
        ),
    ],
)
def test_pydantic_config(path, json, expected_status, expected_response):
    # test extra forbid
    response = client.post(path, json=json)
    assert response.json() == expected_response
    assert response.status_code == expected_status
