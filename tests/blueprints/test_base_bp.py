from typing import Generator

import pytest
from flask import Flask, Response
from flask.testing import FlaskClient

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


def test_healthcheck(client: "FlaskClient[Response]") -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    expected_json = {"status": "ok"}
    assert response.get_json() == expected_json
