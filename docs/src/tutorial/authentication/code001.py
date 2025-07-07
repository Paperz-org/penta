from penta import Penta
from penta.security import django_auth

api = Penta(csrf=True)


@api.get("/pets", auth=django_auth)
def pets(request):
    return f"Authenticated user {request.auth}"
