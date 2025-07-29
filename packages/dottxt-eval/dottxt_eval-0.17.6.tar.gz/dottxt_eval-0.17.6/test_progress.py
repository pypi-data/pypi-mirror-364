#!/usr/bin/env python3
"""Test script to verify progress bars work with concurrent execution."""

import asyncio
import tempfile
from pathlib import Path

from doteval.runner import run_concurrent


def create_test_files():
    """Create test evaluation files."""
    tmpdir = Path(tempfile.mkdtemp())

    # Create multiple test evaluation files
    for i in range(5):
        eval_file = tmpdir / f"eval_progress_test_{i}.py"
        if i == 2:  # Make one evaluation fail to test error display
            eval_file.write_text(
                f"""
import asyncio

def eval_progress_test_{i}(evaluation_name, experiment_name, samples, **kwargs):
    # Simulate some work
    import time
    time.sleep(0.3)  # Simulate work

    # This one will fail
    raise ValueError("Test error for evaluation {i}")

# eval_progress_test functions will be discovered based on naming convention
"""
            )
        else:
            eval_file.write_text(
                f"""
import asyncio

def eval_progress_test_{i}(evaluation_name, experiment_name, samples, **kwargs):
    # Simulate some work
    import time
    time.sleep(0.3)  # Simulate work

    class MockResult:
        def __init__(self):
            self.summary = {{"accuracy": 0.{i}}}
    return MockResult()

# eval_progress_test functions will be discovered based on naming convention
"""
            )

    return tmpdir


async def test_concurrent_with_progress():
    """Test concurrent execution with progress bars."""
    tmpdir = create_test_files()

    print("Testing concurrent execution with progress bars:")
    print(f"Test directory: {tmpdir}")

    # Run with progress bars
    results = await run_concurrent(str(tmpdir), max_concurrent=2, show_progress=True)

    print(f"\\nCompleted {len(results)} evaluations:")
    for name, result in results:
        if isinstance(result, Exception):
            print(f"  ❌ {name}: {result}")
        else:
            print(f"  ✅ {name}: Success")

    # Clean up
    import shutil

    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    asyncio.run(test_concurrent_with_progress())
