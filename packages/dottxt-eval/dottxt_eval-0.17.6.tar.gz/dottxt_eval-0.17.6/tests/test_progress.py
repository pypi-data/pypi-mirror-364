"""Tests for progress.py module."""

from unittest.mock import Mock, patch

from doteval.progress import (
    ConcurrentProgressManager,
    ProgressTracker,
    SequentialProgressManager,
    calculate_metrics,
    get_dataset_info,
)


def test_get_dataset_info_with_dataset_instance():
    """Test get_dataset_info with a dataset instance."""
    # Mock dataset with name and num_rows
    dataset = Mock()
    dataset.name = "test_dataset"
    dataset.num_rows = 100

    info = get_dataset_info(dataset)

    assert info["name"] == "TEST_DATASET"
    assert info["total_rows"] == 100


def test_get_dataset_info_with_len_support():
    """Test get_dataset_info with object supporting len()."""
    # Mock object with __len__ method
    dataset = []
    for i in range(50):
        dataset.append(i)

    info = get_dataset_info(dataset)

    assert info["name"] == "Dataset"
    assert info["total_rows"] == 50


def test_get_dataset_info_with_len_error():
    """Test get_dataset_info when len() raises error."""
    # Mock object with __len__ that raises TypeError
    dataset = Mock()
    dataset.__len__ = Mock(side_effect=TypeError("no len support"))
    del dataset.name
    del dataset.num_rows

    info = get_dataset_info(dataset)

    assert info["name"] == "Dataset"
    assert info["total_rows"] is None


def test_get_dataset_info_fallback():
    """Test get_dataset_info fallback behavior."""

    # Object with no special attributes and no len
    class NoLenObject:
        pass

    dataset = NoLenObject()

    info = get_dataset_info(dataset)

    assert info["name"] == "Dataset"
    assert info["total_rows"] is None


