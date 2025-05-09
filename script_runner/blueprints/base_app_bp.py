from flask import (
    Blueprint,
    Response,
    jsonify,
    make_response,
)

base_app_bp: Blueprint = Blueprint("base", __name__)


@base_app_bp.route("/health")
def health() -> Response:
    return make_response(jsonify({"status": "ok"}))
