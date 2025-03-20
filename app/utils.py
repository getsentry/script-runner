import functools
import yaml
import os
from types import ModuleType
from enum import Enum
import importlib
import inspect
from typing import Any, Literal
from dataclasses import dataclass
import hashlib
import jsonschema
import json
from pathlib import Path


def get_module_exports(module: ModuleType) -> list[str]:
    exports = module.__all__ if hasattr(module, "__all__") else dir(module)
    return [
        name
        for name in exports
        if not name.startswith("_") and callable(getattr(module, name, None))
    ]


class Mode(Enum):
    region = "region"
    main = "main"
    combined = "combined"


@dataclass(frozen=True)
class Region:
    name: str
    url: str


@dataclass(frozen=True)
class FunctionParameter:
    name: str
    default: str | None
    enumValues: list[str] | None

@dataclass(frozen=True)
class Function:
    name: str
    source: str
    docstring: str
    parameters: list[FunctionParameter]

    @functools.cached_property
    def checksum(self) -> str:
        return hashlib.md5(self.source.encode()).hexdigest()


@dataclass(frozen=True)
class FunctionGroup:
    group: str
    module: str
    functions: list[Function]
    iap_principals: list[str]


@dataclass(frozen=True)
class CommonFields:
    groups: dict[str, FunctionGroup]

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        groups = {
            g: load_group(val["python_module"], g, val["iap_principals"]) for (g, val) in data["groups"].items()
        }

        return cls(
            groups=groups
        )

@dataclass(frozen=True)
class RegionFields:
    name: str
    configs: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            name=data["name"],
            configs=data["configs"]
        )

@dataclass(frozen=True)
class MainFields:
    regions: list[Region]

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            regions=[Region(name=r["name"], url=r["url"]) for r in data["regions"]],
        )

@dataclass(frozen=True)
class RegionConfig(CommonFields):
    region: RegionFields

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        common = CommonFields.from_dict(data)

        return cls(
            groups=common.groups,
            region=RegionFields.from_dict(data["region"])
        )


@dataclass(frozen=True)
class MainConfig(CommonFields):
    main: MainFields

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        common = CommonFields.from_dict(data)

        return cls(
            groups=common.groups,
            main=MainFields.from_dict(data["main"])

        )

@dataclass(frozen=True)
class CombinedConfig(CommonFields):
    main: MainFields
    region: RegionFields

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        common = CommonFields.from_dict(data)

        return cls(
            groups=common.groups,
            main=MainFields.from_dict(data["main"]),
            region=RegionFields.from_dict(data["region"])
        )



def get_enum_values(annotation: type):
    """
    Return allowed values or None
    """

    if getattr(annotation, "__origin__", None) is Literal:
        return [arg for arg in annotation.__args__]

    return None


def validate_function(func: str, module: ModuleType) -> bool:
    """
    Validate that the function has a valid signature.
    """
    sig = inspect.signature(getattr(module, func, None))
    parameters = [p for p in sig.parameters]
    assert parameters[0] == "config", f"First parameter of {func} must be 'config'"


def load_group(module_name: str, group: str, iap_principals: list[str]) -> FunctionGroup:
    module = importlib.import_module(module_name)
    module_exports = get_module_exports(module)

    for f in module_exports:
        validate_function(f, module)

    functions = []
    for f in module_exports:
        source = inspect.getsource(getattr(module, f, None))
        func = getattr(module, f, None)
        sig = inspect.signature(func)

        functions.append(
            Function(
                name=f,
                source=source,
                docstring=func.__doc__ or "",
                parameters=[
                    FunctionParameter(
                        name=k,
                        default=str(v.default) if v.default is not inspect.Parameter.empty else None,
                        enumValues=get_enum_values(v.annotation),
                    )
                    for (k, v) in sig.parameters.items()
                    if k != "config"
                ],
            )
        )

    return FunctionGroup(
        group=group,
        module=module_name,
        functions=functions,
        iap_principals=iap_principals,
    )

@functools.lru_cache(maxsize=1)
def load_config() -> RegionConfig | MainConfig | CombinedConfig:
    config_file_path = os.getenv("CONFIG_FILE_PATH")

    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file)

    validate_config(config)

    mode = Mode(config["mode"])

    if mode == Mode.region:
        return RegionConfig.from_dict(config)
    elif mode == Mode.main:
        return MainConfig.from_dict(config)
    else:
        return CombinedConfig.from_dict(config)


def validate_config(config: Any) -> None:
    schema_path = Path(__file__).parent / "config.schema.json"
    with open(schema_path, "r") as f:
        schema = json.load(f)

    jsonschema.validate(instance=config, schema=schema)

