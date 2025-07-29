"""Evaluation runner for collecting and executing doteval functions."""

import asyncio
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pytest
from rich.console import Console

from doteval.fixtures import setup_fixtures_for_evaluation
from doteval.progress import ConcurrentProgressManager

console = Console()


class EvalItem:
    """Represents a discovered evaluation function with pytest integration.

    This class encapsulates an evaluation function discovered through pytest's
    collection mechanism, including any parametrization information and metadata.
    Each parametrized combination becomes a separate EvalItem instance.
    """

    def __init__(
        self,
        name: str,
        function: Callable,
        path: Path,
        module,
        parametrized_name: str,
        params: Optional[Any] = None,
    ):
        """Initialize an EvalItem.

        Args:
            name: Base name of the evaluation function
            function: The actual evaluation function to execute
            path: Path to the file containing the evaluation
            module: Python module containing the evaluation
            parametrized_name: Full name including parameter values (e.g., "eval_test[param1]")
            params: Optional pytest callspec containing parameter information
        """
        self.name = name
        self.function = function
        self.path = path
        self.module = module
        self.parametrized_name = parametrized_name
        self.params = params

        # Extract parameters from pytest callspec if available
        self.parameters: Dict[str, Any] = {}
        if params and hasattr(params, "params"):
            self.parameters = dict(params.params)


def discover_evaluations(
    path: str = ".",
    pattern: str = "eval_*.py",
    keyword: Optional[str] = None,
    marker: Optional[str] = None,
) -> List[EvalItem]:
    """Use pytest's collection API to discover evaluations.

    Args:
        path: Directory path to search for evaluation files (defaults to current directory)
        pattern: File pattern to match (defaults to "eval_*.py")
        keyword: Optional pytest keyword filter to apply during collection
        marker: Optional pytest marker filter to apply during collection

    Returns:
        List of EvalItem objects representing discovered evaluations, including
        parametrized variations as separate items
    """

    # Collect using session.items which contains only filtered items
    collected_items = []

    class CollectorPlugin:
        def pytest_configure(self, config):
            # Configure pytest to collect eval_*.py files and eval_* functions
            config.addinivalue_line("python_files", "eval_*.py")
            config.addinivalue_line("python_functions", "eval_*")

        def pytest_collection_finish(self, session):
            # session.items contains only items that passed keyword/marker filtering
            collected_items.extend(session.items)

    # Build args for pytest
    args = [path, "--collect-only", "-q"]
    if keyword:
        args.extend(["-k", keyword])
    if marker:
        args.extend(["-m", marker])

    # Run pytest with our plugin
    pytest.main(args, plugins=[CollectorPlugin()])

    # Extract evaluations
    evaluations = []
    for item in collected_items:
        # Only include functions that start with "eval_" (exclude test_ functions)
        function_name = item.obj.__name__
        if not function_name.startswith("eval_"):
            continue

        evaluations.append(
            EvalItem(
                name=item.name,
                function=item.obj,
                path=Path(str(getattr(item, "fspath", getattr(item, "path", "")))),
                module=item.module,
                parametrized_name=item.nodeid,
                params=getattr(item, "callspec", None),
            )
        )

    return evaluations


async def run_sequential(
    path: str = ".",
    keyword: Optional[str] = None,
    marker: Optional[str] = None,
    samples: Optional[int] = None,
    experiment_name: Optional[str] = None,
) -> None:
    """Run evaluations sequentially, one after another.

    Args:
        path: Directory path to search for evaluation files
        keyword: Optional pytest keyword filter
        marker: Optional pytest marker filter
        samples: Optional limit on number of samples per evaluation
        experiment_name: Optional experiment name for result storage
    """
    eval_items = discover_evaluations(path, keyword=keyword, marker=marker)

    for item in eval_items:
        console.print(f"\n🔄 Running {item.parametrized_name}...")
        try:
            await _execute_evaluation(item, samples, experiment_name)
        except Exception:
            pass  # Errors are already handled by _execute_evaluation


async def run_concurrent(
    path: str = ".",
    keyword: Optional[str] = None,
    marker: Optional[str] = None,
    samples: Optional[int] = None,
    experiment_name: Optional[str] = None,
    max_concurrent: Optional[int] = None,
) -> None:
    """Run evaluations concurrently with progress tracking.

    Supports parametrized evaluations - each parameter combination
    becomes a separate concurrent execution with its own fixtures.

    Args:
        path: Directory path to search for evaluation files
        keyword: Optional pytest keyword filter
        marker: Optional pytest marker filter
        samples: Optional limit on number of samples per evaluation
        experiment_name: Optional experiment name for result storage
        max_concurrent: Maximum number of evaluations to run concurrently (defaults to unlimited)
    """
    eval_items = discover_evaluations(path, keyword=keyword, marker=marker)

    if not eval_items:
        console.print("No evaluations found.")
        return

    # Default to unlimited concurrency
    if max_concurrent is None:
        max_concurrent = len(eval_items)

    semaphore = asyncio.Semaphore(max_concurrent)
    evaluation_names = [item.name for item in eval_items]

    async def run_with_semaphore(item, progress_manager):
        async with semaphore:
            try:
                await _execute_evaluation(
                    item, samples, experiment_name, progress_manager
                )
                progress_manager.finalize_evaluation(item.name)
            except Exception:
                progress_manager.finalize_evaluation(item.name, error=True)

    # Run with progress bars
    with ConcurrentProgressManager(
        evaluation_names, samples=samples
    ) as progress_manager:
        tasks = [run_with_semaphore(item, progress_manager) for item in eval_items]
        await asyncio.gather(*tasks)


async def _execute_evaluation(
    item: EvalItem,
    samples: Optional[int] = None,
    experiment_name: Optional[str] = None,
    progress_manager=None,
) -> None:
    """Execute a single evaluation function with fixtures and parameters.

    This function handles:
    - Setting up fixtures based on the evaluation's parameter values
    - Merging fixture results with evaluation parameters
    - Calling the evaluation function with all required arguments
    - Handling both sync and async evaluation functions

    Args:
        item: EvalItem containing the evaluation function and its metadata
        samples: Optional limit on number of samples for this evaluation
        experiment_name: Optional experiment name for result storage
        progress_manager: Optional progress manager for progress tracking
    """
    # Set up fixtures for this evaluation
    # Pass parametrized values to fixtures so they can receive their params
    fixture_kwargs = await setup_fixtures_for_evaluation(item.function, item.parameters)

    # Use fixture results as primary kwargs
    # Only add non-fixture parameters to avoid overriding fixture results
    all_kwargs = fixture_kwargs.copy()
    for param_name, param_value in item.parameters.items():
        if param_name not in fixture_kwargs:
            # Only add parameters that aren't fixtures
            all_kwargs[param_name] = param_value

    result = item.function(
        evaluation_name=item.name,
        experiment_name=experiment_name,
        samples=samples,
        progress_manager=progress_manager,
        **all_kwargs,
    )

    if asyncio.iscoroutine(result):
        await result
