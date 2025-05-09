import importlib

from flask import (
    Blueprint,
    Response,
    g,
    jsonify,
    make_response,
    request,
)

from script_runner.app import config
from script_runner.decorators import authenticate_request
from script_runner.function import WrappedFunction
from script_runner.utils import CombinedConfig, RegionConfig

region_config_bp = Blueprint("region_config", __name__)


@region_config_bp.route("/run_region", methods=["POST"])
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

    function = next((f for f in group.functions if f.name == requested_function), None)
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
