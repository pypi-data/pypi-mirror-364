"""
Configuration management module using Pydantic models and YAML files.

This module provides a base configuration class (`BaseConfig`) that loads configuration
sections from a YAML file into Pydantic models. Each section of the configuration is
represented as a subclass of `pydantic.BaseModel`, allowing for type validation and
structured configuration.

Classes:
    AppSettings: Pydantic model for application settings, including name and debug flag.
    BaseConfig: Base class for loading configuration sections from a YAML file.

Usage:
    - Define configuration sections as subclasses of `pydantic.BaseModel`.
    - Inherit from `BaseConfig` and add section attributes.
    - Call `BaseConfig.load()` to load configuration from the specified YAML file.

Attributes:
    path (str): Path to the YAML configuration file. Defaults to "config.yaml".
    app (AppSettings): Application settings section.

Methods:
    load(cls): Class method to load configuration from YAML and instantiate section models.

"""

import yaml
from typing import Type, TypeVar, Any
from pydantic import BaseModel as BaseSection
import os

SectionClass = TypeVar("T", bound="BaseConfig")


class AppSettings(BaseSection):
    name: str
    debug: bool = False


class BaseConfig:
    path: str = "config.yaml"

    app: AppSettings

    @classmethod
    def load(cls: Type[SectionClass], path: str = None) -> SectionClass:
        config_path = path or cls.path
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file '{cls.path}' not found.")
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
            if not issubclass(field_type, BaseSection):
                raise TypeError(
                    f"Config section '{field_name}' must be a subclass of BaseModel"
                )
            values[field_name] = field_type(**section)

        return cls(**values)

    def __init__(self, **sections: Any):
        for k, v in sections.items():
            setattr(self, k, v)
