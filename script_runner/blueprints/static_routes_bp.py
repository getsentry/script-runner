from flask import Blueprint, Response, send_from_directory

from ..decorators import cache_static_files

static_files_bp = Blueprint("static_files", __name__)


@static_files_bp.route("/")
@cache_static_files
def home() -> Response:
    """Serves the main index.html file."""
    return send_from_directory("frontend/dist", "index.html")


@static_files_bp.route("/jq.wasm")
@cache_static_files
def jq_wasm() -> Response:
    return send_from_directory("frontend/dist", "jq.wasm")


@static_files_bp.route("/assets/<path:filename>")
@cache_static_files
def static_file(filename: str) -> Response:
    return send_from_directory("frontend/dist/assets", filename)
