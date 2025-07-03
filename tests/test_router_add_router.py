from penta import Penta, Router
from penta.testing import TestClient

router = Router()


@router.get("/")
def op(request):
    return True


def test_add_router_with_string_path():
    main_router = Router()
    main_router.add_router("sub", "tests.test_router_add_router.router")

    api = Penta()
    api.add_router("main", main_router)

    client = TestClient(api)

    assert client.get("/main/sub/").status_code == 200
