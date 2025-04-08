from typing import Literal

from script_runner import read, write


@read
def hello(to: str = "world") -> str:
    """
    This function says hello to someone
    """
    return f"hello {to}"


@read
def hello_with_enum(to: Literal["foo", "bar"] = "foo") -> str:
    """
    Demo of literal type + default value
    """
    return f"hello {to}"


@write
def some_write_function() -> None:
    pass


__all__ = [
    "hello",
    "hello_with_enum",
    "some_write_function",
]
