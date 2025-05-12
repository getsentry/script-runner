from typing import Generator

import pytest
from flask import Flask, Response, jsonify, make_response
from flask.testing import FlaskClient
from pytest import MonkeyPatch

from script_runner.blueprints.base_app_bp import base_app_bp


@pytest.fixture()
def client() -> "Generator[FlaskClient[Response], None, None]":
    """
    A Flask test client for the app.
    """
    app = Flask(__name__)
    app.register_blueprint(base_app_bp)
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_good_healthcheck(client: "FlaskClient[Response]") -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    expected_json = {"status": "ok"}
    assert response.get_json() == expected_json


def test_bad_healthcheck(
    client: "FlaskClient[Response]", monkeypatch: MonkeyPatch
) -> None:
    def mock_bad_health() -> Response:
        return make_response(
            jsonify({"status": "error", "reason": "simulated failure"}), 503
        )

    monkeypatch.setattr("script_runner.blueprints.base_app_bp.health", mock_bad_health)
    response = client.get("/health")

    assert response.status_code == 503
    assert response.content_type == "application/json"
    expected_json = {"status": "error", "reason": "simulated failure"}
    assert response.get_json() == expected_json
