from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from doteval.models import Record


def get_dataset_info(dataset):
    """Extract dataset information for progress display"""
    info = {"name": "Dataset", "total_rows": None}

    # Check if this is a Dataset instance from the registry
    if hasattr(dataset, "name") and hasattr(dataset, "num_rows"):
        info.update(
            {
                "name": dataset.name.upper(),
                "total_rows": dataset.num_rows,
            }
        )
    # Fallback to size estimation for direct iterators
    elif hasattr(dataset, "__len__"):
        try:
            info["total_rows"] = len(dataset)
        except (TypeError, AttributeError):
            pass

    return info


def calculate_metrics(results: List[Record]) -> Dict[str, Any]:
    """Unified metrics calculation for all progress trackers."""
    if not results:
        return {}

    # First pass: determine the expected score structure from successful results
    expected_scores = []
    for res in results:
        if res.error is None and res.result.scores:
            expected_scores = [
                (score.name, score.metrics) for score in res.result.scores
            ]
            break

    # Recalculate metrics from all results so far
    aggregated_results: Dict[str, Dict[Any, Any]] = defaultdict(
        lambda: defaultdict(list)
    )
    for res in results:
        if res.error is not None:
            # For error cases, add False values for each expected score
            for score_name, metrics in expected_scores:
                for metric in metrics:
                    aggregated_results[score_name][metric].append(False)
        else:
            # For successful cases, use actual scores
            for score in res.result.scores:
                for metric in score.metrics:
                    aggregated_results[score.name][metric].append(score.value)

    # Compute and store metrics
    computed_metrics = {}
    for evaluator_name, metrics_values in aggregated_results.items():
        for metric_func, values in metrics_values.items():
            if values:  # Only compute if we have values
                metric_name = metric_func.__name__.replace("_", " ").title()
                computed_metrics[metric_name] = metric_func(values)

    return computed_metrics


# Progress manager classes for sequential and concurrent execution


