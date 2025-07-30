from pytest import MonkeyPatch, mark, raises

from enfig import BaseConfig
from enfig.errors import (
    ConfigAttributeErrorType,
    InstantiationForbiddenError,
    ValidationError,
)


class SomeOtherMixinWhichDoesntRelateToEnvConfig:
    color = "red"


class TestConfig:
    def test_iter(self, monkeypatch: MonkeyPatch, key_volume: str, base_config_class):
        volume = 5
        monkeypatch.setenv(key_volume, str(volume))
        monkeypatch.setenv("color", "blue")

        class Config(SomeOtherMixinWhichDoesntRelateToEnvConfig, base_config_class):  # type: ignore
            TYPE: str

        items = [item for item in Config]  # type: ignore

        assert len(items) == 5
        assert Config.color == "red"

        assert items[0].name == "TYPE"
        assert items[0].value is None
        assert items[0].type is str

        assert items[1].name == "FIELD_WITH_DEFAULT_VALUE"
        assert items[1].value == "C"
        assert items[1].type is str

        assert items[2].name == "NON_MANDATORY_FIELD"
        assert items[2].value is None
        assert items[2].type is str

        assert items[3].name == "TYPED_NON_MANDATORY_FIELD"
        assert items[3].value is None
        assert items[3].type is str

        assert items[4].name == "VOLUME"
        assert items[4].value == volume
        assert items[4].type is int

    def test_get(self, monkeypatch: MonkeyPatch, key_volume, base_config_class):
        volume = 10
        monkeypatch.setenv(key_volume, str(volume))

        assert volume == base_config_class.VOLUME

    def test_constructor_is_forbidden(self):
        class Config(BaseConfig):
            pass

        with raises(InstantiationForbiddenError):
            Config()

    @mark.parametrize(
        ["v", "expected"],
        [
            ("1", True),
            ("YeS", True),
            ("y", True),
            ("TRUE", True),
            ("0", False),
            ("no", False),
            ("false", False),
            ("on", True),
            ("off", False),
        ],
    )
    def test_bool_field(self, monkeypatch, v: str, expected: bool):
        class Config(BaseConfig):
            DISABLE_JSON_LOGGING: bool

        monkeypatch.setenv("DISABLE_JSON_LOGGING", v)

        assert Config.DISABLE_JSON_LOGGING is expected

    def test_bool_filed_raises_error_if_invalid(self, monkeypatch: MonkeyPatch):
        class Config(BaseConfig):
            DISABLE_JSON_LOGGING: bool

        monkeypatch.setenv("DISABLE_JSON_LOGGING", "haha")

        with raises(ValidationError) as info:
            Config.validate()

        assert "DISABLE_JSON_LOGGING" in str(info.value)

    def test_validation_test_ok(self, key_volume, base_config_class, monkeypatch):
        volume = 10
        monkeypatch.setenv(key_volume, str(volume))

        base_config_class.validate()

    @mark.parametrize(
        ["volume", "error_type"],
        [
            (None, ConfigAttributeErrorType.NOT_SET),
            ("5.2", ConfigAttributeErrorType.INVALID_VALUE),
        ],
    )
    def test_validation_raises_error(
        self,
        error_type: ConfigAttributeErrorType,
        volume,
        key_volume,
        base_config_class,
        monkeypatch,
    ):
        if volume:
            monkeypatch.setenv(key_volume, str(volume))

        with raises(ValidationError) as exc_info:
            base_config_class.validate()

        validation_error = exc_info.value
        assert len(validation_error.errors) == 1
        attribute_error = validation_error.errors[0]

        assert attribute_error.error_type == error_type
        assert attribute_error.attribute_name == key_volume
        assert attribute_error.required_type is int
