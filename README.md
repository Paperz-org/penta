<p align="center">
  <a href="https://paperz-org.github.io/penta/"><img src="./docs/docs/img/penta_logo.png" width="200"></a>
</p>
<p align="center">
    <em>Fast to learn, fast to code, fast to run</em>
</p>

![Test](https://github.com/Paperz-org/penta/actions/workflows/test_full.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/Paperz-org/penta)
[![PyPI version](https://badge.fury.io/py/penta.svg)](https://badge.fury.io/py/penta)
[![Downloads](https://static.pepy.tech/personalized-badge/penta?period=month&units=international_system&left_color=black&right_color=brightgreen&left_text=downloads/month)](https://pepy.tech/project/penta)

# Penta - Fast Django REST Framework

<<<<<<< Updated upstream
# Penta - Fast Django REST Framework

**Penta** is a web framework for building APIs with **Django** and Python 3.10+ **type hints**.
=======
**Penta** is a fork of [Django Ninja](https://github.com/vitalik/django-ninja) web framework for building APIs with **Django** and Python 3.6+ **type hints** focused on opinionated integrations.

Please have a look at the original [Django Ninja](https://github.com/vitalik/django-ninja) and leave a star as the job done by the original author is great.
>>>>>>> Stashed changes

**Key features:**

- **Easy**: Designed to be easy to use and intuitive.
- **FAST execution**: Very high performance thanks to **<a href="https://pydantic-docs.helpmanual.io" target="_blank">Pydantic</a>** and **<a href="/docs/docs/guides/async-support.md">async support</a>**.
- **Fast to code**: Type hints and automatic docs lets you focus only on business logic.
- **Standards-based**: Based on the open standards for APIs: **OpenAPI** (previously known as Swagger) and **JSON Schema**.
- **Django friendly**: (obviously) has good integration with the Django core and ORM.

<<<<<<< Updated upstream
  - **Easy**: Designed to be easy to use and intuitive.
  - **FAST execution**: Very high performance thanks to **<a href="https://pydantic-docs.helpmanual.io" target="_blank">Pydantic</a>** and **<a href="/docs/docs/guides/async-support.md">async support</a>**.
  - **Fast to code**: Type hints and automatic docs lets you focus only on business logic.
  - **Dependency injection**
  - **Standards-based**: Based on the open standards for APIs: **OpenAPI** (previously known as Swagger) and **JSON Schema**.
  - **Django friendly**: (obviously) has good integration with the Django core and ORM.



**Documentation**: As Penta is a fork of django ninja, you can start [here](https://django-ninja.dev). We will create a dedicated documentation for Penta soon !
=======
**Documentation**: https://paperz-org.github.io/penta/
>>>>>>> Stashed changes

---

## Installation

```
pip install penta
```

## Usage

In your django project next to urls.py create new `api.py` file:

```Python
from penta import Penta

api = Penta()


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}
```

Now go to `urls.py` and add the following:

```Python hl_lines="3 7"
...
from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),  # <---------- !
]
```

**That's it !**

Now you've just created an API that:

- receives an HTTP GET request at `/api/add`
- takes, validates and type-casts GET parameters `a` and `b`
- decodes the result to JSON
- generates an OpenAPI schema for defined operation

### Interactive API docs

Now go to <a href="http://127.0.0.1:8000/api/docs" target="_blank">http://127.0.0.1:8000/api/docs</a>

You will see the automatic interactive API documentation (provided by <a href="https://github.com/swagger-api/swagger-ui" target="_blank">Swagger UI</a> or <a href="https://github.com/Redocly/redoc" target="_blank">Redoc</a>):

![Swagger UI](docs/docs/img/index-swagger-ui.png)

## What next?

- Read the full documentation here - https://paperz-org.github.io/unchained/
