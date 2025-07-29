# Async Runner

[![PyPI version](https://badge.fury.io/py/divine-async-runner.svg)](https://badge.fury.io/py/divine-async-runner)
[![Python versions](https://img.shields.io/pypi/pyversions/divine-async-runner.svg)](https://pypi.org/project/divine-async-runner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/divinescreener/divine-async-runner)
[![Security Scan](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/divinescreener/divine-async-runner)

A unified async process runner with configurable output handling and robust error management. Built on [anyio](https://github.com/agronholm/anyio) for compatibility with asyncio and trio.

## ✨ Features

- 🚀 **Async Process Execution**: Built on anyio for compatibility with asyncio and trio
- 📝 **Configurable Output Handling**: Choose whether to capture and log stdout/stderr
- 🛡️ **Robust Error Management**: Comprehensive exception handling and process failure detection  
- 🔧 **Custom Logger Support**: Integrate with any logging infrastructure via simple protocol
- 🔄 **Session Control**: Option to start processes in new sessions (useful for daemons)
- 🎯 **Clean API**: Single `run_process()` function for all your subprocess needs
- ✅ **100% Test Coverage**: Thoroughly tested with both asyncio and trio backends
- 🐍 **Type Safe**: Full type hints for better IDE support and fewer runtime errors

## 🤔 Why Async Runner?

### The Problem
Running subprocesses in async Python applications is surprisingly complex:
- Output streaming requires careful task management
- Error handling needs to cover multiple failure modes
- Resource cleanup must be guaranteed
- Different async libraries (asyncio/trio) have different APIs

### Our Solution
Async Runner provides a battle-tested, production-ready solution:

```python
# Instead of this complex code:
try:
    async with await anyio.open_process(cmd) as process:
        async with anyio.create_task_group() as tg:
            async def read_stream(stream, name):
                async for line in stream:
                    print(f"{name}: {line.decode().strip()}")
            
            if process.stdout:
                tg.start_soon(read_stream, process.stdout, "stdout")
            if process.stderr:
                tg.start_soon(read_stream, process.stderr, "stderr")
        
        await process.wait()
except Exception as e:
    print(f"Process failed: {e}")

# Just use this:
success = await run_process(cmd, capture_output=True)
```

## 📦 Installation

```bash
# Using pip
pip install divine-async-runner

# Using poetry
uv add divine-async-runner

# For development
git clone https://github.com/divinescreener/divine-async-runner
cd divine-async-runner
uv sync
```

### Requirements
- Python 3.13+
- anyio (automatically installed)
- trio (optional, for trio backend support)

## 🚀 Quick Start

```python
import anyio
from async_runner import run_process

async def main():
    # Run a simple command
    success = await run_process(["echo", "Hello, World!"])
    print(f"Success: {success}")
    
    # Capture output
    await run_process(
        ["python3", "--version"],
        capture_output=True,
        process_name="Python Version Check"
    )

anyio.run(main())
```

## 📖 Usage Examples

### Basic Command Execution

```python
import anyio
from async_runner import run_process

async def main():
    # Simple command
    success = await run_process(["echo", "Hello World"])
    
    # Command with multiple arguments
    success = await run_process(["git", "status", "--porcelain"])
    
    # Use process_name for better logging
    success = await run_process(
        ["npm", "install"],
        process_name="NPM Install"
    )

anyio.run(main())
```

### Capturing and Processing Output

```python
import anyio
from async_runner import run_process

async def main():
    # Output will be logged line by line as it arrives
    success = await run_process(
        ["python3", "-c", """
import time
for i in range(5):
    print(f'Progress: {i+1}/5')
    time.sleep(0.5)
        """],
        capture_output=True,
        process_name="Progress Monitor"
    )
    
    # Error output is captured separately
    await run_process(
        ["python3", "-c", "import sys; sys.stderr.write('Error occurred!')"],
        capture_output=True,
        process_name="Error Example"
    )

anyio.run(main())
```

### Custom Logger Integration

```python
import anyio
import logging
from async_runner import run_process, configure_logger

class CustomLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)

async def main():
    # Configure custom logger
    configure_logger(CustomLogger())
    
    # Run process with custom logging
    success = await run_process(
        ["python3", "-c", "print('Hello from Python')"],
        capture_output=True,
        process_name="Python Script"
    )

anyio.run(main())
```

### Advanced Process Management

```python
import anyio
from async_runner import run_process

async def deploy_service():
    """Example deployment workflow"""
    
    # Run tests first
    if not await run_process(
        ["pytest", "tests/"],
        capture_output=True,
        process_name="Unit Tests"
    ):
        print("❌ Tests failed, aborting deployment")
        return False
    
    # Build the application
    if not await run_process(
        ["docker", "build", "-t", "myapp:latest", "."],
        capture_output=True,
        process_name="Docker Build"
    ):
        print("❌ Build failed")
        return False
    
    # Start the service in a new session
    success = await run_process(
        ["docker", "run", "-d", "-p", "8080:8080", "myapp:latest"],
        start_new_session=True,
        process_name="Service Startup"
    )
    
    print("✅ Deployment complete!" if success else "❌ Deployment failed")
    return success

async def main():
    await deploy_service()

anyio.run(main())
```

### Running Multiple Processes Concurrently

```python
import anyio
from async_runner import run_process

async def main():
    # Run multiple processes concurrently using anyio task groups
    results = []
    
    async with anyio.create_task_group() as tg:
        async def run_task(task_name, task_num):
            result = await run_process(
                ["python3", "-c", f"import time; time.sleep(1); print('Task {task_num}')"], 
                capture_output=True, 
                process_name=task_name
            )
            results.append(result)
        
        # All three will run in parallel
        tg.start_soon(run_task, "Task 1", 1)
        tg.start_soon(run_task, "Task 2", 2)
        tg.start_soon(run_task, "Task 3", 3)
    
    print(f"All tasks completed. Success: {all(results)}")

anyio.run(main())
```

### Using with Trio

```python
import trio
from async_runner import run_process

async def main():
    # Works seamlessly with trio
    success = await run_process(
        ["echo", "Hello from Trio!"],
        capture_output=True,
        process_name="Trio Example"
    )
    print(f"Success: {success}")

trio.run(main)
```

## 📚 API Reference

### `run_process()`

```python
async def run_process(
    command: list[str],
    *,
    capture_output: bool = False,
    start_new_session: bool = False,
    process_name: str = "Unknown"
) -> bool
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | `list[str]` | *required* | Command and arguments to execute |
| `capture_output` | `bool` | `False` | Whether to capture and log stdout/stderr |
| `start_new_session` | `bool` | `False` | Whether to start process in a new session |
| `process_name` | `str` | `"Unknown"` | Name for logging identification |

**Returns:**
- `bool`: `True` if process completed successfully (return code 0), `False` otherwise

**Raises:**
- Re-raises `anyio.get_cancelled_exc_class()` if the task is cancelled

### `configure_logger()`

```python
def configure_logger(logger: Logger) -> None
```

Configure a custom logger for all process output.

**Parameters:**
- `logger`: Object implementing the `Logger` protocol with `info()`, `error()`, and `warning()` methods

## 🛡️ Error Handling

Async Runner provides comprehensive error handling:

```python
import anyio
from async_runner import run_process, configure_logger

class ErrorTracker:
    """Example error tracking logger"""
    def __init__(self):
        self.errors = []
    
    def info(self, msg: str): 
        print(f"ℹ️  {msg}")
    
    def error(self, msg: str): 
        print(f"❌ {msg}")
        self.errors.append(msg)
    
    def warning(self, msg: str): 
        print(f"⚠️  {msg}")

async def main():
    tracker = ErrorTracker()
    configure_logger(tracker)
    
    # Command not found
    await run_process(["nonexistent-command"], process_name="Missing Command")
    
    # Non-zero exit code
    await run_process(["python3", "-c", "exit(1)"], process_name="Exit Code 1")
    
    # Permission denied (example)
    await run_process(["cat", "/etc/shadow"], process_name="Permission Test")
    
    print(f"\nTotal errors encountered: {len(tracker.errors)}")

anyio.run(main())
```

### Handled Error Types

1. **Process Failures**: Non-zero exit codes are logged with the return code
2. **Command Not Found**: Logged as process execution errors
3. **Stream Reading Errors**: Handled gracefully with error logging
4. **Task Cancellation**: Properly propagated with warning log
5. **Resource Cleanup**: Guaranteed even on exceptions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/divinescreener/divine-async-runner
cd divine-async-runner

# Install dependencies
uv sync

# Set up pre-commit hooks
./setup-pre-commit.sh

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run mypy src
```

## 📂 More Examples

Explore the [`examples/`](examples/) directory for complete, runnable examples:

| Example | Description |
|---------|-------------|
| [`basic_usage.py`](examples/basic_usage.py) | Simple subprocess execution patterns |
| [`advanced_usage.py`](examples/advanced_usage.py) | Concurrent execution, retries, and pipelines |
| [`logger_integration.py`](examples/logger_integration.py) | Custom logger implementations |

## 🔒 Security

- No shell injection vulnerabilities (command passed as list)
- Comprehensive error handling prevents resource leaks
- Regular security scanning with Bandit and Safety
- See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built on the excellent [anyio](https://github.com/agronholm/anyio) library
- Inspired by the complexity of subprocess handling in async contexts
- Thanks to all contributors and users

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/divinescreener">DIVINE</a>
</p>