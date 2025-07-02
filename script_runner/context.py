from dataclasses import dataclass
from typing import Generic, TypeVar

from flask import g

T = TypeVar("T")


@dataclass(frozen=True)
class FunctionContext(Generic[T]):
    user: str
    region: str
    group_config: T


def get_function_context() -> FunctionContext[T]:
    """
    Returns the function context for the current thread.
    This is used to access the region and group config.
    """
    return FunctionContext(
        user=g.user,
        region=g.region,
        group_config=g.group_config,
    )
