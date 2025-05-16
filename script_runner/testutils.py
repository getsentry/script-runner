from typing import Any

from flask import Flask, g, jsonify

from script_runner.context import FunctionContext
from script_runner.function import WrappedFunction
from script_runner.function_parameter import DynamicAutocomplete


def execute_with_context(
    func: WrappedFunction,
    mock_context: FunctionContext[Any],
    args: list[str],
) -> tuple[Any, dict[str, list[str]]]:
    """
    Run a function with a mock context, and return the result.
    It also returns an object containing any dynamic autocompletions
    so that tests can assert on their output.
    """
    app = Flask(__name__)
    with app.app_context():
        g.region = mock_context.region
        g.group_config = mock_context.group_config

        result = func(*args)

        autocompletions = {}

        # If there are any autocomplete parameters make sure they return a list of strings
        for name, param in func._params:
            if isinstance(param, DynamicAutocomplete):
                options = param._options()
                autocompletions[name] = options
                assert all(isinstance(item, str) for item in options)

        # Ensure the result is JSON serializable
        response = jsonify(result)
        assert response.status_code == 200

        return result, autocompletions
