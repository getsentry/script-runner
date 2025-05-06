import copy
import inspect
from typing import Any, Callable

from script_runner.function_parameter import FunctionParameter

RawFunction = Callable[..., Any]


class WrappedFunction:
    def __init__(self, func: RawFunction, readonly: bool) -> None:
        self._func = func
        self._readonly = readonly

        self._params: list[tuple[str, FunctionParameter[Any]]] = []

        # Validate function arguments
        for name, param in inspect.signature(func).parameters.items():
            if issubclass(param.annotation, FunctionParameter):
                if param.default is inspect.Parameter.empty:
                    self._params.append((name, param.annotation()))
                else:
                    self._params.append((name, param.default))
                continue
            raise TypeError(f"{func.__name__} has invalid argument {param.name}")

    @property
    def is_readonly(self) -> bool:
        return self._readonly

    def __call__(self, *args: Any) -> Any:
        # Deep copy the parameters on each function execution becuase we use
        # mutable default arguments in function signatures.
        params = [copy.deepcopy(p[1]) for p in self._params]

        for idx, arg in enumerate(args):
            params[idx].set_value(arg)

        return self._func(*params)


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
