from enum import Enum

from enfig.bool_type import _Bool


class EnfigError(Exception):
    pass


class InstantiationForbiddenError(EnfigError):
    pass


class ConfigAttributeErrorType(str, Enum):
    NOT_SET = "Not set"
    INVALID_VALUE = "Invalid value"


class ConfigAttributeError(EnfigError):
    __slots__ = ["error_type", "attribute_name", "required_type"]

    def __init__(
        self,
        error_type: ConfigAttributeErrorType,
        attribute_name: str,
        required_type: type,
    ):
        self.error_type = error_type
        self.attribute_name = attribute_name
        self.required_type = required_type

    def __repr__(self):
        return f"{self.attribute_name}: {self.error_type}"

    def __str__(self) -> str:
        required_type = bool if self.required_type is _Bool else self.required_type
        return (
            f"{self.attribute_name}: {self.error_type}, "
            f"required type: `{required_type.__name__}`"
        )


class ValidationError(EnfigError):
    __slots__ = ["errors"]

    def __init__(self, errors: list[ConfigAttributeError]):
        self.errors = errors
