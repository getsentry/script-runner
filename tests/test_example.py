from script_runner.context import FunctionContext
from script_runner.testutils import execute_with_context
from tests.example import basic_autocomplete, dynamic_autocomplete, hello

mock_context = FunctionContext(
    region="test",
    group_config=None,
)


def test_simple_function() -> None:
    (result, _) = execute_with_context(hello, mock_context, ["there"])
    assert result == "hello there"


def test_basic_autocomplete() -> None:
    (result, _) = execute_with_context(basic_autocomplete, mock_context, ["bar"])
    assert result == "hello bar"


def test_dynamic_autocomplete() -> None:
    (result, autocompletions) = execute_with_context(
        dynamic_autocomplete, mock_context, ["foo"]
    )
    assert result == "Selected foo"
    assert autocompletions["value"] == ["0", "1", "2", "3"]
