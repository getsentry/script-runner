import logging

import requests
from flask import (
    Blueprint,
    Response,
    jsonify,
    make_response,
    request,
)

from script_runner.app import config
from script_runner.decorators import authenticate_request, get_config
from script_runner.utils import CombinedConfig, RegionConfig

main_config_bp = Blueprint("main_config", __name__)


@main_config_bp.route("/run", methods=["POST"])
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
    function = next((f for f in group.functions if f.name == requested_function), None)
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


@main_config_bp.route("/config")
def fetch_config() -> Response:
    res = get_config()

    groups_without_access = []

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
