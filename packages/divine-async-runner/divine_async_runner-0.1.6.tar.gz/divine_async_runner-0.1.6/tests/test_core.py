import subprocess
from unittest.mock import AsyncMock, patch

import pytest

from async_runner import configure_logger, core, run_process
from async_runner.core import DefaultLogger


class MockLogger:
    """Mock logger for testing."""

    def __init__(self):
        self.info_calls = []
        self.error_calls = []
        self.warning_calls = []

    def info(self, message: str) -> None:
        self.info_calls.append(message)

    def error(self, message: str) -> None:
        self.error_calls.append(message)

    def warning(self, message: str) -> None:
        self.warning_calls.append(message)


@pytest.mark.anyio
async def test_run_process_success():
    """Test that run_process works correctly when the process succeeds"""
    # Mock the process completion with successful return code
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.wait = AsyncMock()

    # Create a mock context manager that returns our mock process
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_process

    # Mock open_process to return our mocked context
    with patch("anyio.open_process", return_value=mock_context) as mock_open_process:
        result = await run_process(["echo", "Hello World"], process_name="test_process")

        # Verify the result
        assert result is True
        mock_open_process.assert_called_once_with(
            ["echo", "Hello World"], stdout=None, stderr=None, start_new_session=False
        )
        mock_process.wait.assert_called_once()


@pytest.mark.anyio
async def test_run_process_failure():
    """Test that run_process returns False when the process fails"""
    # Setup mock logger to capture error messages
    mock_logger = MockLogger()
    configure_logger(mock_logger)

    # Mock the process completion with non-zero return code
    mock_process = AsyncMock()
    mock_process.returncode = 1
    mock_process.wait = AsyncMock()

    # Create a mock context manager that returns our mock process
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_process

    # Mock open_process to return our mocked context
    with patch("anyio.open_process", return_value=mock_context) as mock_open_process:
        result = await run_process(["invalid_command"], process_name="test_process")

        # Verify the result
        assert result is False
        mock_open_process.assert_called_once()
        mock_process.wait.assert_called_once()
        assert "test_process failed with return code 1" in mock_logger.error_calls


