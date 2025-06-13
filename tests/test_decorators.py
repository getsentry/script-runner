from dataclasses import replace

import pytest
from flask import Flask, Request, Response, jsonify, make_response

from script_runner.approval_policy import AllowAll
from script_runner.auth import AuthMethod, UnauthorizedUser
from script_runner.config import configure


class MockAuthMethod(AuthMethod):
    """
    Mock auth method that only allows `test_group` access.
    """

    def authenticate_request(self, request: Request) -> None:
        data = request.get_json()

        if data["group"] == "test_group":
            return None

        raise UnauthorizedUser("User is not authorized for this group")

    def get_user_email(self, request: Request) -> str | None:
        return "test@test.com"

    def has_group_access(self, request: Request, group: str) -> bool:
        if group == "test_group":
            return True
        return False


@pytest.fixture(scope="module")
def app() -> Flask:
    """
    Flask app configured for testing.
    """
    from script_runner.decorators import authenticate_request

    config_file_path = "example_config_combined.yaml"
    approval_policy = AllowAll()
    approval_store = None

    app_config = configure(config_file_path, approval_policy, approval_store)

    # switch out to the mock auth method
    app_config_with_auth_mock = replace(
        app_config,
        config=replace(
            app_config.config,
            auth=MockAuthMethod(),
        ),
    )

    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/protected_route", methods=["POST"])
    @authenticate_request(app_config_with_auth_mock)
    def _protected_view() -> Response:
        return make_response(jsonify(message="Access Granted"), 200)

    return app


def test_auth_on_success(app: Flask) -> None:
    with app.test_client() as client:
        response = client.post("/protected_route", json={"group": "test_group"})

    assert response.status_code == 200
    assert response.get_json()["message"] == "Access Granted"


def test_no_auth_on_failure(app: Flask) -> None:
    with app.test_client() as client:
        response = client.post("/protected_route", json={"group": "invalid_group"})

    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"
