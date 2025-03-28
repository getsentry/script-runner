from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseFunction(ABC):
    """Base class for all script functions."""

    @abstractmethod
    def execute(self, config: Dict[str, Any], *args, **kwargs) -> Any:
        """
        Execute the function with the given configuration and parameters.
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def validate_parameters(self, *args, **kwargs) -> bool:
        """
        Validate function parameters before execution.
        """
        return True

    def get_description(self) -> str:
        """
        Get function description from the docstring.
        """
        return self.__doc__ or ""


class ReadFunction(BaseFunction):
    """Base class for read-only functions."""

    def is_read_only(self) -> bool:
        """
        Indicates that this function only reads data.
        """
        return True


class WriteFunction(BaseFunction):
    """Base class for functions that modify data."""

    def is_read_only(self) -> bool:
        """
        Indicates that this function modifies data.

        Returns:
            bool: Always False for WriteFunction
        """
        return False

    def dry_run(self, config: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        """
        Simulate the execution without making actual changes.

        Args:
            config: Region-specific configuration
            *args, **kwargs: Function-specific parameters

        Returns:
            Dict[str, Any]: Description of what would be done
        """
        return {
            "would_execute": True,
            "parameters": {**kwargs},
            "description": "This is a dry run. No changes were made.",
        }
