"""
Compatibility layer over the versions of pydantic penta supports.
"""

from typing import Any, Callable, cast

from pydantic_core import core_schema

__all__ = ["with_info_plain_validator_function"]

# pydantic 2.4 renamed `general_plain_validator_function`, and the name that does not
# exist cannot be referenced directly: whichever is there has that signature.
_ValidatorFunctionFactory = Callable[..., core_schema.PlainValidatorFunctionSchema]
_factory = cast(
    _ValidatorFunctionFactory,
    getattr(
        core_schema,
        "with_info_plain_validator_function",
        getattr(core_schema, "general_plain_validator_function", None),
    ),
)


def with_info_plain_validator_function(
    function: Callable[..., Any],
) -> core_schema.PlainValidatorFunctionSchema:
    """A schema validating with `function`, which is given the validation info."""
    return _factory(function)
