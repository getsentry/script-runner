"""
example for tests
"""

from script_runner import read, write
from script_runner.function_parameter import Autocomplete, DynamicAutocomplete, Text


@read
def hello(to: Text = Text(default="world")) -> str:
    """
    This function says hello to someone
    """
    return f"hello {to.value}"


@write
def some_write_function() -> None:
    pass


@read
def basic_autocomplete(
    to: Autocomplete = Autocomplete(options=["foo", "bar"], default="foo")
) -> str:
    """
    Demo of literal type + default value
    """
    return f"hello {to.value}"


def get_options() -> list[str]:
    return [str(i) for i in range(4)]


@read
def dynamic_autocomplete(
    value: DynamicAutocomplete = DynamicAutocomplete(options=get_options),
) -> str:
    """
    Autocomplete demo with dynamic options
    """
    return f"Selected {value.value}"


__all__ = [
    "hello",
    "some_write_function",
    "basic_autocomplete",
    "dynamic_autocomplete",
]
