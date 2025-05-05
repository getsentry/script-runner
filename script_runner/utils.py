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
from typing import Any

import jsonschema
import yaml

from script_runner.audit_log import (
    AuditLogger,
    DatadogEventLogger,
    StandardOutputLogger,
)
from script_runner.auth import AuthMethod, GoogleAuth, NoAuth
from script_runner.function import WrappedFunction
from script_runner.function_parameter import InputType


class ConfigError(Exception):
    pass


def get_module_exports(module: ModuleType) -> list[str]:
    assert hasattr(module, "__all__")
    return [f for f in module.__all__]


def get_markdown_files(module: ModuleType) -> list[str]:
    if hasattr(module, "__file__") and module.__file__ is not None:
        module_path = os.path.dirname(os.path.abspath(module.__file__))
        return [
            f"{module_path}/{f}"
            for f in os.listdir(module_path)
            if os.path.isfile(os.path.join(module_path, f)) and f.endswith(".md")
        ]
    else:
        return []


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
    type: InputType
    default: str | None
    enum_values: list[str] | None  # applies only to select


@dataclass(frozen=True)
class Function:
    name: str
    source: str
    docstring: str
    parameters: list[FunctionParameter]
    is_readonly: bool

    @functools.cached_property
    def checksum(self) -> str:
        return hashlib.md5(self.source.encode()).hexdigest()


@dataclass(frozen=True)
class MarkdownFile:
    filename: str
    content: str

    @classmethod
    def from_path(cls, filepath: str) -> "MarkdownFile":
        with open(filepath, "r") as file:
            content = file.read()
        filename = os.path.basename(filepath)
        return cls(filename=filename, content=content)


@dataclass(frozen=True)
class FunctionGroup:
    group: str
    module: str
    docstring: str
    functions: list[Function]
    markdown_files: list[MarkdownFile]


@dataclass(frozen=True)
class CommonFields:
    auth: AuthMethod
    audit_loggers: list[AuditLogger]
    groups: dict[str, FunctionGroup]
    sentry_dsn: str | None

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

        audit_loggers: list[AuditLogger] = []

        audit_log_data = data["audit_logs"]
        if "console" in audit_log_data:
            audit_loggers.append(StandardOutputLogger())

        if "datadog" in audit_log_data:
            audit_loggers.append(
                DatadogEventLogger(api_key=audit_log_data["datadog"]["api_key"])
            )

        sentry_dsn = data.get("sentry_dsn")

        return cls(
            auth=auth, audit_loggers=audit_loggers, groups=groups, sentry_dsn=sentry_dsn
        )


@dataclass(frozen=True)
class RegionFields:
    name: str
    configs: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RegionFields":
        return cls(name=data["name"], configs=data["configs"])


@dataclass(frozen=True)
class MainFields:
    title: str | None
    regions: list[Region]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MainFields":
        return cls(
            title=data.get("title"),
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
            audit_loggers=common.audit_loggers,
            groups=common.groups,
            sentry_dsn=common.sentry_dsn,
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
            audit_loggers=common.audit_loggers,
            groups=common.groups,
            sentry_dsn=common.sentry_dsn,
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
            audit_loggers=common.audit_loggers,
            groups=common.groups,
            sentry_dsn=common.sentry_dsn,
            main=MainFields.from_dict(data["main"]),
            region=RegionFields.from_dict(data["region"]),
        )


def load_group(module_name: str, group: str) -> FunctionGroup:
    module = importlib.import_module(module_name)
    module_exports = get_module_exports(module)
    markdown_files = get_markdown_files(module)

    module_doc = module.__doc__
    assert module_doc is not None, f"Missing module documentation: {module_name}"

    functions = []
    for f in module_exports:
        function = getattr(module, f, None)
        assert isinstance(
            function, WrappedFunction
        ), f"{f} must be marked @read or @write"

        source = inspect.getsource(function._func)

        functions.append(
            Function(
                name=f,
                source=source,
                docstring=function.__doc__ or "",
                parameters=[
                    FunctionParameter(
                        name=name,
                        type=p.input_type(),
                        default=p.default,
                        enum_values=p.options,
                    )
                    for (name, p) in function._params
                ],
                is_readonly=function.is_readonly,
            )
        )

    return FunctionGroup(
        group=group,
        module=module_name,
        functions=functions,
        docstring=module_doc,
        markdown_files=[MarkdownFile.from_path(f) for f in markdown_files],
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
