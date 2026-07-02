from unittest.mock import ANY, patch

import pytest
from flask import Flask

from script_runner.app import create_flask_app
from script_runner.approval_policy import AllowAll
from script_runner.auth import NoAuth


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
    app = create_flask_app(config_file_path, approval_policy, approval_store)
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


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


def test_config_not_poisoned_by_restricted_user(app: Flask) -> None:
    """
    A request from a user without group access must not remove those groups
    from the cached config served to subsequent requests.
    """
    test_client = app.test_client()

    with patch.object(NoAuth, "has_group_access", return_value=False):
        restricted = test_client.get("config")
    assert restricted.status_code == 200
    assert restricted.json is not None
    assert restricted.json["groups"] == []
    assert restricted.json["groupsWithoutAccess"] == ["example"]
    assert restricted.json["accessMap"] == {}

    response = test_client.get("config")
    assert response.status_code == 200
    assert response.json is not None
    assert [g["group"] for g in response.json["groups"]] == ["example"]
    assert response.json["groupsWithoutAccess"] == []
    assert response.json["accessMap"]["example"]["hello"] == {"local": "allow"}
