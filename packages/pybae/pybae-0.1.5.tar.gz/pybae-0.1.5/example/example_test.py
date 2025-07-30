import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pybae.config import BaseConfig, AppSettings, ConfigSection


class Config(BaseConfig):
    pass


cfg = Config.load()
print("Load built-in config")
print(f"{cfg.path=}")
print(f"{cfg.app.name=}")


class MyAppSettings(AppSettings):
    version: str = "1.0.0"


class Config(BaseConfig):
    app: MyAppSettings


cfg = Config.load()

print("\nLoad extension of built-in AppSettings")
print(f"{cfg.app.name=}")
print(f"{cfg.app.version=}")


class CustomSection(ConfigSection):
    custom_field: str = "example_value"


class Config(BaseConfig):
    custom: CustomSection


cfg = Config.load()
print("\nLoad custom section")
print(f"{cfg.custom.custom_field=}")
print(f"{cfg.app.name=}")
