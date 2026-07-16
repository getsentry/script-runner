from typing import Any

from flask import Flask, g

from script_runner.context import FunctionContext, get_function_context


def test_get_function_context_without_user() -> None:
    # Endpoints like /autocomplete_region don't authenticate and never set
    # g.user. get_function_context() must not raise in that case.
    app = Flask(__name__)
    with app.app_context():
        g.region = "test"
        g.group_config = {"clusters": []}

        context: FunctionContext[Any] = get_function_context()

        assert context.user is None
        assert context.region == "test"
        assert context.group_config == {"clusters": []}


def test_get_function_context_with_user() -> None:
    app = Flask(__name__)
    with app.app_context():
        g.user = "test@test.com"
        g.region = "test"
        g.group_config = None

        context: FunctionContext[Any] = get_function_context()

        assert context.user == "test@test.com"
