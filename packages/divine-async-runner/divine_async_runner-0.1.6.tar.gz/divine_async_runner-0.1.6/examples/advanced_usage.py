#!/usr/bin/env python3
"""
Advanced usage examples for divine-async-runner.

This script demonstrates advanced patterns including:
- Starting processes in new sessions
- Running multiple commands concurrently
- Process management patterns
- Error recovery strategies
"""

import anyio

from async_runner import run_process


async def new_session_example():
    """Demonstrate starting processes in new sessions."""
    print("=== New Session Example ===")

    # Start a process in a new session (useful for daemons/background processes)
    success = await run_process(
        [
            "python3",
            "-c",
            "import time; print('Background process started'); time.sleep(0.5); print('Background process done')",
        ],
        start_new_session=True,
        capture_output=True,
        process_name="Background Process",
    )
    print(f"Background process completed: {success}")


async def concurrent_execution():
    """Demonstrate running multiple processes concurrently."""
    print("\n=== Concurrent Execution ===")

    # Run all tasks concurrently using anyio task groups
    print("Starting concurrent tasks...")
    results = []

    async with anyio.create_task_group() as tg:
        for i in range(1, 4):

            async def run_task(task_num):
                try:
                    result = await run_process(
                        ["python3", "-c", f"import time; time.sleep(0.{task_num}); print(f'Task {task_num} complete')"],
                        capture_output=True,
                        process_name=f"Task {task_num}",
                    )
                    results.append((task_num, result))
                except Exception as e:  # noqa: BLE001
                    results.append((task_num, e))

            tg.start_soon(run_task, i)

    # Sort results by task number and check them
    results.sort(key=lambda x: x[0])
    for task_num, result in results:
        if isinstance(result, Exception):
            print(f"Task {task_num} failed with exception: {result}")
        else:
            print(f"Task {task_num} succeeded: {result}")


async def error_recovery_example():
    """Demonstrate error recovery strategies."""
    print("\n=== Error Recovery Strategies ===")

    # Strategy 1: Retry failed commands
    async def retry_command(command, max_retries=3):
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1}/{max_retries}")
            success = await run_process(command, capture_output=True, process_name=f"Retry Attempt {attempt + 1}")
            if success:
                print("✅ Command succeeded")
                return True
            if attempt < max_retries - 1:
                print("❌ Command failed, retrying...")
                await anyio.sleep(0.1)  # Brief delay before retry

        print("❌ All retry attempts failed")
        return False

    # Test with a command that randomly fails
    await retry_command(["python3", "-c", "import random; exit(0 if random.random() > 0.7 else 1)"])


async def batch_processing_example():
    """Demonstrate batch processing patterns."""
    print("\n=== Batch Processing ===")

    # Process a batch of files (simulated)
    files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]

    async def process_file(filename):
        """Simulate file processing."""
        return await run_process(
            ["python3", "-c", f"print(f'Processing {filename}'); import time; time.sleep(0.1)"],
            capture_output=True,
            process_name=f"Process {filename}",
        )

    # Process files in batches of 2
    batch_size = 2
    for i in range(0, len(files), batch_size):
        batch = files[i : i + batch_size]
        print(f"Processing batch: {batch}")

        # Process batch concurrently using anyio task groups
        batch_results = []
        results_dict = {}

        async with anyio.create_task_group() as tg:
            for filename in batch:

                def make_batch_processor(fname):
                    async def process_batch_file():
                        result = await process_file(fname)
                        results_dict[fname] = result  # noqa: B023

                    return process_batch_file

                tg.start_soon(make_batch_processor(filename))

        batch_results = [results_dict[filename] for filename in batch]
        print(f"Batch results: {batch_results}")


async def pipeline_example():
    """Demonstrate pipeline processing."""
    print("\n=== Pipeline Processing ===")

    # Simulate a data processing pipeline
    steps = [
        (["echo", "raw_data"], "Data Ingestion"),
        (["python3", "-c", "print('cleaned_data')"], "Data Cleaning"),
        (["python3", "-c", "print('processed_data')"], "Data Processing"),
        (["python3", "-c", "print('final_output')"], "Final Output"),
    ]

    print("Running pipeline steps sequentially...")
    pipeline_success = True

    for i, (command, step_name) in enumerate(steps, 1):
        print(f"Step {i}: {step_name}")
        success = await run_process(command, capture_output=True, process_name=step_name)

        if not success:
            print(f"❌ Pipeline failed at step {i}: {step_name}")
            pipeline_success = False
            break
        print(f"✅ Step {i} completed successfully")

    if pipeline_success:
        print("🎉 Pipeline completed successfully!")


async def resource_monitoring_example():
    """Demonstrate monitoring resource-intensive processes."""
    print("\n=== Resource Monitoring ===")

    # Simulate monitoring a resource-intensive process
    async def monitor_process():
        """Monitor a long-running process."""
        async with anyio.create_task_group() as tg:

            async def run_long_process():
                return await run_process(
                    ["python3", "-c", "import time; [print(f'Working... {i}') or time.sleep(0.1) for i in range(5)]"],
                    capture_output=True,
                    process_name="Long Running Process",
                )

            tg.start_soon(run_long_process)

            # Simulate monitoring loop in parallel
            async def monitor():
                for _ in range(3):
                    print("📊 Monitoring process...")
                    await anyio.sleep(0.2)

            tg.start_soon(monitor)

        print("Process completed: True")

    await monitor_process()


async def main():
    """Run all advanced usage examples."""
    print("Async Runner - Advanced Usage Examples\n")

    await new_session_example()
    await concurrent_execution()
    await error_recovery_example()
    await batch_processing_example()
    await pipeline_example()
    await resource_monitoring_example()

    print("\n=== Advanced Examples Complete ===")


if __name__ == "__main__":
    anyio.run(main)
