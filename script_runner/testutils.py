from typing import Any

from flask import Flask, g

from script_runner.context import FunctionContext
from script_runner.function import WrappedFunction


def execute_with_context(
    func: WrappedFunction, mock_context: FunctionContext[Any], args: list[str]
) -> Any:
    """
    Run a function with a mock context, and return the result.
    """
    app = Flask(__name__)
    with app.app_context():
        g.region = mock_context.region
        g.group_config = mock_context.group_config

        return func(*args)
