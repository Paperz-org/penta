from django.urls import path

from penta import Penta

from .api import router

api_multi_param = Penta(version="1.0.1")
api_multi_param.add_router("", router)

urlpatterns = [
    path("api/", api_multi_param.urls),
]