class TestProgressTracker:
    """Test ProgressTracker class."""

    def test_initialization(self):
        """Test ProgressTracker initialization."""
        dataset_info = {"name": "test", "total_rows": 100}
        manager = SequentialProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)

        assert tracker.eval_name == "test_eval"
        assert tracker.dataset_info == dataset_info
        assert tracker.completed == 0
        assert tracker.total == 100
        assert tracker.error_count == 0
        assert tracker.metrics == {}

    def test_context_manager_sequential_mode(self):
        """Test context manager in sequential mode."""
        dataset_info = {"name": "test", "total_rows": 100}
        manager = SequentialProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)

        # Sequential mode tracker should return self and set up display
        with tracker as p:
            assert p is tracker

    def test_context_manager_concurrent_mode(self):
        """Test context manager in concurrent mode."""
        dataset_info = {"name": "test", "total_rows": 100}
        manager = ConcurrentProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)

        # In concurrent mode, tracker doesn't set up its own display
        with tracker as p:
            assert p is tracker

    def test_context_manager_with_unknown_size(self):
        """Test context manager with unknown dataset size."""
        dataset_info = {"name": "test", "total_rows": None}
        manager = SequentialProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)

        with tracker as p:
            assert p is tracker
            assert tracker.total is None

    def test_build_display_no_progress(self):
        """Test _build_sequential_display when no progress object exists."""
        dataset_info = {"name": "test", "total_rows": 100}
        manager = SequentialProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)
        manager.trackers["test_eval"] = tracker

        result = manager._build_sequential_display(tracker)
        assert result == ""

    def test_build_display_with_metrics_and_errors(self):
        """Test _build_sequential_display with metrics and errors."""
        dataset_info = {"name": "test", "total_rows": 100}
        manager = SequentialProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)
        manager.trackers["test_eval"] = tracker

        with patch("doteval.progress.Progress") as mock_progress:
            with patch("doteval.progress.Table") as mock_table:
                mock_progress_instance = Mock()
                mock_progress.return_value = mock_progress_instance

                mock_table_instance = Mock()
                mock_table.grid.return_value = mock_table_instance

                manager.progress = mock_progress_instance
                tracker.metrics = {"accuracy": 0.85, "count": 42}
                tracker.error_count = 3

                manager._build_sequential_display(tracker)

                # Should add progress, metrics, and error rows
                assert mock_table_instance.add_row.call_count == 3
                calls = mock_table_instance.add_row.call_args_list

                # First call should be progress
                assert calls[0][0][0] == mock_progress_instance

                # Second call should be metrics text
                # Third call should be error text

    def test_update_progress_no_progress_object(self):
        """Test update_progress when no progress object exists."""
        dataset_info = {"name": "test", "total_rows": 100}
        manager = SequentialProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)

        # Create a mock result
        result = Mock()
        result.error = None
        result.result = Mock()
        result.result.scores = []

        # Should not crash, and should update counts
        tracker.update_progress(result)
        assert tracker.completed == 1  # Should increment

    def test_update_progress_with_error(self):
        """Test update_progress with error result."""
        dataset_info = {"name": "test", "total_rows": 100}
        manager = SequentialProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)

        # Create a mock result with error
        result = Mock()
        result.error = "Test error"
        result.result = Mock()
        result.result.scores = []

        # Should update counts including error count
        tracker.update_progress(result)

        assert tracker.completed == 1  # Should increment
        assert tracker.error_count == 1  # Should increment error count

    def test_metrics_calculation_via_calculate_metrics(self):
        """Test unified calculate_metrics function."""

        # Mock metric function
        def mock_accuracy(values):
            return sum(values) / len(values)

        mock_accuracy.__name__ = "accuracy"

        # Create mock results
        score1 = Mock()
        score1.name = "evaluator1"
        score1.value = True
        score1.metrics = [mock_accuracy]

        result1 = Mock()
        result1.error = None
        result1.result = Mock()
        result1.result.scores = [score1]

        score2 = Mock()
        score2.name = "evaluator1"
        score2.value = False
        score2.metrics = [mock_accuracy]

        result2 = Mock()
        result2.error = None
        result2.result = Mock()
        result2.result.scores = [score2]

        # Test the unified function
        metrics = calculate_metrics([result1, result2])

        # Should calculate accuracy
        assert "Accuracy" in metrics
        assert metrics["Accuracy"] == 0.5  # (True + False) / 2

    def test_calculate_metrics_with_errors(self):
        """Test calculate_metrics with error results."""

        # Mock metric function
        def mock_accuracy(values):
            return sum(values) / len(values)

        mock_accuracy.__name__ = "accuracy"

        # Create successful result first to establish expected scores
        score1 = Mock()
        score1.name = "evaluator1"
        score1.value = True
        score1.metrics = [mock_accuracy]

        result1 = Mock()
        result1.error = None
        result1.result = Mock()
        result1.result.scores = [score1]

        # Create error result
        result2 = Mock()
        result2.error = "Test error"
        result2.result = Mock()
        result2.result.scores = []

        # Test the unified function
        metrics = calculate_metrics([result1, result2])

        # Should calculate accuracy with False for error
        assert "Accuracy" in metrics
        assert metrics["Accuracy"] == 0.5  # (True + False) / 2

    def test_update_progress_updates_metrics(self):
        """Test that update_progress calculates and updates metrics."""
        dataset_info = {"name": "test", "total_rows": 100}
        manager = SequentialProgressManager(["test_eval"])
        tracker = ProgressTracker("test_eval", dataset_info, manager)

        # Mock metric function
        def mock_accuracy(values):
            return sum(values) / len(values)

        mock_accuracy.__name__ = "accuracy"

        # Create mock result
        score = Mock()
        score.name = "evaluator1"
        score.value = True
        score.metrics = [mock_accuracy]

        result = Mock()
        result.error = None
        result.result = Mock()
        result.result.scores = [score]

        tracker.update_progress(result)

        assert "Accuracy" in tracker.metrics
        assert tracker.metrics["Accuracy"] == 1.0  # Only True value

    def test_tracker_creation_via_manager(self):
        """Test that SequentialProgressManager creates trackers correctly."""
        manager = SequentialProgressManager(["eval1", "eval2"])
        dataset_info = {"name": "test", "total_rows": 100}

        tracker = manager.create_tracker("eval1", dataset_info)
        assert tracker.eval_name == "eval1"
        assert tracker.manager is manager
        assert "eval1" in manager.trackers

    def test_sequential_vs_concurrent_mode(self):
        """Test that trackers behave differently in sequential vs concurrent mode."""
        dataset_info = {"name": "test", "total_rows": 100}

        # Sequential mode
        seq_manager = SequentialProgressManager(["eval1"])
        seq_tracker = ProgressTracker("eval1", dataset_info, seq_manager)
        assert not seq_tracker.manager.concurrent

        # Concurrent mode
        conc_manager = ConcurrentProgressManager(["eval1"])
        conc_tracker = ProgressTracker("eval1", dataset_info, conc_manager)
        assert conc_tracker.manager.concurrent


