"""
Script runner demos
"""

import random
from datetime import datetime, timedelta

from script_runner import (
    Autocomplete,
    DynamicAutocomplete,
    Integer,
    Number,
    Text,
    TextArea,
    read,
    write,
)


@read
def hello(to: Text = Text(default="world")) -> str:
    """
    This function says hello to someone
    """
    return f"hello {to.value}"


@read
def add_numbers(a: Integer, b: Number = Number(default=0.1)) -> float:
    """
    testing numeric input types
    """
    return float(a.value) + b.value


@write
def writes_to_file(content: TextArea) -> None:
    """
    Testing a write action
    """
    with open("example.txt", "w") as file:
        file.write(content.value)


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


@read
def basic_autocomplete(
    to: Autocomplete = Autocomplete(options=["foo", "bar"], default="foo")
) -> str:
    """
    Demo of literal type + default value
    """
    return f"hello {to.value}"


def get_options() -> list[str]:
    import random

    return [str(random.randint(0, 100) * i) for i in range(10)]


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
    "writes_to_file",
    "render_chart",
    "add_numbers",
    "basic_autocomplete",
    "dynamic_autocomplete",
]
