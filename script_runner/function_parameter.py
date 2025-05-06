from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, TypeVar


# This is the list of types that the UI knows how to handle
class InputType(Enum):
    TEXT = "text"  # <input type=text />
    TEXTAREA = "textarea"  # <textarea />
    SELECT = "select"  # <select />
    NUMBER = "number"  # <input type=number />
    INTEGER = "integer"  # <input type=number /> with integer validation


TParam = TypeVar("TParam", int, float, str, bool)


class FunctionParameter(ABC, Generic[TParam]):
    @abstractmethod
    def input_type(self) -> InputType:
        raise NotImplementedError

    @abstractmethod
    def encode(self, value: TParam) -> str:
        """
        values are always strings in the API/UI
        """
        raise NotImplementedError

    @abstractmethod
    def decode(self, value: str) -> TParam:
        """
        decode values from the UI
        input validation can be done here
        """
        raise NotImplementedError

    def set_value(self, value: str) -> None:
        """
        Initially empty. self._value is populated
        when the value gets set via the UI
        """
        self._value: TParam = self.decode(value)

    def set_default(self, default: TParam) -> None:
        """
        Called from constructor of of the subclass to set the default value
        if one is provided
        """
        self._default: TParam = default

    @property
    def value(self) -> TParam:
        if hasattr(self, "_value"):
            return self._value
        elif hasattr(self, "_default"):
            return self._default
        else:
            raise ValueError("No value or default")

    @property
    def default(self) -> TParam | None:
        return getattr(self, "_default", None)

    @property
    def options(self) -> list[str] | None:
        """
        default none, only applies to select
        """
        return None


class Text(FunctionParameter[str]):
    def __init__(self, *, default: str | None = None) -> None:
        if default is not None:
            self.set_default(default)

    def input_type(self) -> InputType:
        return InputType.TEXT

    def encode(self, value: str) -> str:
        return value

    def decode(self, value: str) -> str:
        return value


class TextArea(Text):
    def input_type(self) -> InputType:
        return InputType.TEXTAREA


class Number(FunctionParameter[float]):
    def __init__(self, *, default: float | None = None) -> None:
        if default is not None:
            self.set_default(default)

    def input_type(self) -> InputType:
        return InputType.NUMBER

    def encode(self, value: float) -> str:
        return str(value)

    def decode(self, value: str) -> float:
        return float(value)


class Integer(FunctionParameter[int]):
    def __init__(self, *, default: int | None = None) -> None:
        if default is not None:
            self.set_default(default)

    def input_type(self) -> InputType:
        return InputType.INTEGER

    def encode(self, value: int) -> str:
        return str(value)

    def decode(self, value: str) -> int:
        return int(value)


class Select(FunctionParameter[str]):
    """
    basic select which supports choosing one value from a list of strings
    """

    def __init__(self, *, options: list[str], default: str | None = None) -> None:
        self._options = options
        if default is not None:
            self.set_default(default)

    def input_type(self) -> InputType:
        return InputType.SELECT

    def encode(self, value: str) -> str:
        return value

    def decode(self, value: str) -> str:
        return value

    @property
    def options(self) -> list[str]:
        return self._options
