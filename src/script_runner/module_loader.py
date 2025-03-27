"""
Module for dynamically loading and inspecting Python modules.
"""

import functools
import importlib
import inspect
from typing import Any, Callable, Dict, List, Optional, TypedDict
import types
from types import ModuleType


class FunctionParameter(TypedDict):
    name: str
    default: Optional[str]
    enumValues: Optional[List[Any]]


class FunctionInfo(TypedDict):
    name: str
    source: str
    docstring: str
    parameters: List[FunctionParameter]


class GroupInfo(TypedDict):
    group: str
    functions: List[FunctionInfo]


def get_module_exports(module: ModuleType) -> List[str]:
    """
    Get a list of exported function names from a module.
    """
    exports = module.__all__ if hasattr(module, "__all__") else dir(module)
    return [
        name
        for name in exports
        if not name.startswith("_") and callable(getattr(module, name, None))
    ]


def get_enum_values(annotation: type) -> Optional[List[Any]]:
    """
    Return allowed values for a Literal type annotation or None.
    """
    if hasattr(annotation, "__origin__") and annotation.__origin__ is Literal:
        return [arg for arg in annotation.__args__]
    return None


def load_module(module_path: str) -> ModuleType:
    """
    Load a Python module by its path.
    """
    return importlib.import_module(module_path)


def get_function_info(module: ModuleType, function_name: str) -> FunctionInfo:
    """
    Get information about a function from a module.
    """
    func = getattr(module, function_name)

    return {
        "name": function_name,
        "source": inspect.getsource(func),
        "docstring": func.__doc__ or "",
        "parameters": [
            {
                "name": k,
                "default": (
                    str(v.default) if v.default is not inspect.Parameter.empty else None
                ),
                "enumValues": get_enum_values(v.annotation),
            }
            for (k, v) in inspect.signature(func).parameters.items()
            if k != "config"  # Skip the config parameter
        ],
    }


def get_group_info(module_name: str, group: str) -> GroupInfo:
    """
    Get information about all functions in a module group.
    """
    try:
        module = load_module(f"{module_name}.{group}")
        module_exports = get_module_exports(module)

        functions = [get_function_info(module, f) for f in module_exports]

    except ModuleNotFoundError:
        functions = []

    return {"group": group, "functions": functions}


def validate_function_signatures(module_name: str, groups: List[str]) -> None:
    """
    Validate that all functions in the groups have valid signatures.
    """
    for group in groups:
        try:
            module = load_module(f"{module_name}.{group}")
            for func_name in get_module_exports(module):
                func = getattr(module, func_name)
                sig = inspect.signature(func)
                parameters = list(sig.parameters.keys())
                if not parameters or parameters[0] != "config":
                    raise ValueError(
                        f"First parameter of {func_name} in {group} must be 'config'"
                    )
        except ModuleNotFoundError:
            # Skip if module doesn't exist
            pass


def execute_function(
    module_name: str, group: str, function_name: str, config: Any, params: List[Any]
) -> Any:
    """
    Execute a function from a module with the given parameters.
    """
    module = load_module(f"{module_name}.{group}")
    func = getattr(module, function_name)
    return func(config, *params)
