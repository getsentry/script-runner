import functools
import hashlib
import importlib
import inspect
import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

import jsonschema
import yaml

from app.auth import AuthMethod, GoogleAuth, NoAuth


class ConfigError(Exception):
    pass


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


@dataclass(frozen=True)
class CommonFields:
    auth: AuthMethod
    groups: dict[str, FunctionGroup]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommonFields":
        auth_data = data["authentication"]
        auth_method = auth_data["method"]

        auth: AuthMethod

        if auth_method == "google_iap":
            iap_principals = auth_data["google_iap"]["iap_principals"]
            audience_code = auth_data["google_iap"]["audience_code"]

            auth = GoogleAuth(audience_code, iap_principals)
        elif auth_method == "no_auth":
            auth = NoAuth()
        else:
            raise ConfigError(f"Invalid authentication method: {auth_method}")

        groups = {
            g: load_group(val["python_module"], g)
            for (g, val) in data["groups"].items()
        }

        return cls(auth=auth, groups=groups)


@dataclass(frozen=True)
class RegionFields:
    name: str
    configs: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RegionFields":
        return cls(name=data["name"], configs=data["configs"])


@dataclass(frozen=True)
class MainFields:
    regions: list[Region]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MainFields":
        return cls(
            regions=[Region(name=r["name"], url=r["url"]) for r in data["regions"]],
        )


@dataclass(frozen=True)
class RegionConfig(CommonFields):
    region: RegionFields

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RegionConfig":
        common = CommonFields.from_dict(data)

        return cls(
            auth=common.auth,
            groups=common.groups,
            region=RegionFields.from_dict(data["region"]),
        )


@dataclass(frozen=True)
class MainConfig(CommonFields):
    main: MainFields

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MainConfig":
        common = CommonFields.from_dict(data)

        return cls(
            auth=common.auth,
            groups=common.groups,
            main=MainFields.from_dict(data["main"]),
        )


@dataclass(frozen=True)
class CombinedConfig(CommonFields):
    main: MainFields
    region: RegionFields

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CombinedConfig":
        common = CommonFields.from_dict(data)

        return cls(
            auth=common.auth,
            groups=common.groups,
            main=MainFields.from_dict(data["main"]),
            region=RegionFields.from_dict(data["region"]),
        )


def get_enum_values(annotation: type) -> list[str] | None:
    """
    Return allowed values or None
    """

    if getattr(annotation, "__origin__", None) is Literal:
        return [arg for arg in annotation.__args__]  # type:ignore[attr-defined]

    return None


def validate_function(func: str, module: ModuleType) -> None:
    """
    Validate that the function has a valid signature.
    """
    function = getattr(module, func, None)
    assert function is not None
    sig = inspect.signature(function)
    parameters = [p for p in sig.parameters]
    assert parameters[0] == "config", f"First parameter of {func} must be 'config'"


def load_group(module_name: str, group: str) -> FunctionGroup:
    module = importlib.import_module(module_name)
    module_exports = get_module_exports(module)

    for f in module_exports:
        validate_function(f, module)

    functions = []
    for f in module_exports:
        function = getattr(module, f, None)
        assert function is not None
        source = inspect.getsource(function)
        sig = inspect.signature(function)

        functions.append(
            Function(
                name=f,
                source=source,
                docstring=function.__doc__ or "",
                parameters=[
                    FunctionParameter(
                        name=k,
                        default=(
                            str(v.default)
                            if v.default is not inspect.Parameter.empty
                            else None
                        ),
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
    )


@functools.lru_cache(maxsize=1)
def load_config() -> RegionConfig | MainConfig | CombinedConfig:
    config_file_path = os.getenv("CONFIG_FILE_PATH")
    assert isinstance(config_file_path, str)

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
