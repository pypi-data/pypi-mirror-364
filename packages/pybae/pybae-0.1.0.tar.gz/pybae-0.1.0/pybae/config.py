import yaml
from typing import Type, TypeVar, Any
from pydantic import BaseModel as ConfigSection

SectionClass = TypeVar("T", bound="BaseConfig")


class AppSettings(ConfigSection):
    name: str
    debug: bool = False


class BaseConfig:
    path: str = "config.yaml"

    app: AppSettings

    @classmethod
    def load(cls: Type[SectionClass]) -> SectionClass:
        with open(cls.path, "r") as f:
            raw_data = yaml.safe_load(f)

        values: dict[str, Any] = {}

        annotations = {}
        for base_cls in reversed(cls.__mro__):
            if hasattr(base_cls, "__annotations__"):
                annotations.update(base_cls.__annotations__)

        for field_name, field_type in annotations.items():
            if field_name == "path":
                continue
            section = raw_data.get(field_name, {})
            if not issubclass(field_type, ConfigSection):
                raise TypeError(
                    f"Config section '{field_name}' must be a subclass of BaseModel"
                )
            values[field_name] = field_type(**section)

        return cls(**values)

    def __init__(self, **sections: Any):
        for k, v in sections.items():
            setattr(self, k, v)