@pytest.mark.anyio
async def test_run_process_with_capture_output():
    """Test that run_process correctly captures and logs output"""
    # Setup mock logger to capture messages
    mock_logger = MockLogger()
    configure_logger(mock_logger)

    # Create mock streams
    mock_stdout = AsyncMock()
    mock_stdout.__aiter__.return_value = [b"stdout line 1\n", b"stdout line 2\n"]

    mock_stderr = AsyncMock()
    mock_stderr.__aiter__.return_value = [b"stderr line 1\n", b"stderr line 2\n"]

    # Mock the process
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.wait = AsyncMock()
    mock_process.stdout = mock_stdout
    mock_process.stderr = mock_stderr

    # Create a mock context manager that returns our mock process
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_process

    # Mock open_process to return our mocked context
    with patch("anyio.open_process", return_value=mock_context) as mock_open_process:
        result = await run_process(["echo", "Hello World"], capture_output=True, process_name="test_process")

        # Verify the result
        assert result is True
        mock_open_process.assert_called_once_with(
            ["echo", "Hello World"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=False
        )

        # Verify that output was logged
        assert len(mock_logger.info_calls) >= 2
        assert len(mock_logger.error_calls) >= 2

        # Check the specific log messages
        assert "test_process STDOUT: stdout line 1" in mock_logger.info_calls
        assert "test_process STDOUT: stdout line 2" in mock_logger.info_calls
        assert "test_process STDERR: stderr line 1" in mock_logger.error_calls
        assert "test_process STDERR: stderr line 2" in mock_logger.error_calls


@pytest.mark.anyio
async def test_run_process_exception():
    """Test that run_process handles exceptions correctly"""
    # Setup mock logger to capture error messages
    mock_logger = MockLogger()
    configure_logger(mock_logger)

    # Setup mock to raise an exception
    with patch("anyio.open_process", side_effect=Exception("Mock exception")):
        result = await run_process(["echo", "Hello World"], process_name="test_process")

        # Verify the result
        assert result is False
        assert "Error running test_process: Mock exception" in mock_logger.error_calls


class MockCancelledError(Exception):
    """Mock exception to simulate task cancellation"""


@pytest.mark.anyio
async def test_run_process_cancellation():
    """Test that run_process handles cancellation correctly"""
    # Setup mock logger to capture warning messages
    mock_logger = MockLogger()
    configure_logger(mock_logger)

    # Create a mock for anyio's cancellation exception
    with patch("async_runner.core.anyio.get_cancelled_exc_class", return_value=MockCancelledError):
        cancel_exc = MockCancelledError("Task cancelled")

        # Setup mock to raise the cancellation exception
        with patch("anyio.open_process", side_effect=cancel_exc):
            with pytest.raises(MockCancelledError):
                await run_process(["echo", "Hello World"], process_name="test_process")

            # Verify logging
            assert "test_process execution cancelled" in mock_logger.warning_calls


@pytest.mark.anyio
async def test_read_stream_exception_handling():
    """Test that _read_stream handles exceptions correctly"""
    # Setup mock logger to capture error messages
    mock_logger = MockLogger()
    configure_logger(mock_logger)

    # Setup to trigger the exception inside _read_stream
    mock_stream = AsyncMock()
    mock_stream.__aiter__.side_effect = Exception("Stream error")

    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.wait = AsyncMock()
    mock_process.stdout = mock_stream
    mock_process.stderr = mock_stream

    # Create a mock context manager that returns our mock process
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_process

    # Mock open_process to return our mocked context
    with patch("anyio.open_process", return_value=mock_context):
        # Result not used in assertions
        await run_process(["echo", "Hello World"], capture_output=True, process_name="test_process")

        # Verify error was logged
        assert any("Error reading STDOUT from test_process: Stream error" in call for call in mock_logger.error_calls)
        assert any("Error reading STDERR from test_process: Stream error" in call for call in mock_logger.error_calls)


@pytest.mark.anyio
async def test_run_process_with_new_session():
    """Test that run_process works correctly with start_new_session=True"""
    # Mock the process completion with successful return code
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.wait = AsyncMock()

    # Create a mock context manager that returns our mock process
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_process

    # Mock open_process to return our mocked context
    with patch("anyio.open_process", return_value=mock_context) as mock_open_process:
        result = await run_process(["echo", "Hello World"], start_new_session=True, process_name="test_process")

        # Verify the result
        assert result is True
        mock_open_process.assert_called_once_with(
            ["echo", "Hello World"], stdout=None, stderr=None, start_new_session=True
        )
        mock_process.wait.assert_called_once()


def test_configure_logger():
    """Test that configure_logger works correctly"""
    # Create a mock logger
    mock_logger = MockLogger()

    # Configure it
    configure_logger(mock_logger)

    # Test that the logger is actually used by importing and checking the module
    # Verify the configured logger was applied
    assert core._logger is mock_logger


def test_default_logger():
    """Test the DefaultLogger class methods"""
    logger = DefaultLogger()

    # Test all methods exist and can be called (they print to stdout/stderr)
    logger.info("test info message")
    logger.error("test error message")
    logger.warning("test warning message")


@pytest.mark.anyio
async def test_empty_stdout_lines():
    """Test handling of empty lines in stdout/stderr streams"""
    # Setup mock logger to capture messages
    mock_logger = MockLogger()
    configure_logger(mock_logger)

    # Create mock streams with empty lines
    mock_stdout = AsyncMock()
    mock_stdout.__aiter__.return_value = [b"", b"valid line\n", b""]

    mock_stderr = AsyncMock()
    mock_stderr.__aiter__.return_value = [b"", b"error line\n", b""]

    # Mock the process
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.wait = AsyncMock()
    mock_process.stdout = mock_stdout
    mock_process.stderr = mock_stderr

    # Create a mock context manager that returns our mock process
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_process

    # Mock open_process to return our mocked context
    with patch("anyio.open_process", return_value=mock_context):
        result = await run_process(["echo", "test"], capture_output=True, process_name="test_process")

        # Verify the result
        assert result is True

        # Verify only non-empty lines were logged
        assert "test_process STDOUT: valid line" in mock_logger.info_calls
        assert "test_process STDERR: error line" in mock_logger.error_calls

        # Verify empty lines were not logged
        empty_stdout_logs = [
            call for call in mock_logger.info_calls if "STDOUT: " in call and call.endswith("STDOUT: ")
        ]
        empty_stderr_logs = [
            call for call in mock_logger.error_calls if "STDERR: " in call and call.endswith("STDERR: ")
        ]
        assert len(empty_stdout_logs) == 0
        assert len(empty_stderr_logs) == 0


@pytest.mark.anyio
async def test_decode_errors_handling():
    """Test handling of decode errors in stream reading"""
    # Setup mock logger to capture messages
    mock_logger = MockLogger()
    configure_logger(mock_logger)

    # Create mock streams with bytes that might cause decode issues
    mock_stdout = AsyncMock()
    # Use invalid UTF-8 bytes that should be handled with errors="replace"
    mock_stdout.__aiter__.return_value = [b"\xff\xfe invalid utf-8 \xff\n"]

    mock_stderr = AsyncMock()
    mock_stderr.__aiter__.return_value = [b"\xff\xfe stderr invalid \xff\n"]

    # Mock the process
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.wait = AsyncMock()
    mock_process.stdout = mock_stdout
    mock_process.stderr = mock_stderr

    # Create a mock context manager that returns our mock process
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_process

    # Mock open_process to return our mocked context
    with patch("anyio.open_process", return_value=mock_context):
        result = await run_process(["echo", "test"], capture_output=True, process_name="test_process")

        # Verify the result
        assert result is True

        # Verify that decode errors were handled (replaced with replacement chars)
        # The exact replacement characters may vary by system, but output should be logged
        assert len(mock_logger.info_calls) >= 1
        assert len(mock_logger.error_calls) >= 1
        assert any("test_process STDOUT:" in call for call in mock_logger.info_calls)
        assert any("test_process STDERR:" in call for call in mock_logger.error_calls)
