"""A unified async process runner with configurable output handling and robust error management."""

from .core import configure_logger, run_process

__version__ = "0.1.0"
__all__ = ["configure_logger", "run_process"]
