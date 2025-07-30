from collections.abc import Iterator
from os import getenv
from typing import Any, get_args

from enfig.bool_type import _Bool
from enfig.errors import (
    ConfigAttributeError,
    ConfigAttributeErrorType,
    InstantiationForbiddenError,
    ValidationError,
)


class _Variable:
    def __init__(self, type_: type = str, default_value=...):
        type_args = get_args(type_)
        type_ = type_args[0] if type_args else type_
        self._type = _Bool if type_ is bool else type_
        self._default_value = default_value

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, obj, type_=None):
        return self.value

    @property
    def default_value(self) -> Any:
        return self._default_value

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def value(self) -> Any:
        if (value := getenv(self._name)) is not None:
            casted_val = self._type(value)
            return bool(casted_val) if self._type is _Bool else casted_val

        if self._default_value is not ...:
            return self._default_value

        return None


class _ConfigMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        for key, type_ in namespace.get("__annotations__", {}).items():
            namespace[key] = _Variable(type_, namespace.get(key, ...))

        for base in bases:
            if not isinstance(base, _ConfigMeta):
                continue

            for variable in base:
                namespace[variable.name] = variable

        return super().__new__(mcs, name, bases, namespace)

    def __iter__(cls) -> Iterator[_Variable]:
        return (
            value for value in cls.__dict__.values() if isinstance(value, _Variable)
        )


class BaseConfig(metaclass=_ConfigMeta):
    def __new__(cls, *args, **kwargs):
        raise InstantiationForbiddenError

    @classmethod
    def validate(cls):
        errors = []

        for item in cls:
            try:
                _validate_attribute(item)
            except ConfigAttributeError as error:
                errors.append(error)

        if errors:
            raise ValidationError(errors)


def _validate_attribute(item: _Variable):
    try:
        value = item.value
    except ValueError:
        raise ConfigAttributeError(
            error_type=ConfigAttributeErrorType.INVALID_VALUE,
            attribute_name=item.name,
            required_type=item.type,
        )

    if item.default_value is ... and value is None:
        raise ConfigAttributeError(
            error_type=ConfigAttributeErrorType.NOT_SET,
            attribute_name=item.name,
            required_type=item.type,
        )
