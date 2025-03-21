from app.utils import FunctionParameter, load_group


def test_validate_config_functions() -> None:
    """
    Test that all functions in the config module have a valid signature.
    """
    module = "tests.example"
    group_name = "example"
    iap_principals = ["test@sentry.io"]

    group = load_group(module, group_name, iap_principals)
    assert group.module == module
    assert group.iap_principals == ["test@sentry.io"]
    assert [f.name for f in group.functions] == ["hello", "hello_with_enum"]
    assert [f.parameters for f in group.functions] == [
        [FunctionParameter(name="to", default="world", enumValues=None)],
        [FunctionParameter(name="to", default="foo", enumValues=["foo", "bar"])],
    ]
