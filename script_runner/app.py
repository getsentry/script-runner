import functools
import importlib
import logging
from functools import wraps
from typing import Any, Callable

import requests
import sentry_sdk
from flask import Flask, Response, jsonify, request, send_from_directory

from script_runner.auth import UnauthorizedUser
from script_runner.function import WrappedFunction
from script_runner.utils import CombinedConfig, MainConfig, RegionConfig, load_config

app = Flask(__name__)
config = load_config()

if config.sentry_dsn:
    sentry_sdk.init(
        dsn=config.sentry_dsn,
    )


app = Flask(__name__)


def authenticate_request(f: Callable[..., Response]) -> Callable[..., Response]:
    @wraps(f)
    def authenticate(*args: Any, **kwargs: Any) -> Response:
        try:
            config.auth.authenticate_request(request)
            res = f(*args, **kwargs)
            return res
        except UnauthorizedUser as e:
            logging.error(e, exc_info=True)
            err_response = jsonify({"error": "Unauthorized"})
            err_response.status_code = 401
            return err_response

    return authenticate


def cache_static_files(f: Callable[..., Response]) -> Callable[..., Response]:
    @wraps(f)
    def add_cache_headers(*args: Any, **kwargs: Any) -> Response:
        res = f(*args, **kwargs)
        res.headers["Cache-Control"] = "public, max-age=3600"
        return res

    return add_cache_headers


@functools.lru_cache(maxsize=1)
def get_config() -> dict[str, Any]:
    assert isinstance(config, (MainConfig, CombinedConfig))

    regions = config.main.regions
    groups = config.groups

    group_data = [
        {
            "group": g,
            "functions": [
                {
                    "name": f.name,
                    "docstring": f.docstring,
                    "source": f.source,
                    "parameters": [
                        {
                            "name": p.name,
                            "default": p.default,
                            "enumValues": p.enumValues,
                        }
                        for p in f.parameters
                    ],
                }
                for f in function_group.functions
            ],
        }
        for (g, function_group) in groups.items()
    ]

    return {
        "regions": [r.name for r in regions],
        "groups": group_data,
    }


@app.route("/health")
def health() -> Response:
    return jsonify({"status": "ok"})


if not isinstance(config, RegionConfig):

    @app.route("/")
    @cache_static_files
    def home() -> Response:
        return send_from_directory("frontend/dist", "index.html")

    @app.route("/jq.wasm")
    @cache_static_files
    def jq_wasm() -> Response:
        return send_from_directory("frontend/dist", "jq.wasm")

    @app.route("/assets/<filename>")
    @cache_static_files
    def static_file(filename: str) -> Response:
        return send_from_directory("frontend/dist/assets", filename)

    @app.route("/run", methods=["POST"])
    @authenticate_request
    def run_all() -> Response:
        """
        Run a script for all regions
        """
        assert not isinstance(config, RegionConfig)
        data = request.get_json()

        results = {}

        group_name = data["group"]
        group = config.groups[group_name]
        requested_function = data["function"]
        function = next(
            (f for f in group.functions if f.name == requested_function), None
        )
        assert function is not None, "Invalid function"
        params = data["parameters"]

        for requested_region in data["regions"]:
            region = next(
                (r for r in config.main.regions if r.name == requested_region), None
            )
            if region is None:
                err_response = jsonify({"error": "Invalid region"})
                err_response.status_code = 400
                return err_response

            for audit_logger in config.audit_loggers:
                audit_logger.log(
                    user=config.auth.get_user_email(request) or "unknown",
                    group=group_name,
                    function=requested_function,
                    region=region.name,
                )

            scheme = request.scheme if isinstance(config, CombinedConfig) else "http"

            res = requests.post(
                f"{scheme}://{region.url}/run_region",
                json={
                    "group": group_name,
                    "function": function.name,
                    "function_checksum": function.checksum,
                    "parameters": params,
                    "region": region.name,
                },
            )

            # TODO: handle errors properly
            assert res.status_code == 200
            results[region.name] = res.json()

        return jsonify(results)

    @app.route("/config")
    def fetch_config() -> Response:
        res = get_config()

        executable_groups = []

        for group in config.groups:
            if config.auth.has_group_access(request, group):
                executable_groups.append(group)

        res["executableGroups"] = executable_groups

        return jsonify(res)


if not isinstance(config, MainConfig):

    @app.route("/run_region", methods=["POST"])
    @authenticate_request
    def run_one_region() -> Response:
        """
        Run a script for a specific region. Called from the `/run` endpoint.
        """
        assert isinstance(config, (RegionConfig, CombinedConfig))

        data = request.get_json()
        group_name = data["group"]
        group = config.groups[group_name]
        requested_function = data["function"]

        function = next(
            (f for f in group.functions if f.name == requested_function), None
        )
        assert function is not None

        # Do not run the function if it doesn't appear to be the same
        if function.checksum != data["function_checksum"]:
            raise ValueError("Function mismatch")

        params = data["parameters"]
        module = importlib.import_module(group.module)
        func = getattr(module, requested_function)
        assert isinstance(func, WrappedFunction)
        group_config = config.region.configs.get(group_name, None)
        return jsonify(func.func(group_config, *params))
