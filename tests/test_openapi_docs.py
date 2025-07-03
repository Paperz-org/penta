from django.conf import settings
from django.test import override_settings

from penta import Penta, Redoc, Swagger
from penta.testing import TestClient

NO_PENTA_INSTALLED_APPS = [i for i in settings.INSTALLED_APPS if i != "penta"]


def test_swagger():
    "Default engine is swagger"
    api = Penta()

    assert isinstance(api.docs, Swagger)

    client = TestClient(api)

    response = client.get("/docs")
    assert response.status_code == 200
    assert b"swagger-ui-init.js" in response.content

    # Testing without penta in INSTALLED_APPS
    @override_settings(INSTALLED_APPS=NO_PENTA_INSTALLED_APPS)
    def call_docs():
        response = client.get("/docs")
        assert response.status_code == 200
        assert b"https://cdn.jsdelivr.net/npm/swagger-ui-dist" in response.content

    call_docs()


def test_swagger_settings():
    api = Penta(docs=Swagger(settings={"persistAuthorization": True}))
    client = TestClient(api)
    response = client.get("/docs")
    assert response.status_code == 200
    assert b'"persistAuthorization": true' in response.content


def test_redoc():
    api = Penta(docs=Redoc())
    client = TestClient(api)

    response = client.get("/docs")
    assert response.status_code == 200
    assert b"redoc.standalone.js" in response.content

    # Testing without penta in INSTALLED_APPS
    @override_settings(INSTALLED_APPS=NO_PENTA_INSTALLED_APPS)
    def call_docs():
        response = client.get("/docs")
        assert response.status_code == 200
        assert (
            b"https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"
            in response.content
        )

    call_docs()


def test_redoc_settings():
    api = Penta(docs=Redoc(settings={"disableSearch": True}))
    client = TestClient(api)
    response = client.get("/docs")
    assert response.status_code == 200
    assert b'"disableSearch": true' in response.content
