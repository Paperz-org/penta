from unittest.mock import patch

from penta import Penta
from penta.testing import TestClient


def test_examples():
    api = Penta()

    with patch("builtins.api", api, create=True):
        import docs.src.tutorial.query.code01  # noqa: F401
        import docs.src.tutorial.query.code010  # noqa: F401
        import docs.src.tutorial.query.code02  # noqa: F401
        import docs.src.tutorial.query.code03  # noqa: F401

        client = TestClient(api)

        # Defaults
        assert client.get("/weapons").json() == [
            "Penta",
            "Shuriken",
            "Katana",
            "Kama",
            "Kunai",
            "Naginata",
            "Yari",
        ]

        assert client.get("/weapons?offset=0&limit=3").json() == [
            "Penta",
            "Shuriken",
            "Katana",
        ]

        assert client.get("/weapons?offset=2&limit=2").json() == [
            "Katana",
            "Kama",
        ]

        # Required/Optional

        assert client.get("/weapons/search?offset=1&q=k").json() == [
            "Katana",
            "Kama",
            "Kunai",
        ]

        # Coversion

        # fmt: off
        assert client.get("/example?b=1").json() == [None, True, None, None]
        assert client.get("/example?b=True").json() == [None, True, None, None]
        assert client.get("/example?b=true").json() == [None, True, None, None]
        assert client.get("/example?b=on").json() == [None, True, None, None]
        assert client.get("/example?b=yes").json() == [None, True, None, None]
        assert client.get("/example?b=0").json() == [None, False, None, None]
        assert client.get("/example?b=no").json() == [None, False, None, None]
        assert client.get("/example?b=false").json() == [None, False, None, None]
        assert client.get("/example?d=1577836800").json() == [None, None, "2020-01-01", None]
        assert client.get("/example?d=2020-01-01").json() == [None, None, "2020-01-01", None]
        # fmt: on

        # Schema

        assert client.get("/filter").json() == {
            "filters": {
                "limit": 100,
                "offset": None,
                "query": None,
                "category__in": None,
            }
        }
        assert client.get("/filter?limit=10").json() == {
            "filters": {
                "limit": 10,
                "offset": None,
                "query": None,
                "category__in": None,
            }
        }
        assert client.get("/filter?offset=10").json() == {
            "filters": {"limit": 100, "offset": 10, "query": None, "category__in": None}
        }
        assert client.get("/filter?query=10").json() == {
            "filters": {
                "limit": 100,
                "offset": None,
                "query": "10",
                "category__in": None,
            }
        }
        assert client.get("/filter?categories=a&categories=b").json() == {
            "filters": {
                "limit": 100,
                "offset": None,
                "query": None,
                "category__in": ["a", "b"],
            }
        }

        schema = api.get_openapi_schema(path_prefix="")
        params = schema["paths"]["/filter"]["get"]["parameters"]
        # print(params)
        assert params == [
            {
                "in": "query",
                "name": "limit",
                "schema": {"default": 100, "title": "Limit", "type": "integer"},
                "required": False,
            },
            {
                "in": "query",
                "name": "offset",
                "schema": {"title": "Offset", "type": "integer"},
                "required": False,
            },
            {
                "in": "query",
                "name": "query",
                "schema": {"title": "Query", "type": "string"},
                "required": False,
            },
            {
                "in": "query",
                "name": "categories",
                "schema": {
                    "items": {"type": "string"},
                    "title": "Categories",
                    "type": "array",
                },
                "required": False,
            },
        ]
