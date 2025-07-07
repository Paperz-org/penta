# Versioning

## Different API version numbers

With **Penta** it's easy to run multiple API versions from a single Django project.

All you have to do is create two or more Penta instances with different `version` arguments:

**api_v1.py**:

```python hl_lines="4"
from penta import Penta


api = Penta(version='1.0.0')

@api.get('/hello')
def hello(request):
    return {'message': 'Hello from V1'}

```

api\_**v2**.py:

```python hl_lines="4"
from penta import Penta


api = Penta(version='2.0.0')

@api.get('/hello')
def hello(request):
    return {'message': 'Hello from V2'}
```

and then in **urls.py**:

```python hl_lines="8 9"
...
from api_v1 import api as api_v1
from api_v2 import api as api_v2


urlpatterns = [
    ...
    path('api/v1/', api_v1.urls),
    path('api/v2/', api_v2.urls),
]

```

Now you can go to different OpenAPI docs pages for each version:

- http://127.0.0.1/api/**v1**/docs
- http://127.0.0.1/api/**v2**/docs

## Different business logic

In the same way, you can define a different API for different components or areas:

```python hl_lines="4 7"
...


api = Penta(auth=token_auth, urls_namespace='public_api')
...

api_private = Penta(auth=session_auth, urls_namespace='private_api')
...


urlpatterns = [
    ...
    path('api/', api.urls),
    path('internal-api/', api_private.urls),
]

```

!!! note
If you use different **Penta** instances, you need to define different `version`s or different `urls_namespace`s.
