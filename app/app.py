from flask import Flask, send_from_directory, request, jsonify, Response
import functools
import os
from typing import Any, Dict, List, Tuple, Union
from functools import wraps
from datetime import timedelta

from script_runner.config import Config
from script_runner.module_loader import (
    get_group_info,
    validate_function_signatures,
    execute_function,
)


def create_app(config_path: str = None) -> Flask:
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)

    # Initialize config
    config = Config(config_path)

    def cache_static_files(f):
        @wraps(f)
        def add_cache_headers(*args, **kwargs):
            res = f(*args, **kwargs)
            res.headers["Cache-Control"] = "public, max-age=3600"
            return res

        return add_cache_headers

    @app.route("/")
    @cache_static_files
    def home() -> Response:
        """
        Serve the main HTML page.
        """
        return send_from_directory("frontend/dist", "index.html")

    @app.route("/health")
    def health() -> Tuple[Dict[str, str], int]:
        """
        Health check endpoint.
        """
        return jsonify({"status": "ok"}), 200

    @app.route("/jq.wasm")
    @cache_static_files
    def jq_wasm() -> Response:
        """
        Serve the jq.wasm file.
        """
        return send_from_directory("frontend/dist", "jq.wasm")

    @app.route("/config")
    def get_config() -> Dict[str, Any]:
        """
        Get configuration and available functions.
        """
        cfg = config.load()
        module_name = cfg["python_scripts_module_name"]
        groups = cfg["groups"]

        # Validate function signatures
        validate_function_signatures(module_name, groups)

        # Get group info
        group_data = [get_group_info(module_name, group) for group in groups]

        return {
            "regions": cfg["regions"],
            "groups": group_data,
            "executableGroups": config.get_executable_groups(),
        }

    @app.route("/assets/<filename>")
    @cache_static_files
    def static_file(filename: str) -> Response:
        """
        Serve static assets.
        """
        return send_from_directory("frontend/dist/assets", filename)

    @app.route("/run", methods=["POST"])
    def run_script() -> Union[Dict[str, Any], Tuple[Dict[str, str], int]]:
        """
        Run a script with the given parameters.
        """
        cfg = config.load()
        module_name = cfg["python_scripts_module_name"]

        data = request.get_json()

        results = {}

        group = data["group"]
        function = data["function"]
        params = data["parameters"]

        for region in data["regions"]:
            group_config = config.get_region_config(region, group)
            try:
                results[region] = execute_function(
                    module_name, group, function, group_config, params
                )
            except ValueError as exc:
                app.logger.error(f"Error executing function: {exc}")
                return jsonify({"error": "An internal error has occurred."}), 400

        return jsonify(results)

    return app


app = create_app()
