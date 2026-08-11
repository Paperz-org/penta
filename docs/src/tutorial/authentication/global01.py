from penta import Form, Penta
from penta.security import HttpBearer


class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token


api = Penta(auth=GlobalAuth())

# @api.get(...)
# def ...
# @api.post(...)
# def ...


@api.post("/token", auth=None)
def get_token(request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "giraffethinnknslong":
        return {"token": "supersecret"}
