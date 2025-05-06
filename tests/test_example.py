from script_runner.context import FunctionContext
from script_runner.testutils import execute_with_context
from tests.example import hello, hello_with_enum

mock_context = FunctionContext(
    region="test",
    group_config=None,
)


def test_simple_function() -> None:
    result = execute_with_context(hello, mock_context, ["there"])
    assert result == "hello there"


def test_enum() -> None:
    result = execute_with_context(hello_with_enum, mock_context, ["bar"])
    assert result == "hello bar"
