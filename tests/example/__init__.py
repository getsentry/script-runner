"""
example for tests
"""

from script_runner import read, write
from script_runner.function_parameter import Autocomplete, Text


@read
def hello(to: Text = Text(default="world")) -> str:
    """
    This function says hello to someone
    """
    return f"hello {to.value}"


@read
def hello_with_enum(
    to: Autocomplete = Autocomplete(options=["foo", "bar"], default="foo")
) -> str:
    """
    Demo of literal type + default value
    """
    return f"hello {to.value}"


@write
def some_write_function() -> None:
    pass


__all__ = [
    "hello",
    "hello_with_enum",
    "some_write_function",
]
