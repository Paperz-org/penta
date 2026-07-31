import pydantic

PYDANTIC_VERSION = tuple(map(int, pydantic.VERSION.split(".")[:2]))


def pydantic_ref_fix(data: dict):
    "In pydantic 1.7 $ref was changed to allOf: [{'$ref': ...}] but in 2.9 it was changed back"
    if PYDANTIC_VERSION < (1, 7) or PYDANTIC_VERSION >= (2, 9):
        return data

    result = data.copy()
    if "$ref" in data:
        result["allOf"] = [{"$ref": result.pop("$ref")}]
    return result
