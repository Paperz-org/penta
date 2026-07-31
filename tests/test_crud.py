"""
Tests for the CRUD router, which builds the views of a Django model on its own.

Those views take no `request` argument at all: everything they need is injected.
"""

import django
import pytest
from someapp.models import Category

from penta import Penta
from penta.crud import CRUDRouter
from penta.testing import TestAsyncClient

api = Penta(urls_namespace="test_crud")
crud_router = CRUDRouter(Category)
api.add_router(crud_router.path, crud_router.router)
client = TestAsyncClient(api)


def test_router_path():
    assert crud_router.path == "categorys"


def test_registered_operations():
    schema = api.get_openapi_schema(path_prefix="")
    assert sorted(schema["paths"]) == ["/categorys/", "/categorys/{id}"]
    assert sorted(schema["paths"]["/categorys/"]) == ["get", "post"]
    assert sorted(schema["paths"]["/categorys/{id}"]) == ["delete", "get", "patch"]

    # the pk is documented as a path param, and nothing else leaks in
    assert [
        param["name"]
        for param in schema["paths"]["/categorys/{id}"]["get"]["parameters"]
    ] == ["id"]


def test_partial_operations():
    read_only = CRUDRouter(Category, path="read-only", operations="R")
    read_only_api = Penta(urls_namespace="test_crud_read_only")
    read_only_api.add_router(read_only.path, read_only.router)

    schema = read_only_api.get_openapi_schema(path_prefix="")
    assert sorted(schema["paths"]) == ["/read-only/", "/read-only/{id}"]
    assert sorted(schema["paths"]["/read-only/"]) == ["get"]
    assert sorted(schema["paths"]["/read-only/{id}"]) == ["get"]


@pytest.mark.skipif(django.VERSION[:2] < (5, 0), reason="Requires Django 5.0+")
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_crud_flow():
    response = await client.post("/categorys/", json={"title": "cat1"})
    assert response.status_code == 201, response.content
    item_id = response.json()["id"]
    assert response.json()["title"] == "cat1"

    response = await client.get("/categorys/")
    assert response.status_code == 200, response.content
    assert response.json()["items"] == [{"id": item_id, "title": "cat1"}]

    response = await client.get(f"/categorys/{item_id}")
    assert response.status_code == 200, response.content
    assert response.json() == {"id": item_id, "title": "cat1"}

    response = await client.patch(f"/categorys/{item_id}", json={"title": "renamed"})
    assert response.status_code == 200, response.content
    assert response.json() == {"id": item_id, "title": "renamed"}

    response = await client.delete(f"/categorys/{item_id}")
    assert response.status_code == 204, response.content

    response = await client.get(f"/categorys/{item_id}")
    assert response.status_code == 404, response.content
