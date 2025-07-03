from penta.security.apikey import APIKeyCookie, APIKeyHeader, APIKeyQuery
from penta.security.http import HttpBasicAuth, HttpBearer
from penta.security.session import SessionAuth, SessionAuthIsStaff, SessionAuthSuperUser

__all__ = [
    "APIKeyCookie",
    "APIKeyHeader",
    "APIKeyQuery",
    "HttpBasicAuth",
    "HttpBearer",
    "SessionAuth",
    "SessionAuthSuperUser",
    "django_auth",
    "django_auth_superuser",
    "django_auth_is_staff",
]

django_auth = SessionAuth()
django_auth_superuser = SessionAuthSuperUser()
django_auth_is_staff = SessionAuthIsStaff()
