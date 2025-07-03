import copy
import uuid

import pytest
from pydantic import BaseModel

from penta import Penta
from penta.constants import NOT_SET
from penta.signature.details import is_pydantic_model
from penta.signature.utils import UUIDStrConverter
from penta.testing import TestClient


def test_is_pydantic_model():
    class Model(BaseModel):
        x: int

    assert is_pydantic_model(Model)
    assert is_pydantic_model("instance") is False


def test_client():
    "covering everything in testclient (including invalid paths)"
    api = Penta()
    client = TestClient(api)
    with pytest.raises(Exception):  # noqa: B017
        client.get("/404")


def test_kwargs():
    api = Penta()

    @api.get("/")
    def operation(request, a: str, *args, **kwargs):
        pass

    schema = api.get_openapi_schema()
    params = schema["paths"]["/api/"]["get"]["parameters"]
    print(params)
    assert params == [  # Only `a` should be here, not kwargs
        {
            "in": "query",
            "name": "a",
            "schema": {"title": "A", "type": "string"},
            "required": True,
        }
    ]


def test_uuid_converter():
    conv = UUIDStrConverter()
    assert isinstance(conv.to_url(uuid.uuid4()), str)


def test_copy_not_set():
    assert id(NOT_SET) == id(copy.copy(NOT_SET))
    assert id(NOT_SET) == id(copy.deepcopy(NOT_SET))
