import functools
import logging
from functools import wraps
from typing import Any, Callable

from flask import Response, jsonify, make_response, request

from script_runner.auth import UnauthorizedUser
from script_runner.config import config
from script_runner.utils import CombinedConfig, MainConfig


def authenticate_request(f: Callable[..., Response]) -> Callable[..., Response]:
    @wraps(f)
    def authenticate(*args: Any, **kwargs: Any) -> Response:
        try:
            config.auth.authenticate_request(request)
            res = f(*args, **kwargs)
            return res
        except UnauthorizedUser as e:
            logging.error(e, exc_info=True)
            err_response = make_response(jsonify({"error": "Unauthorized"}), 401)
            return err_response

    return authenticate


def cache_static_files(f: Callable[..., Response]) -> Callable[..., Response]:
    @wraps(f)
    def add_cache_headers(*args: Any, **kwargs: Any) -> Response:
        res = f(*args, **kwargs)
        res.headers["Cache-Control"] = "public, max-age=3600"
        return res

    return add_cache_headers


def cache_autocomplete(f: Callable[..., Response]) -> Callable[..., Response]:
    """Cache autocomplete responses in browser for 5 minutes"""

    @wraps(f)
    def add_cache_headers(*args: Any, **kwargs: Any) -> Response:
        res = f(*args, **kwargs)
        res.headers["Cache-Control"] = "public, max-age=300"
        return res

    return add_cache_headers


@functools.lru_cache(maxsize=1)
def get_config() -> dict[str, Any]:
    assert isinstance(config, (MainConfig, CombinedConfig))

    regions = config.main.regions
    groups = config.groups

    group_data = [
        {
            "group": g,
            "functions": [
                {
                    "name": f.name,
                    "docstring": f.docstring,
                    "source": f.source,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.type.value,
                            "default": p.default,
                            "enumValues": p.enum_values,
                        }
                        for p in f.parameters
                    ],
                    "isReadonly": f.is_readonly,
                }
                for f in function_group.functions
            ],
            "docstring": function_group.docstring,
            "markdownFiles": [
                {"name": file.filename, "content": file.content}
                for file in function_group.markdown_files
            ],
        }
        for (g, function_group) in groups.items()
    ]

    return {
        "title": config.main.title,
        "regions": [r.name for r in regions],
        "groups": group_data,
    }
