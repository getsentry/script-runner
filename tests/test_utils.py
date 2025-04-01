from script_runner.auth import GoogleAuth, NoAuth
from script_runner.utils import CommonFields, FunctionParameter, load_group


def test_common_fields() -> None:
    no_auth = CommonFields.from_dict(
        {
            "groups": {},
            "authentication": {
                "method": "no_auth",
            },
        }
    )
    assert isinstance(no_auth.auth, NoAuth)

    google_auth = CommonFields.from_dict(
        {
            "groups": {"example": {"python_module": "tests.example"}},
            "authentication": {
                "method": "google_iap",
                "google_iap": {
                    "iap_principals": {"example": ["test@test.com"]},
                    "audience_code": "/projects/xxx/global/backendServices/xxx",
                },
            },
        }
    )
    assert isinstance(google_auth.auth, GoogleAuth)


def test_validate_config_functions() -> None:
    """
    Test that all functions in the config module have a valid signature.
    """
    module = "tests.example"
    group_name = "example"

    group = load_group(module, group_name)
    assert group.module == module
    assert [f.name for f in group.functions] == ["hello", "hello_with_enum"]
    assert [f.parameters for f in group.functions] == [
        [FunctionParameter(name="to", default="world", enumValues=None)],
        [FunctionParameter(name="to", default="foo", enumValues=["foo", "bar"])],
    ]