class BaseProgressManager(ABC):
    """Abstract base class for progress management"""

    def __init__(self, evaluations: List[str], samples: Optional[int] = None):
        self.evaluations = evaluations
        self.samples = samples
        self.console = Console()
        self.live = None
        self.progress = None
        self.trackers: Dict[str, "ProgressTracker"] = {}

    @abstractmethod
    def create_tracker(self, eval_name: str, dataset_info: dict) -> "ProgressTracker":
        """Create a tracker for a single evaluation"""
        pass

    @abstractmethod
    def update_from_tracker(
        self,
        eval_name: str,
        completed: int,
        total: Optional[int],
        error_count: int,
        metrics: Dict[str, Any],
    ):
        """Called by individual trackers to update overall display"""
        pass

    @abstractmethod
    def finalize_evaluation(
        self, eval_name: str, result_obj: Any = None, error: bool = False
    ):
        """Mark an evaluation as completed with final results"""
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class SequentialProgressManager(BaseProgressManager):
    """Manages progress for sequential evaluation execution"""

    def __init__(self, evaluations: List[str], samples: Optional[int] = None):
        super().__init__(evaluations, samples)
        self.concurrent = False  # For backward compatibility
        self.current_tracker: Optional["ProgressTracker"] = None

    def create_tracker(self, eval_name: str, dataset_info: dict) -> "ProgressTracker":
        """Create a tracker for a single evaluation"""
        tracker = ProgressTracker(eval_name, dataset_info, self)
        self.trackers[eval_name] = tracker
        self.current_tracker = tracker
        return tracker

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()

    def update_from_tracker(
        self,
        eval_name: str,
        completed: int,
        total: Optional[int],
        error_count: int,
        metrics: Dict[str, Any],
    ):
        """Update sequential display"""
        tracker = self.trackers.get(eval_name)
        if tracker:
            # Update tracker state
            tracker.completed = completed
            tracker.error_count = error_count
            tracker.metrics = metrics

            # Update the progress display
            if (
                self.progress
                and hasattr(tracker, "main_task")
                and tracker.main_task is not None
            ):
                self.progress.update(tracker.main_task, completed=completed)
                if self.live:
                    self.live.update(self._build_sequential_display(tracker))

    def finalize_evaluation(
        self, eval_name: str, result_obj: Any = None, error: bool = False
    ):
        """Sequential mode doesn't need special finalization"""
        pass

    def _setup_sequential_display(self):
        """Set up display for sequential mode"""
        if not self.trackers:
            return

        tracker = next(iter(self.trackers.values()))
        total = tracker.total
        dataset_info = tracker.dataset_info

        if total:
            self.progress = Progress(
                TextColumn("✨ {task.description}"),
                BarColumn(bar_width=60),
                MofNCompleteColumn(),
                TextColumn("• Elapsed:"),
                TimeElapsedColumn(),
                TextColumn("• ETA:"),
                TimeRemainingColumn(),
                console=self.console,
                expand=False,
            )
            dataset_name = dataset_info.get("name", "Dataset")
            description = f"{dataset_name} [{total:,} examples]"
            tracker.main_task = self.progress.add_task(description, total=total)
        else:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("✨ {task.description}"),
                TextColumn("• {task.completed:,} completed"),
                TimeElapsedColumn(),
                console=self.console,
                expand=False,
            )
            dataset_name = dataset_info.get("name", "Dataset")
            description = f"{dataset_name} Evaluation"
            tracker.main_task = self.progress.add_task(description, total=None)

        self.live = Live(
            self._build_sequential_display(tracker),
            console=self.console,
            refresh_per_second=10,
        )
        self.live.start()

    def _build_sequential_display(self, tracker):
        """Build the complete display for sequential mode"""
        if not self.progress:
            return ""

        table = Table.grid(padding=(0, 0))
        table.add_column()
        table.add_row(self.progress)

        if tracker.metrics:
            metrics_parts = []
            for name, value in tracker.metrics.items():
                if isinstance(value, float):
                    metrics_parts.append(f"{name}: {value:.1%}")
                else:
                    metrics_parts.append(f"{name}: {value}")

            if metrics_parts:
                metrics_text = " • ".join(metrics_parts)
                table.add_row(Text(metrics_text, style="dim"))

        if tracker.error_count > 0:
            error_text = f"! {tracker.error_count} error{'s' if tracker.error_count != 1 else ''} encountered"
            table.add_row(Text(error_text, style="bold red"))

        return table


