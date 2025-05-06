import functools
import importlib
import logging
from functools import wraps
from typing import Any, Callable

import requests
import sentry_sdk
from flask import (
    Blueprint,
    Response,
    g,
    jsonify,
    make_response,
    request,
    send_from_directory,
)

from script_runner.auth import UnauthorizedUser
from script_runner.function import WrappedFunction
from script_runner.utils import CombinedConfig, MainConfig, RegionConfig, load_config

config = load_config()

if config.sentry_dsn:
    sentry_sdk.init(
        dsn=config.sentry_dsn,
    )

app_blueprint = Blueprint("app", __name__)


def authenticate_request(f: Callable[..., Response]) -> Callable[..., Response]:
    @wraps(f)
    def authenticate(*args: Any, **kwargs: Any) -> Response:
        try:
            config.auth.authenticate_request(request)
            res = f(*args, **kwargs)
            return res
        except UnauthorizedUser as e:
            logging.error(e, exc_info=True)
            err_response = make_response(jsonify({"error": "Unauthorized"}), 401)
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
                            "type": p.type.value,
                            "default": p.default,
                            "enumValues": p.enum_values,
                        }
                        for p in f.parameters
                    ],
                    "isReadonly": f.is_readonly,
                }
                for f in function_group.functions
            ],
            "docstring": function_group.docstring,
            "markdownFiles": [
                {"name": file.filename, "content": file.content}
                for file in function_group.markdown_files
            ],
        }
        for (g, function_group) in groups.items()
    ]

    return {
        "title": config.main.title,
        "regions": [r.name for r in regions],
        "groups": group_data,
    }


@app_blueprint.route("/health")
def health() -> Response:
    return make_response(jsonify({"status": "ok"}))


if not isinstance(config, RegionConfig):

    @app_blueprint.route("/")
    @cache_static_files
    def home() -> Response:
        return send_from_directory("frontend/dist", "index.html")

    @app_blueprint.route("/jq.wasm")
    @cache_static_files
    def jq_wasm() -> Response:
        return send_from_directory("frontend/dist", "jq.wasm")

    @app_blueprint.route("/assets/<filename>")
    @cache_static_files
    def static_file(filename: str) -> Response:
        return send_from_directory("frontend/dist/assets", filename)

    @app_blueprint.route("/run", methods=["POST"])
    @authenticate_request
    def run_all() -> Response:
        """
        Run a script for all regions
        """
        assert not isinstance(config, RegionConfig)
        data = request.get_json()

        results = {}
        errors = {}

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
                err_response = make_response(jsonify({"error": "Invalid region"}), 400)
                return err_response

            for audit_logger in config.audit_loggers:
                audit_logger.log(
                    user=config.auth.get_user_email(request) or "unknown",
                    group=group_name,
                    function=requested_function,
                    region=region.name,
                )

            scheme = request.scheme if isinstance(config, CombinedConfig) else "http"
            try:
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
                res.raise_for_status()
                results[region.name] = res.json()

            except requests.exceptions.RequestException as e:
                logging.error(
                    f"Request failed for region {region.name}: {e}", exc_info=True
                )
                error_type = (
                    "TimeoutError"
                    if isinstance(e, requests.exceptions.Timeout)
                    else "ConnectionError"
                )
                errors[region.name] = {
                    "type": error_type,
                    "message": f"Network or connection error contacting region {region.name}",
                    "details": str(e),
                }
            except Exception as e:
                logging.error(
                    f"Unexpected error processing region {region.name}: {e}",
                    exc_info=True,
                )
                errors[region.name] = {
                    "type": "GenericError",
                    "message": f"An unexpected error occurred processing region {region.name}",
                    "details": str(e),
                }

        return make_response(jsonify({"results": results, "errors": errors}), 200)

    @app_blueprint.route("/config")
    def fetch_config() -> Response:
        res = get_config()

        groups_without_access = []

        # Filter out groups user doesn't have access to
        user_groups = set()
        for group in config.groups:
            if config.auth.has_group_access(request, group):
                user_groups.add(group)
            else:
                groups_without_access.append(group)

        filtered_groups = [g for g in res["groups"] if g["group"] in user_groups]
        res["groups"] = filtered_groups
        res["groupsWithoutAccess"] = groups_without_access

        return make_response(jsonify(res), 200)


if not isinstance(config, MainConfig):

    @app_blueprint.route("/run_region", methods=["POST"])
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
        g.region = data["region"]
        g.group_config = group_config
        return make_response(jsonify(func(*params)), 200)