class TestProgressManager:
    """Test ProgressManager class."""

    def test_initialization(self):
        """Test ProgressManager initialization."""
        eval_names = ["eval1", "eval2", "eval3"]
        manager = ConcurrentProgressManager(eval_names, samples=50)

        assert manager.evaluations == eval_names
        assert manager.samples == 50
        assert manager.concurrent is True
        assert manager.trackers == {}

    def test_context_manager_concurrent_mode(self):
        """Test context manager in concurrent mode."""
        eval_names = ["eval1", "eval2"]
        manager = ConcurrentProgressManager(eval_names)

        # Concurrent mode sets up progress display
        with manager as p:
            assert p is manager

    def test_context_manager_sequential_mode(self):
        """Test context manager in sequential mode."""
        eval_names = ["eval1"]
        manager = SequentialProgressManager(eval_names)

        # Sequential mode doesn't set up concurrent display
        with manager as p:
            assert p is manager
            assert manager.live is None  # No concurrent display

    def test_build_concurrent_display_no_progress(self):
        """Test _build_concurrent_display when no progress object exists."""
        eval_names = ["eval1"]
        manager = ConcurrentProgressManager(eval_names)

        result = manager._build_concurrent_display()
        assert result == ""

    def test_build_concurrent_display_with_metrics(self):
        """Test _build_concurrent_display with metrics."""
        eval_names = ["eval1", "eval2"]
        manager = ConcurrentProgressManager(eval_names)

        with patch("doteval.progress.Progress") as mock_progress:
            with patch("doteval.progress.Table") as mock_table:
                mock_progress_instance = Mock()
                mock_progress.return_value = mock_progress_instance

                manager.progress = mock_progress_instance
                manager.task_metrics = {"eval1": {"accuracy": 0.8}, "eval2": {}}

                mock_table_instance = Mock()
                mock_table.grid.return_value = mock_table_instance

                manager._build_concurrent_display()

                # Should create table structure
                mock_table.grid.assert_called()

    def test_update_from_tracker_no_progress_object(self):
        """Test update_from_tracker when no progress object exists."""
        eval_names = ["eval1"]
        manager = ConcurrentProgressManager(eval_names)

        # Should not crash
        manager.update_from_tracker("eval1", 5, 100, 0, {})

    def test_update_from_tracker_unknown_evaluation(self):
        """Test update_from_tracker with unknown evaluation name."""
        eval_names = ["eval1"]
        manager = ConcurrentProgressManager(eval_names)

        manager.progress = Mock()
        manager.task_ids = {"eval1": "task1"}

        # Should not crash
        manager.update_from_tracker("unknown_eval", 5, 100, 0, {})

    def test_finalize_evaluation(self):
        """Test finalize_evaluation marking evaluation as completed."""
        eval_names = ["eval1"]
        manager = ConcurrentProgressManager(eval_names)

        manager.progress = Mock()
        manager.task_ids = {"eval1": "task1"}
        manager.live = Mock()

        # Mock _build_concurrent_display to avoid complex UI logic
        with patch.object(
            manager, "_build_concurrent_display", return_value="mock_display"
        ):
            manager.finalize_evaluation("eval1")

            assert "eval1" in manager.completed_tasks

    def test_finalize_evaluation_with_result_and_metrics(self):
        """Test finalize_evaluation with result object containing metrics."""
        eval_names = ["eval1"]
        manager = ConcurrentProgressManager(eval_names)

        manager.progress = Mock()
        manager.task_ids = {"eval1": "task1"}
        manager.live = Mock()

        # Mock result object with summary
        result_obj = Mock()
        result_obj.summary = {"accuracy": 0.85, "precision": 0.9}

        # Mock _build_concurrent_display to avoid complex UI logic
        with patch.object(
            manager, "_build_concurrent_display", return_value="mock_display"
        ):
            manager.finalize_evaluation("eval1", result_obj=result_obj)

            assert manager.task_metrics["eval1"]["Accuracy"] == 0.85
            assert manager.task_metrics["eval1"]["Precision"] == 0.9

    def test_finalize_evaluation_with_error(self):
        """Test finalize_evaluation with error flag."""
        eval_names = ["eval1"]
        manager = ConcurrentProgressManager(eval_names)

        manager.progress = Mock()
        manager.task_ids = {"eval1": "task1"}
        manager.live = Mock()

        # Mock _build_concurrent_display to avoid complex UI logic
        with patch.object(
            manager, "_build_concurrent_display", return_value="mock_display"
        ):
            manager.finalize_evaluation("eval1", error=True)

            assert manager.task_errors["eval1"] == 1

    def test_update_from_tracker_existing_task(self):
        """Test update_from_tracker with existing task."""
        eval_names = ["eval1"]
        manager = ConcurrentProgressManager(eval_names)

        manager.progress = Mock()
        manager.task_ids = {"eval1": "task1"}

        # Should not crash
        manager.update_from_tracker("eval1", 5, 100, 0, {})

    def test_create_tracker_integration(self):
        """Test that ProgressManager properly creates and manages trackers."""
        eval_names = ["eval1"]
        manager = ConcurrentProgressManager(eval_names)

        dataset_info = {"name": "test", "total_rows": 100}
        tracker = manager.create_tracker("eval1", dataset_info)

        assert tracker.eval_name == "eval1"
        assert tracker.manager is manager
        assert manager.trackers["eval1"] is tracker


