from abc import ABC, abstractmethod
from typing import Any

class Logger(ABC):
    """Base abstract class for all algorithms.
    """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def log(self, *args: Any, **kwargs: Any) -> None:
        """Logs the input.
        """
        pass

    @abstractmethod
    def error(self, *args: Any, **kwargs: Any) -> None:
        """Errors the input.
        """
        pass

class StdOutLogger(Logger):
    def log(self, *args: Any, **kwargs: Any) -> None:
        print(*args, **kwargs)

    def error(self, *args: Any, **kwargs: Any) -> None:
        print('\033[91m', *args, '\033[0m', **kwargs)
