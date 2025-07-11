from unittest.mock import patch

from penta import Penta
from penta.testing import TestClient


def test_examples():
    api = Penta()

    with patch("builtins.api", api, create=True):
        import docs.src.tutorial.path.code01  # noqa: F401

        client = TestClient(api)

        response = client.get("/items/123")
        assert response.json() == {"item_id": "123"}

    api = Penta()

    with patch("builtins.api", api, create=True):
        import docs.src.tutorial.path.code010  # noqa: F401
        import docs.src.tutorial.path.code02  # noqa: F401

        client = TestClient(api)

        response = client.get("/items/123")
        assert response.json() == {"item_id": 123}

        response = client.get("/events/2020/1/1")
        assert response.json() == {"date": "2020-01-01"}
        schema = api.get_openapi_schema(path_prefix="")
        events_params = schema["paths"]["/events/{year}/{month}/{day}"]["get"][
            "parameters"
        ]
        assert events_params == [
            {
                "in": "path",
                "name": "year",
                "schema": {"title": "Year", "type": "integer"},
                "required": True,
            },
            {
                "in": "path",
                "name": "month",
                "schema": {"title": "Month", "type": "integer"},
                "required": True,
            },
            {
                "in": "path",
                "name": "day",
                "schema": {"title": "Day", "type": "integer"},
                "required": True,
            },
        ]
