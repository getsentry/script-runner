from typing import Any, Callable

RawFunction = Callable[..., Any]


class WrappedFunction:
    def __init__(self, func: RawFunction, readonly: bool) -> None:
        self.func = func
        self._readonly = readonly

    @property
    def is_readonly(self) -> bool:
        return self._readonly


def read(func: RawFunction) -> WrappedFunction:
    """
    Decorator to mark a function as read-only.
    """
    return WrappedFunction(func, readonly=True)


def write(func: RawFunction) -> WrappedFunction:
    """
    Decorator to mark a function that does more than just read.
    Executing a write function will be logged in the system.
    """
    return WrappedFunction(func, readonly=False)
