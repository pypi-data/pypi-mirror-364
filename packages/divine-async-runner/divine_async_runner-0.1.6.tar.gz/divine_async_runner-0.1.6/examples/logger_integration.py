#!/usr/bin/env python3
"""
Logger integration examples for divine-async-runner.

This script demonstrates how to integrate divine-async-runner with various
logging systems and patterns.
"""

import logging
import sys
from datetime import datetime

import anyio

from async_runner import configure_logger, run_process


class StandardLogger:
    """Integration with Python's standard logging module."""

    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Add console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)


class StructuredLogger:
    """Example of structured logging integration."""

    def __init__(self, component: str):
        self.component = component

    def _log(self, level: str, message: str) -> None:
        timestamp = datetime.now().isoformat()
        structured_msg = {"timestamp": timestamp, "component": self.component, "level": level, "message": message}
        print(f"STRUCTURED: {structured_msg}")

    def info(self, message: str) -> None:
        self._log("INFO", message)

    def error(self, message: str) -> None:
        self._log("ERROR", message)

    def warning(self, message: str) -> None:
        self._log("WARNING", message)


class SilentLogger:
    """Logger that suppresses all output."""

    def info(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass

    def warning(self, message: str) -> None:
        pass


async def standard_logging_example():
    """Demonstrate integration with Python's logging module."""
    print("=== Standard Logging Integration ===")

    # Configure standard logger
    standard_logger = StandardLogger("async_runner_demo")
    configure_logger(standard_logger)

    # Run some commands
    await run_process(
        ["python3", "-c", "print('Standard logging output')"], capture_output=True, process_name="Standard Logger Test"
    )


async def structured_logging_example():
    """Demonstrate structured logging integration."""
    print("\n=== Structured Logging Integration ===")

    # Configure structured logger
    structured_logger = StructuredLogger("process_runner")
    configure_logger(structured_logger)

    # Run some commands
    await run_process(["echo", "Structured logging test"], capture_output=True, process_name="Structured Test")


async def silent_logging_example():
    """Demonstrate silent logging for quiet operation."""
    print("\n=== Silent Logging (No Output) ===")

    # Configure silent logger
    silent_logger = SilentLogger()
    configure_logger(silent_logger)

    # Run commands silently
    success = await run_process(
        ["echo", "This output will be suppressed"], capture_output=True, process_name="Silent Test"
    )
    print(f"Silent command completed: {success}")


async def logger_switching_example():
    """Demonstrate switching between different loggers."""
    print("\n=== Logger Switching ===")

    loggers = [
        ("Standard", StandardLogger("switcher")),
        ("Structured", StructuredLogger("switcher")),
        ("Silent", SilentLogger()),
    ]

    for logger_name, logger in loggers:
        print(f"\nUsing {logger_name} logger:")
        configure_logger(logger)

        await run_process(
            ["echo", f"Message from {logger_name} logger"], capture_output=True, process_name=f"{logger_name} Test"
        )


async def main():
    """Run all logger integration examples."""
    print("Async Runner - Logger Integration Examples\n")

    await standard_logging_example()
    await structured_logging_example()
    await silent_logging_example()
    await logger_switching_example()

    print("\n=== Logger Integration Examples Complete ===")


if __name__ == "__main__":
    anyio.run(main)
