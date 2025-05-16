import os
from typing import Generator

import pytest
from flask import Flask, Response
from flask.testing import FlaskClient


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
def app() -> Generator[Flask, None, None]:
    """
    Flask app configured for testing.
    """
    from script_runner.app import app as flask_application

    flask_application.config.update(
        {
            "TESTING": True,
        }
    )
    yield flask_application


@pytest.fixture()
def client(
    app: Flask,
) -> "FlaskClient[Response]":
    """
    A Flask test client for the app.
    """
    return app.test_client()
