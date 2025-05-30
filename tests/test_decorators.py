import os
from typing import Generator
from unittest.mock import patch

import pytest
from flask import Flask, Response, jsonify, make_response

from script_runner.auth import UnauthorizedUser


@pytest.fixture(scope="session", autouse=True)
def setup() -> Generator[None, None, None]:
    original_config_path = os.environ.get("CONFIG_FILE_PATH")

    current_file_path = os.path.abspath(__file__)
    project_root_dir = os.path.dirname(os.path.dirname(current_file_path))
    test_config_path = os.path.join(
        project_root_dir,
        "example_config_combined.yaml",
    )

    os.environ["CONFIG_FILE_PATH"] = test_config_path

    yield
    if original_config_path:
        os.environ["CONFIG_FILE_PATH"] = original_config_path
    else:
        os.environ.pop("CONFIG_FILE_PATH", None)


@pytest.fixture()
def app() -> Flask:
    """
    Flask app configured for testing.
    """
    from script_runner.decorators import authenticate_request

    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/protected_route", methods=["GET", "POST"])
    @authenticate_request
    def _protected_view() -> Response:
        return make_response(jsonify(message="Access Granted"), 200)

    return app


def test_auth_on_success(app: Flask) -> None:
    with app.test_client() as client:
        response = client.get("/protected_route")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Access Granted"


def test_no_auth_on_failure(app: Flask) -> None:
    from script_runner.config import config

    with app.test_client() as client:
        with patch.object(
            config.auth,
            "authenticate_request",
            side_effect=UnauthorizedUser("Simulated direct auth failure"),
        ) as mock_auth_call:
            response = client.post("/protected_route", json={"group": "test_group"})

    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"
    mock_auth_call.assert_called_once()
