"""
Script runner demos
"""

import random
from datetime import datetime, timedelta
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
def writes_to_file(content: str) -> None:
    """
    Testing a write action
    """

    with open("example.txt", "w") as file:
        file.write(content)


@read
def render_chart() -> list[dict[str, str | int]]:
    """
    Return some data for a timeseries chart
    """
    return list(
        {
            "day": (datetime.today() - timedelta(days=i + 1)).strftime("%Y-%m-%d"),
            "series1": random.randint(0, 100),
            "series2": random.randint(300, 500),
            "series3": random.randint(1000, 5000),
        }
        for i in range(14)
    )


__all__ = ["hello", "hello_with_enum", "writes_to_file", "render_chart"]
