from types import UnionType
from typing import Union

__all__ = ["UNION_TYPES"]

# both ways of building a union: `Union[str, int]` and, since python 3.10, `str | int`
UNION_TYPES = (Union, UnionType)
