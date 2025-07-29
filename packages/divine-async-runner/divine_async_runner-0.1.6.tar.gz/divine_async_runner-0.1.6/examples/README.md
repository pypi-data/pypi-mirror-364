# Examples

This directory contains practical examples demonstrating how to use divine-async-runner in real-world scenarios.

## Available Examples

### [basic_usage.py](basic_usage.py)
Simple examples showing fundamental usage patterns:
- Basic command execution
- Output capture
- Error handling
- Process naming

### [logger_integration.py](logger_integration.py)
Demonstrates how to integrate divine-async-runner with existing logging systems:
- Custom logger configuration
- Structured logging
- Log level control
- Integration with Python's logging module

### [advanced_usage.py](advanced_usage.py)
Advanced patterns and use cases:
- Starting processes in new sessions
- Running multiple commands concurrently
- Process management patterns
- Error recovery strategies

## Running the Examples

Each example is a standalone Python script that can be run directly:

```bash
# Install the package first
cd /path/to/async-runner
pip install -e .

# Run examples
python examples/basic_usage.py
python examples/logger_integration.py
python examples/advanced_usage.py
```

## Integration Patterns

These examples show common integration patterns that you can adapt for your own projects:

1. **Drop-in Replacement**: How to replace existing subprocess calls
2. **Custom Logging**: Integrating with your application's logging
3. **Error Handling**: Robust error handling strategies
4. **Concurrent Execution**: Running multiple processes efficiently