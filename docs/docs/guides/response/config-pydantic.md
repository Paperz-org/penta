# Overriding Pydantic Config

There are many customizations available for a **Django Ninja `Schema`**, via the schema's
[Pydantic `Config` class](https://pydantic-docs.helpmanual.io/usage/model_config/). 

!!! info
    Under the hood **Django Ninja** uses [Pydantic Models](https://pydantic-docs.helpmanual.io/usage/models/)
    with all their power and benefits. The alias `Schema` was chosen to avoid confusion in code
    when using Django models, as Pydantic's model class is called Model by default, and conflicts with
    Django's Model class.

## Example Camel Case mode

One interesting `Config` attribute is [`alias_generator`](https://pydantic-docs.helpmanual.io/usage/model_config/#alias-generator).
Using Pydantic's example in **Django Ninja** can look something like:

```python hl_lines="12 13"
from ninja import Schema


def to_camel(string: str) -> str:
    words = string.split('_')
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

class CamelModelSchema(Schema):
    str_field_name: str
    float_field_name: float

    class Config(Schema.Config):
        alias_generator = to_camel
```

!!! note
    When overriding the schema's `Config`, it is necessary to inherit from the base `Config` class. 

Keep in mind that when you want modify output for field names (like camel case) - you need to set as well  `populate_by_name` and `by_alias`

```python hl_lines="6 9"
class UserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ["id", "email", "is_staff"]
        alias_generator = to_camel
        populate_by_name = True  # !!!!!! <--------


@api.get("/users", response=list[UserSchema], by_alias=True) # !!!!!! <-------- by_alias
def get_users(request):
    return User.objects.all()

```

results:

```JSON
[
  {
    "id": 1,
    "email": "tim@apple.com",
    "isStaff": true
  },
  {
    "id": 2,
    "email": "sarah@smith.com",
    "isStaff": false
  }
  ...
]

```

## Custom Config from Django Model

When using [`create_schema`](django-pydantic-create-schema.md#create_schema), the resulting
schema can be used to build another class with a custom config like:

```python hl_lines="10"
from django.contrib.auth.models import User
from penta.orm import create_schema


BaseUserSchema = create_schema(User)


class UserSchema(BaseUserSchema):

    class Config(BaseUserSchema.Config):
        ...
```
