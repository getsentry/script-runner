from unittest.mock import ANY

import pytest
from flask import Flask

from script_runner.app import create_flask_app
from script_runner.approval_policy import AllowAll


@pytest.fixture(
    scope="module",
    autouse=True,
    params=[
        "example_config_combined.yaml",
        "example_config_main.yaml",
    ],
)
def app(request: pytest.FixtureRequest) -> Flask:
    config_file_path = request.param
    approval_policy = AllowAll()
    approval_store = None
    return create_flask_app(config_file_path, approval_policy, approval_store)


def test_config(app: Flask) -> None:
    test_client = app.test_client()
    response = test_client.get("config")
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["regions"] == ["local"]
    assert response.json["groups"] == [
        {"group": "example", "docstring": ANY, "functions": ANY, "markdownFiles": [ANY]}
    ]
    assert response.json["groupsWithoutAccess"] == []
    assert response.json["accessMap"]["example"]["hello"] == {"local": "allow"}
