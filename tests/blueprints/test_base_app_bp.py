import pytest
from flask import Flask

from script_runner.app import create_flask_app
from script_runner.approval_policy import AllowAll


@pytest.fixture(scope="module", autouse=True, params=[
    "example_config_combined.yaml",
    "example_config_main.yaml",
    "example_config_local.yaml",
])
def app(request: pytest.FixtureRequest) -> Flask:
    config_file_path = request.param
    approval_policy = AllowAll()
    approval_store = None
    return create_flask_app(config_file_path, approval_policy, approval_store)


def test_health(app: Flask) -> None:
    test_client = app.test_client()
    response = test_client.get("health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
