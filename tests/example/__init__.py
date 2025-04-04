from typing import Any, Literal

from script_runner import read, write


@read
def hello(config: Any, to: str = "world") -> str:
    """
    This function says hello to someone
    """
    return f"hello {to}"


@read
def hello_with_enum(config: Any, to: Literal["foo", "bar"] = "foo") -> str:
    """
    Demo of literal type + default value
    """
    return f"hello {to}"


@write
def some_write_function(config: Any) -> None:
    pass


__all__ = [
    "hello",
    "hello_with_enum",
    "some_write_function",
]