def test_get_dataset_info_with_name_but_no_num_rows():
    """Test get_dataset_info fallback behavior."""
    # Simple test case that covers additional code paths
    dataset_list = [1, 2, 3, 4, 5]  # Simple list with len()
    info = get_dataset_info(dataset_list)

    assert info["name"] == "Dataset"
    assert info["total_rows"] == 5


def test_progress_manager_final_metrics_display():
    """Test ProgressManager final metrics display to cover specific code paths."""
    eval_names = ["eval1", "eval2"]
    manager = ConcurrentProgressManager(eval_names)

    # Set up mocked components
    manager.progress = Mock()
    manager.task_ids = {"eval1": "task1", "eval2": "task2"}
    manager.live = Mock()
    manager.task_metrics = {
        "eval1": {"accuracy": 0.8, "precision": 0.9},
        "eval2": {"accuracy": 0.7},
    }
    manager.task_errors = {"eval1": 0, "eval2": 1}

    with patch("doteval.progress.Table") as mock_table_class:
        mock_table = Mock()
        mock_table_class.grid.return_value = mock_table

        # This should trigger the final metrics display logic
        manager._build_concurrent_display()

        # Should have created table and added rows
        mock_table_class.grid.assert_called_once()


def test_progress_manager_concurrent_live_update():
    """Test ProgressManager live update in concurrent mode."""
    eval_names = ["eval1"]
    manager = ConcurrentProgressManager(eval_names)

    # Set up mock progress and live objects
    manager.progress = Mock()
    manager.task_ids = {"eval1": "task1"}
    manager.live = Mock()

    # Test live update path
    with patch.object(manager, "_build_concurrent_display", return_value="display"):
        manager.update_from_tracker("eval1", 5, 100, 0, {})

        # Should have updated the live display
        manager.live.update.assert_called_with("display")
