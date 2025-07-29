#!/usr/bin/env python3
"""
Basic usage examples for divine-async-runner.

This script demonstrates fundamental usage patterns including:
- Simple command execution
- Output capture
- Error handling
- Process naming
"""

import anyio

from async_runner import run_process


async def simple_execution():
    """Demonstrate basic command execution."""
    print("=== Simple Command Execution ===")

    # Execute a simple command
    success = await run_process(["echo", "Hello, World!"])
    print(f"Echo command succeeded: {success}")

    # Execute a command that will fail
    success = await run_process(["ls", "/nonexistent-directory"])
    print(f"Failed command succeeded: {success}")


async def output_capture():
    """Demonstrate output capture and logging."""
    print("\n=== Output Capture ===")

    # Capture output from a command
    success = await run_process(
        ["python3", "-c", "print('Hello from Python'); import sys; print('Error message', file=sys.stderr)"],
        capture_output=True,
        process_name="Python Script",
    )
    print(f"Python script succeeded: {success}")


async def process_naming():
    """Demonstrate the importance of process naming for logging."""
    print("\n=== Process Naming ===")

    # Without meaningful name
    await run_process(["sleep", "0.1"], capture_output=True)

    # With meaningful name
    await run_process(["sleep", "0.1"], capture_output=True, process_name="Short Sleep")


async def error_handling():
    """Demonstrate proper error handling patterns."""
    print("\n=== Error Handling ===")

    commands = [
        (["echo", "This will work"], "Working Command"),
        (["false"], "Command that returns 1"),
        (["nonexistent-command"], "Command that doesn't exist"),
    ]

    for command, description in commands:
        print(f"\nTesting: {description}")
        try:
            success = await run_process(command, capture_output=True, process_name=description)
            if success:
                print("✅ Command succeeded")
            else:
                print("❌ Command failed")
        except Exception as e:  # noqa: BLE001
            print(f"🚨 Exception occurred: {e}")


async def main():
    """Run all examples."""
    print("Async Runner - Basic Usage Examples\n")

    await simple_execution()
    await output_capture()
    await process_naming()
    await error_handling()

    print("\n=== Examples Complete ===")


if __name__ == "__main__":
    anyio.run(main)
