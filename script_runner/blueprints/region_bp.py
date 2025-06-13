import importlib

from flask import Blueprint, Response, g, jsonify, make_response, request

from script_runner.config import Config
from script_runner.decorators import authenticate_request
from script_runner.function import WrappedFunction
from script_runner.function_parameter import DynamicAutocomplete
from script_runner.utils import CombinedConfig, MainConfig, RegionConfig


def create_region_bp(app_config: Config) -> Blueprint:
    config = app_config.config

    assert not isinstance(config, MainConfig)

    region_bp: Blueprint = Blueprint("region_config", __name__)

    @region_bp.route("/run_region", methods=["POST"])
    @authenticate_request(app_config)
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

    @region_bp.route("/autocomplete_region", methods=["GET"])
    def autocomplete_one_region() -> Response:
        """
        Get autocomplete values for one region. Called from the `/autocomplete` endpoint.
        """
        group_name = request.args["group"]
        group = config.groups[group_name]
        requested_function = request.args["function"]
        region = request.args["region"]

        options = {}

        function = next(
            (f for f in group.functions if f.name == requested_function), None
        )
        assert function is not None

        group_config = config.region.configs.get(group_name, None)
        g.region = region
        g.group_config = group_config

        for param in function.parameters:
            if isinstance(param._ref, DynamicAutocomplete):
                options[param.name] = param._ref.get_autocomplete_options()

        return make_response(jsonify(options), 200)

    return region_bp
