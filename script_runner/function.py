from typing import Any, Protocol


class Function(Protocol):
    _readonly: bool

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass


def read(func: Function) -> Function:
    """
    Decorator to mark a function as read-only.
    """
    func._readonly = True
    return func


def write(func: Function) -> Function:
    """
    Decorator to mark a function that does more than just read.
    Executing a write function will be logged in the system.
    """
    func._readonly = False
    return func
