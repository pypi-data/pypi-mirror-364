# API Reference

Complete API documentation for divine-async-runner.

## Core Functions

### `run_process(command, *, capture_output=False, start_new_session=False, process_name="Unknown")`

Run a subprocess asynchronously with robust error handling.

**Parameters:**
- `command` (List[str]): Command and arguments to execute
- `capture_output` (bool, optional): Whether to capture and log stdout/stderr. Defaults to False.
- `start_new_session` (bool, optional): Whether to start in a new session. Defaults to False.
- `process_name` (str, optional): Name for logging purposes. Defaults to "Unknown".

**Returns:**
- `bool`: True if process completed successfully (return code 0), False otherwise

**Raises:**
- The function handles most exceptions internally and returns False for errors
- Cancellation exceptions (from anyio) are re-raised to allow proper cleanup

**Example:**
```python
import asyncio
from async_runner import run_process

async def main():
    # Simple execution
    success = await run_process(["echo", "Hello World"])
    print(f"Success: {success}")
    
    # With output capture
    success = await run_process(
        ["python", "--version"],
        capture_output=True,
        process_name="Python Version Check"
    )
    
    # Start in new session (useful for daemons)
    success = await run_process(
        ["long-running-daemon"],
        start_new_session=True,
        process_name="Background Service"
    )

asyncio.run(main())
```

### `configure_logger(logger)`

Configure a custom logger for the async runner.

**Parameters:**
- `logger`: Logger instance implementing the Logger protocol (info, error, warning methods)

**Returns:**
- None

**Example:**
```python
import logging
from async_runner import configure_logger

class CustomLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)

# Configure custom logger
configure_logger(CustomLogger())
```

## Protocol Interfaces

### `Logger` Protocol

Interface that custom loggers must implement.

**Methods:**
- `info(message: str) -> None`: Log info-level message
- `error(message: str) -> None`: Log error-level message  
- `warning(message: str) -> None`: Log warning-level message

## Built-in Classes

### `DefaultLogger`

Default logger implementation that prints to stdout/stderr.

**Methods:**
- `info(message: str)`: Prints "INFO: {message}"
- `error(message: str)`: Prints "ERROR: {message}"
- `warning(message: str)`: Prints "WARNING: {message}"

## Error Handling

The library handles various error scenarios gracefully:

### Process Failures
- Non-zero exit codes are logged and return False
- Process execution errors are caught and logged

### Stream Reading Errors
- Decode errors are handled with `errors="replace"`
- Stream iteration exceptions are caught and logged
- Empty lines are filtered out automatically

### Cancellation Handling
- anyio cancellation exceptions are properly re-raised
- Cleanup logging is performed before re-raising

### General Exceptions
- All other exceptions are caught and logged
- Function returns False for any unexpected errors

## Output Handling

### Without Output Capture
```python
# No output capture - stdout/stderr go to terminal
success = await run_process(["ls", "-la"])
```

### With Output Capture
```python
# Output is captured and logged line by line
success = await run_process(
    ["ls", "-la"],
    capture_output=True,
    process_name="Directory Listing"
)
```

Output format in logs:
- stdout: `{process_name} STDOUT: {line}`
- stderr: `{process_name} STDERR: {line}`

## Session Management

### Regular Process
```python
# Process runs in same session as parent
success = await run_process(["python", "script.py"])
```

### New Session Process
```python
# Process runs in new session (detached from parent)
success = await run_process(
    ["daemon-process"],
    start_new_session=True
)
```

New sessions are useful for:
- Background services/daemons
- Processes that should survive parent termination
- Avoiding signal propagation from parent

## Integration Examples

### With Custom Logging
```python
import structlog
from async_runner import configure_logger, run_process

class StructlogLogger:
    def __init__(self):
        self.logger = structlog.get_logger()
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)

configure_logger(StructlogLogger())
```

### Error Recovery Patterns
```python
async def retry_process(command, max_retries=3):
    for attempt in range(max_retries):
        success = await run_process(
            command,
            process_name=f"Attempt {attempt + 1}"
        )
        if success:
            return True
        await asyncio.sleep(1)  # Brief delay
    return False
```

### Concurrent Execution
```python
async def run_multiple():
    tasks = [
        run_process(["task1"], process_name="Task 1"),
        run_process(["task2"], process_name="Task 2"),
        run_process(["task3"], process_name="Task 3"),
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## Best Practices

1. **Always use meaningful process names** for easier debugging
2. **Enable output capture for debugging** complex processes
3. **Handle cancellation properly** in calling code
4. **Use new sessions judiciously** - only when needed
5. **Configure custom loggers** for production environments
6. **Test both success and failure scenarios** in your code
7. **Consider timeout handling** in your application logic

## Migration from subprocess

### Before (blocking)
```python
import subprocess

result = subprocess.run(["echo", "hello"], capture_output=True)
success = result.returncode == 0
```

### After (async)
```python
from async_runner import run_process

success = await run_process(
    ["echo", "hello"],
    capture_output=True,
    process_name="Echo Test"
)
```

Benefits of async_runner:
- Non-blocking execution
- Better error handling
- Integrated logging
- Stream processing
- Cancellation support
- Consistent interface