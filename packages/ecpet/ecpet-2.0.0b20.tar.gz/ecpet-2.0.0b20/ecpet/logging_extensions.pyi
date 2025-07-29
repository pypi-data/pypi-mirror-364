# logging_extensions.pyi
import logging
from typing import Any

# Extend the logging module with custom levels
INSANE: int
NORMAL: int

class Logger(logging.Logger):
    def insane(self, message: Any, *args: Any, **kwargs: Any) -> None: ...
    def normal(self, message: Any, *args: Any, **kwargs: Any) -> None: ...
