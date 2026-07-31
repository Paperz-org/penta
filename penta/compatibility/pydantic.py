"""
Compatibility layer over the versions of pydantic penta supports.
"""

from typing import Any, Callable

from pydantic_core import core_schema

__all__ = ["with_info_plain_validator_function"]

# pydantic 2.4 renamed `general_plain_validator_function`
_with_info_plain_validator_function: Callable[
    ..., core_schema.PlainValidatorFunctionSchema
] = getattr(
    core_schema,
    "with_info_plain_validator_function",
    getattr(core_schema, "general_plain_validator_function", None),
)


def with_info_plain_validator_function(
    function: Callable[..., Any],
) -> core_schema.PlainValidatorFunctionSchema:
    """A schema validating with `function`, which is given the validation info."""
    return _with_info_plain_validator_function(function)
