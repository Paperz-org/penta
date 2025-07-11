from penta import NinjaAPI
from penta.security import django_auth

api = NinjaAPI(csrf=True)


@api.get("/pets", auth=django_auth)
def pets(request):
    return f"Authenticated user {request.auth}"
