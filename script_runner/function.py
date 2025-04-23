from typing import Any, Callable, Literal
import inspect

RawFunction = Callable[..., Any]


class WrappedFunction:
    def __init__(self, func: RawFunction, readonly: bool) -> None:
        self.func = func
        self._readonly = readonly

        # Validate raw function
        for param in inspect.signature(func).parameters.values():
            if param.annotation is str:
                continue
            elif param.annotation.__origin__ == Literal and all(
                [isinstance(a, str) for a in param.annotation.__args__]
            ):
                continue
            raise TypeError(f"{func} has non-string argument {param.name}")


    @property
    def is_readonly(self) -> bool:
        return self._readonly

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)


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
