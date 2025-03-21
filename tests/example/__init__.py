from typing import Any, Literal


def hello(config: Any, to: str = "world") -> str:
    """
    This function says hello to someone
    """
    return f"hello {to}"


def hello_with_enum(config: Any, to: Literal["foo", "bar"] = "foo") -> str:
    """
    Demo of literal type + default value
    """
    return f"hello {to}"


__all__ = ["hello", "hello_with_enum"]
