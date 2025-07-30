from typing import Optional

from pytest import fixture

from enfig.base import BaseConfig


@fixture(scope="session")
def base_config_class(key_volume) -> type[BaseConfig]:
    class VolumeConfig(BaseConfig):
        VOLUME: int
        FIELD_WITH_DEFAULT_VALUE: str = "C"
        NON_MANDATORY_FIELD: str = None  # type: ignore
        TYPED_NON_MANDATORY_FIELD: Optional[str] = None

    return VolumeConfig


@fixture(scope="session")
def key_volume() -> str:
    return "VOLUME"
