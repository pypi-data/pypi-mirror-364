import subprocess  # nosec B404: subprocess is used intentionally for process execution
from typing import Protocol

import anyio


class Logger(Protocol):
    """Protocol for logger interface."""

    def info(self, message: str) -> None:
        """Log info message."""
        ...

    def error(self, message: str) -> None:
        """Log error message."""
        ...

    def warning(self, message: str) -> None:
        """Log warning message."""
        ...


class DefaultLogger:
    """Default logger that prints to stdout/stderr."""

    def info(self, message: str) -> None:
        print(f"INFO: {message}")

    def error(self, message: str) -> None:
        print(f"ERROR: {message}")

    def warning(self, message: str) -> None:
        print(f"WARNING: {message}")


# Global logger instance
_logger: Logger = DefaultLogger()


def configure_logger(logger: Logger) -> None:
    """Configure a custom logger for the async runner.

    Args:
        logger: Logger instance that implements the Logger protocol
    """
    # Avoid using the global statement
    globals()["_logger"] = logger


async def run_process(
    command: list[str], *, capture_output: bool = False, start_new_session: bool = False, process_name: str = "Unknown"
) -> bool:
    """
    Unified process runner with configurable output handling.

    Args:
        command: Command and arguments to run
        capture_output: Whether to capture and log stdout/stderr
        start_new_session: Whether to start in a new session (useful for subprocesses)
        process_name: Name of the process for logging

    Returns:
        bool: True if process completed successfully
    """
    stdout = subprocess.PIPE if capture_output else None
    stderr = subprocess.PIPE if capture_output else None

    async def _read_stream(stream, log_method, stream_name):
        """Continuously reads from a stream and logs its output."""
        try:
            async for line in stream:
                text = line.decode(errors="replace").rstrip()
                if text:
                    log_method(f"{process_name} {stream_name}: {text}")
        except Exception as e:  # noqa: BLE001
            _logger.error(f"Error reading {stream_name} from {process_name}: {e}")

    try:
        async with await anyio.open_process(
            command, stdout=stdout, stderr=stderr, start_new_session=start_new_session
        ) as process:
            if capture_output:
                async with anyio.create_task_group() as tg:
                    tg.start_soon(_read_stream, process.stdout, _logger.info, "STDOUT")
                    tg.start_soon(_read_stream, process.stderr, _logger.error, "STDERR")

            await process.wait()
            if process.returncode != 0:
                _logger.error(f"{process_name} failed with return code {process.returncode}")
            return process.returncode == 0

    except anyio.get_cancelled_exc_class():
        _logger.warning(f"{process_name} execution cancelled")
        raise
    except Exception as e:  # noqa: BLE001
        _logger.error(f"Error running {process_name}: {e}")
        return False
