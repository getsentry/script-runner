import pytest

from script_runner.app import create_flask_app
from script_runner.approval_policy import AllowAll


@pytest.mark.parametrize(
    "config_file_path",
    [
        "example_config_combined.yaml",
        "example_config_main.yaml",
        "example_config_local.yaml",
    ],
)
def test_create_flask_app(config_file_path: str) -> None:
    """
    Test creating app in combined, main and regional modes.
    """
    approval_policy = AllowAll()
    approval_store = None

    app = create_flask_app(config_file_path, approval_policy, approval_store)

    test_client = app.test_client()
    response = test_client.get("health")
    assert response.status_code == 200
