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
def writes_to_file(config: Any, content: str) -> None:
    with open("example.txt", "w") as file:
        file.write(content)


__all__ = ["hello", "hello_with_enum", "writes_to_file"]
