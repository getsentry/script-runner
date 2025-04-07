import threading
from dataclasses import dataclass
from typing import Generic, TypeVar

function_context_thread_local = threading.local()


T = TypeVar("T")


@dataclass(frozen=True)
class FunctionContext(Generic[T]):
    region: str
    group_config: T


def get_function_context() -> FunctionContext[T]:
    """
    Returns the function context for the current thread.
    This is used to access the region and group config.
    """
    return FunctionContext(
        region=function_context_thread_local.region,
        group_config=function_context_thread_local.group_config,
    )
