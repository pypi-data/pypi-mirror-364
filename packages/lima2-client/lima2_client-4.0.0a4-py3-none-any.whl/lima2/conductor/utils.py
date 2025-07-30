# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Utility functions"""

from typing import Any, Callable, TypeVar

import jsonschema
from jsonschema import validators
from jsonschema.protocols import Validator

from lima2.common.types import pixel_type_to_np_dtype

DecoratedFunc = TypeVar("DecoratedFunc", bound=Callable[..., Any])

ValidationError = jsonschema.ValidationError
"""Type alias for `jsonschema.ValidationError`."""


def validate(instance: dict[str, Any], schema: dict[str, Any]) -> None:
    """Lima2 param validation.

    Raises a ValidationError if `instance` fails the schema validation.

    Since JSON schema draft 6, a value is considered an "integer" if its
    fractional part is zero [1]. This means for example that 2.0 is considered
    an integer. Since we don't want floats to pass the validation where ints are
    expected, this function overrides this flexibility with a stricter type check.

    [1] https://json-schema.org/draft-06/json-schema-release-notes
    """

    def is_strict_int(_: Validator, value: Any) -> bool:
        return type(value) is int

    base_validator: type[Validator] = validators.validator_for(schema)
    strict_checker = base_validator.TYPE_CHECKER.redefine("integer", is_strict_int)
    strict_validator = validators.extend(base_validator, type_checker=strict_checker)

    jsonschema.validate(instance, schema, cls=strict_validator)


def frame_info_to_shape_dtype(frame_info: dict[str, Any]) -> dict[str, Any]:
    return dict(
        shape=(
            frame_info["nb_channels"],
            frame_info["dimensions"]["y"],
            frame_info["dimensions"]["x"],
        ),
        dtype=pixel_type_to_np_dtype[frame_info["pixel_type"]],
    )
