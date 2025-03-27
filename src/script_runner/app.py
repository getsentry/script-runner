from flask import Flask, send_from_directory, request, jsonify
import functools
import importlib
import inspect
import yaml
from typing import Literal
import os
from functools import wraps
from datetime import timedelta

from types import ModuleType

app = Flask(__name__)


def cache_static_files(f):
    @wraps(f)
    def add_cache_headers(*args, **kwargs):
        res = f(*args, **kwargs)
        res.headers['Cache-Control'] = 'public, max-age=3600'
        return res
    return add_cache_headers


def get_module_exports(module: ModuleType) -> list[str]:
    exports = module.__all__ if hasattr(module, "__all__") else dir(module)
    return [
        name
        for name in exports
        if not name.startswith("_") and callable(getattr(module, name, None))
    ]


@functools.lru_cache(maxsize=1)
def load_config_file():
    """
    Loads and validates configuration
    """
    config_file_path = os.getenv("CONFIG_FILE_PATH")

    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file)

    module_name = config["python_scripts_module_name"]

    # TODO: json validation

    assert set(config["regions"]) == set(config["region_configs"].keys()), "Invalid region config"

    # Ensure all functions have valid signatures
    for group in config["groups"]:
        module = importlib.import_module(f"{module_name}.{group}")
        for f in get_module_exports(module):
            sig = inspect.signature(getattr(module, f, None))
            parameters = [p for p in sig.parameters]
            assert parameters[0] == "config", f"First parameter of {f} must be 'config'"

    return config


def get_enum_values(annotation: type):
    """
    Return allowed values or None
    """

    if getattr(annotation, "__origin__", None) is Literal:
        return [arg for arg in annotation.__args__]

    return None


@functools.lru_cache(maxsize=1)
def get_functions():
    config = load_config_file()

    regions = config["regions"]
    groups = config["groups"]

    group_data = []

    module_name = config["python_scripts_module_name"]

    for group in groups:
        try:
            module = importlib.import_module(f"{module_name}.{group}")
            module_exports = get_module_exports(module)

            functions = [
                {
                    "name": f,
                    "source": inspect.getsource(getattr(module, f, None)),
                    "docstring": getattr(module, f, None).__doc__ or "",
                    "parameters": [
                        {
                            "name": k,
                            "default": (
                                str(v.default) if v.default is not inspect.Parameter.empty else None
                            ),
                            "enumValues": get_enum_values(v.annotation),
                        }
                        for (k, v) in inspect.signature(getattr(module, f, None)).parameters.items()
                        if k != "config"
                    ],
                }
                for f in module_exports
            ]

        except ModuleNotFoundError:
            functions = []

        group_data.append({"group": group, "functions": functions})

    return {
        "regions": regions,
        "groups": group_data,
    }


@app.route("/")
@cache_static_files
def home():
    return send_from_directory("frontend/dist", "index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200



@app.route("/jq.wasm")
@cache_static_files
def jq_wasm():
    return send_from_directory("frontend/dist", "jq.wasm")


@app.route("/config")
def functions():
    res = get_functions()

    # TODO: properly filter based on user access
    res["executableGroups"] = ["example", "kafka", "access_logs"]

    return res


@app.route("/assets/<filename>")
@cache_static_files
def static_file(filename: str):
    return send_from_directory("frontend/dist/assets", filename)


@app.route("/run", methods=["POST"])
def run_script():
    config = load_config_file()
    module_name = config["python_scripts_module_name"]

    data = request.get_json()

    results = {}

    group = data["group"]
    function = data["function"]
    params = data["parameters"]
    module = importlib.import_module(f"{module_name}.{group}")

    for region in data["regions"]:
        func = getattr(module, function)
        group_config = config["region_configs"][region].get(group, None)
        try:
            results[region] = func(group_config, *params)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    return jsonify(results)