class ConcurrentProgressManager(BaseProgressManager):
    """Manages progress for concurrent evaluation execution"""

    def __init__(self, evaluations: List[str], samples: Optional[int] = None):
        super().__init__(evaluations, samples)
        self.concurrent = True  # For backward compatibility
        self.task_ids: Dict[str, Any] = {}
        self.task_metrics: Dict[str, Dict[str, Any]] = {}
        self.task_errors: Dict[str, int] = {}
        self.completed_tasks: set = set()

    def create_tracker(self, eval_name: str, dataset_info: dict) -> "ProgressTracker":
        """Create a tracker for a single evaluation"""
        tracker = ProgressTracker(eval_name, dataset_info, self)
        self.trackers[eval_name] = tracker
        return tracker

    def __enter__(self):
        self._setup_concurrent_display()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()

    def update_from_tracker(
        self,
        eval_name: str,
        completed: int,
        total: Optional[int],
        error_count: int,
        metrics: Dict[str, Any],
    ):
        """Update concurrent mode display"""
        if not self.progress or eval_name not in self.task_ids:
            return

        task_id = self.task_ids[eval_name]

        self.progress.update(task_id, completed=completed)
        if total:
            self.progress.update(task_id, total=total)

        self.task_metrics[eval_name] = metrics
        self.task_errors[eval_name] = error_count

        if error_count > 0:
            error_info = f"! {error_count} error{'s' if error_count != 1 else ''}"
            self.progress.update(task_id, error_info=error_info)
        else:
            self.progress.update(task_id, error_info="")

        if self.live:
            self.live.update(self._build_concurrent_display())

    def finalize_evaluation(
        self, eval_name: str, result_obj: Any = None, error: bool = False
    ):
        """Mark an evaluation as completed with final results"""
        if eval_name not in self.completed_tasks:
            self.completed_tasks.add(eval_name)

            if result_obj and hasattr(result_obj, "summary") and result_obj.summary:
                metrics = {}
                for metric_name, value in result_obj.summary.items():
                    if metric_name == "accuracy":
                        metrics["Accuracy"] = value
                    else:
                        metrics[metric_name.title()] = value
                self.task_metrics[eval_name] = metrics

            if error:
                self.task_errors[eval_name] = 1

            if self.live:
                self.live.update(self._build_concurrent_display())

    def _setup_concurrent_display(self):
        """Set up display for concurrent mode"""
        self.progress = Progress(
            TextColumn("✨ {task.description}"),
            BarColumn(bar_width=60),
            MofNCompleteColumn(),
            TextColumn("• Elapsed:"),
            TimeElapsedColumn(),
            TextColumn("• ETA:"),
            TimeRemainingColumn(),
            TextColumn("[red]{task.fields[error_info]}[/red]", style="red"),
            console=self.console,
            expand=False,
        )

        for eval_name in self.evaluations:
            task_id = self.progress.add_task(eval_name, total=None, error_info="")
            self.task_ids[eval_name] = task_id
            self.task_metrics[eval_name] = {}
            self.task_errors[eval_name] = 0

        self.live = Live(
            self._build_concurrent_display(),
            console=self.console,
            refresh_per_second=10,
        )
        self.live.start()

    def _build_concurrent_display(self):
        """Build the complete display for concurrent mode"""
        if not self.progress:
            return ""

        main_table = Table.grid(padding=(0, 0))
        main_table.add_column()
        main_table.add_row(self.progress)

        for eval_name in self.evaluations:
            if eval_name in self.task_metrics and self.task_metrics[eval_name]:
                metrics_parts = []
                for name, value in self.task_metrics[eval_name].items():
                    if isinstance(value, float) and value > 0:
                        metrics_parts.append(f"{name}: {value:.1%}")
                    elif not isinstance(value, float) and value:
                        metrics_parts.append(f"{name}: {value}")

                if metrics_parts:
                    metrics_line = f"{eval_name}: " + " • ".join(metrics_parts)
                    main_table.add_row(Text(metrics_line, style="dim"))

        return main_table


class ProgressTracker:
    """Tracks progress for a single evaluation - works in both modes"""

    def __init__(self, eval_name: str, dataset_info: dict, manager):
        self.eval_name = eval_name
        self.dataset_info = dataset_info
        self.manager = manager
        self.completed = 0
        self.total = dataset_info.get("total_rows")
        self.error_count = 0
        self.results: List[Record] = []
        self.metrics: Dict[str, Any] = {}

        # Task ID for progress tracking (set by manager if needed)
        self.main_task = None

    def __enter__(self):
        # Trigger sequential display setup in manager
        if isinstance(self.manager, SequentialProgressManager):
            self.manager._setup_sequential_display()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # New managers handle their own cleanup
        pass

    def update_progress(self, result: Record):
        """Update progress with a new result - unified interface"""
        self.completed += 1
        self.results.append(result)

        if result.error is not None:
            self.error_count += 1

        # Calculate metrics using unified function
        self.metrics = calculate_metrics(self.results)

        # Update display via manager
        if isinstance(
            self.manager, (ConcurrentProgressManager, SequentialProgressManager)
        ):
            self.manager.update_from_tracker(
                self.eval_name,
                self.completed,
                self.total,
                self.error_count,
                self.metrics,
            )
