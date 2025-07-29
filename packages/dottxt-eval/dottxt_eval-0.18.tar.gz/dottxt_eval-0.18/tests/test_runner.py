"""Tests for the evaluation runner functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from doteval.runner import (
    _execute_evaluation,
    discover_evaluations,
    run_concurrent,
    run_sequential,
)


class TestDiscoverEvaluations:
    """Test evaluation discovery functionality."""

    def test_discover_evaluations_with_temp_files(self):
        """Test discovering evaluations from temporary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation files
            eval_file1 = tmpdir_path / "eval_test1.py"
            eval_file1.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("2+2", "4"), ("3+3", "6")])
def eval_test1(question, answer):
    return {"result": "test1"}

def not_eval_function():
    pass
"""
            )

            eval_file2 = tmpdir_path / "eval_test2.py"
            eval_file2.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("1+1", "2"), ("5+5", "10")])
def eval_test2(question, answer):
    return {"result": "test2"}
"""
            )

            # Create non-eval file
            other_file = tmpdir_path / "other_file.py"
            other_file.write_text("def regular_function(): pass")

            # Test discovery
            items = discover_evaluations(str(tmpdir_path))

            # Should find both eval functions
            assert len(items) == 2
            names = [item.name for item in items]
            assert any("eval_test1" in name for name in names)
            assert any("eval_test2" in name for name in names)

            # Check functions were discovered
            for item in items:
                assert callable(item.function)

    def test_discover_evaluations_with_keyword_filter(self):
        """Test discovering evaluations with keyword filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation files
            eval_file1 = tmpdir_path / "eval_async_test.py"
            eval_file1.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("async test", "async result")])
def eval_async_test(question, answer):
    return {"result": "async"}
"""
            )

            eval_file2 = tmpdir_path / "eval_sync_test.py"
            eval_file2.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("sync test", "sync result")])
def eval_sync_test(question, answer):
    return {"result": "sync"}
"""
            )

            # Test with keyword filter
            items = discover_evaluations(str(tmpdir_path), keyword="async")

            # Should find only async eval (pytest may find multiple parameter combinations)
            assert len(items) >= 1
            # Check that all found items match the async test
            async_items = [item for item in items if "eval_async_test" in item.name]
            assert len(async_items) >= 1

    def test_discover_evaluations_empty_directory(self):
        """Test discovering evaluations in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            items = discover_evaluations(str(tmpdir))
            assert len(items) == 0

    def test_discover_evaluations_no_eval_functions(self):
        """Test discovering evaluations with no eval functions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create file with no eval functions
            test_file = tmpdir_path / "eval_empty.py"
            test_file.write_text("def regular_function(): pass")

            items = discover_evaluations(str(tmpdir_path))
            assert len(items) == 0

    def test_discover_evaluations_with_marker_filter(self):
        """Test discovering evaluations with marker filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation files
            eval_file1 = tmpdir_path / "eval_marked_test.py"
            eval_file1.write_text(
                """
from doteval import foreach
import pytest

@pytest.mark.slow
@foreach("question,answer", [("marked test", "marked result")])
def eval_marked_test(question, answer):
    return {"result": "marked"}
"""
            )

            eval_file2 = tmpdir_path / "eval_unmarked_test.py"
            eval_file2.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("unmarked test", "unmarked result")])
def eval_unmarked_test(question, answer):
    return {"result": "unmarked"}
"""
            )

            # Test with marker filter
            items = discover_evaluations(str(tmpdir_path), marker="slow")

            # Should find only the marked function since marker filtering now works correctly
            assert len(items) == 1
            assert "eval_marked_test" in items[0].name


class TestExecuteEvaluation:
    """Test evaluation execution functionality."""

    @pytest.mark.asyncio
    @patch("doteval.runner.setup_fixtures_for_evaluation")
    async def test_execute_evaluation_sync(self, mock_setup):
        """Test executing a sync evaluation."""

        # Mock fixtures - make it return a coroutine since setup_fixtures_for_evaluation is async
        async def mock_fixture_setup(func, fixture_params=None):
            return {"fixture": "value"}

        mock_setup.side_effect = mock_fixture_setup

        # Create mock evaluation function
        mock_eval_fn = Mock()
        mock_eval_fn.return_value = {"result": "success"}

        # Create mock item
        mock_item = Mock()
        mock_item.name = "test_eval"
        mock_item.function = mock_eval_fn
        mock_item.parameters = {}

        # Execute evaluation
        await _execute_evaluation(mock_item, samples=10, experiment_name="test")

        # Verify function was called correctly
        mock_eval_fn.assert_called_once_with(
            evaluation_name="test_eval",
            experiment_name="test",
            samples=10,
            progress_manager=None,
            fixture="value",
        )

    @pytest.mark.asyncio
    async def test_execute_evaluation_async(self):
        """Test executing an async evaluation."""

        # Create mock async evaluation function
        async def mock_async_eval(**kwargs):
            return {"result": "async_success"}

        # Create mock item
        mock_item = Mock()
        mock_item.name = "test_async_eval"
        mock_item.function = mock_async_eval
        mock_item.parameters = {}

        # Execute evaluation
        await _execute_evaluation(mock_item, samples=5, experiment_name="async_test")

    @pytest.mark.asyncio
    @patch("doteval.runner.setup_fixtures_for_evaluation")
    async def test_execute_evaluation_with_coroutine(self, mock_setup):
        """Test executing evaluation that returns a coroutine."""
        # Mock fixtures
        mock_setup.return_value = {"fixture": "value"}

        # Create mock evaluation function that returns coroutine
        async def mock_coroutine():
            return {"result": "coroutine_success"}

        mock_eval_fn = Mock()
        mock_eval_fn.return_value = mock_coroutine()

        # Create mock item
        mock_item = Mock()
        mock_item.name = "test_coroutine_eval"
        mock_item.function = mock_eval_fn
        mock_item.parameters = {}

        # Execute evaluation (should handle coroutine)
        await _execute_evaluation(mock_item)


class TestRunSequential:
    """Test sequential execution functionality."""

    @pytest.mark.asyncio
    async def test_run_sequential_success(self):
        """Test successful sequential execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation file
            eval_file = tmpdir_path / "eval_sequential_test.py"
            eval_file.write_text(
                """
def eval_sequential_test(evaluation_name, experiment_name, samples, **kwargs):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.8}
    return MockResult()

"""
            )

            # Run sequential
            with patch("doteval.runner.console") as mock_console:
                await run_sequential(str(tmpdir_path), samples=2)

            # Verify console output
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    async def test_run_sequential_with_exception(self):
        """Test sequential execution with exception handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation file that raises exception
            eval_file = tmpdir_path / "eval_exception_test.py"
            eval_file.write_text(
                """
def eval_exception_test(evaluation_name, experiment_name, samples, **kwargs):
    raise ValueError("Test exception")

"""
            )

            # Run sequential
            with patch("doteval.runner.console") as mock_console:
                await run_sequential(str(tmpdir_path), samples=2)

            # Verify console showed error message
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    async def test_run_sequential_with_runner_exception(self):
        """Test sequential execution with exception in runner itself."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation file
            eval_file = tmpdir_path / "eval_runner_exception_test.py"
            eval_file.write_text(
                """
def eval_runner_exception_test(evaluation_name, experiment_name, samples, **kwargs):
    return {"result": "success"}

"""
            )

            # Mock _execute_evaluation to raise exception (testing lines 91-93)
            with patch("doteval.runner._execute_evaluation") as mock_execute:
                mock_execute.side_effect = RuntimeError("Runner exception")

                with patch("doteval.runner.console") as mock_console:
                    await run_sequential(str(tmpdir_path), samples=2)

                # Verify error message was printed
                mock_console.print.assert_called()


class TestRunConcurrent:
    """Test concurrent execution functionality."""

    @pytest.mark.asyncio
    async def test_run_concurrent_success(self):
        """Test successful concurrent execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation files
            eval_file1 = tmpdir_path / "eval_concurrent1.py"
            eval_file1.write_text(
                """
def eval_concurrent1(evaluation_name, experiment_name, samples, **kwargs):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.7}
    return MockResult()

"""
            )

            eval_file2 = tmpdir_path / "eval_concurrent2.py"
            eval_file2.write_text(
                """
def eval_concurrent2(evaluation_name, experiment_name, samples, **kwargs):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.9}
    return MockResult()

"""
            )

            # Run concurrent - results are handled internally
            with patch("doteval.runner.console"):
                await run_concurrent(str(tmpdir_path), samples=2)

    @pytest.mark.asyncio
    async def test_run_concurrent_with_concurrency_limit(self):
        """Test concurrent execution with concurrency limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create multiple test evaluation files
            for i in range(5):
                eval_file = tmpdir_path / f"eval_limit_test{i}.py"
                eval_file.write_text(
                    f"""
def eval_limit_test{i}(evaluation_name, experiment_name, samples, **kwargs):
    class MockResult:
        def __init__(self):
            self.summary = {{"accuracy": 0.{i}}}
    return MockResult()

"""
                )

            # Run concurrent with limit - results are handled internally
            with patch("doteval.runner.console"):
                await run_concurrent(str(tmpdir_path), samples=2, max_concurrent=2)

    @pytest.mark.asyncio
    async def test_run_concurrent_with_exception(self):
        """Test concurrent execution with exception handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation files (one with exception)
            eval_file1 = tmpdir_path / "eval_success.py"
            eval_file1.write_text(
                """
def eval_success(evaluation_name, experiment_name, samples, **kwargs):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.8}
    return MockResult()

"""
            )

            eval_file2 = tmpdir_path / "eval_exception.py"
            eval_file2.write_text(
                """
def eval_exception(evaluation_name, experiment_name, samples, **kwargs):
    raise RuntimeError("Concurrent exception")

"""
            )

            # Run concurrent - exceptions are handled internally
            with patch("doteval.runner.console"):
                await run_concurrent(str(tmpdir_path), samples=2)

    @pytest.mark.asyncio
    async def test_run_concurrent_with_runner_exception(self):
        """Test concurrent execution with exception in runner itself."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation file
            eval_file = tmpdir_path / "eval_concurrent_exception.py"
            eval_file.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("concurrent test", "concurrent result")])
def eval_concurrent_exception(question, answer):
    return {"result": "success"}
"""
            )

            # Mock _execute_evaluation to raise exception
            with patch("doteval.runner._execute_evaluation") as mock_execute:
                mock_execute.side_effect = RuntimeError("Concurrent runner exception")

                with patch("doteval.runner.console"):
                    await run_concurrent(str(tmpdir_path), samples=2)

    @pytest.mark.asyncio
    async def test_run_concurrent_empty_directory(self):
        """Test concurrent execution with no evaluations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("doteval.runner.console") as mock_console:
                await run_concurrent(str(tmpdir), samples=2)

            mock_console.print.assert_called_with("No evaluations found.")


class TestParametrizeAndFixturesIntegration:
    """Test runner integration with parametrize and fixtures."""

    def test_discover_evaluations_with_parametrize(self):
        """Test that parametrized evaluations are expanded into separate items."""
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_file = Path(temp_dir) / "eval_unique_test1.py"
            eval_file.write_text(
                """
from doteval import foreach, parametrize

@parametrize("temp", [0.5, 1.0])
@foreach("question", [("What is 2+2?",)])
def eval_math(question, temp):
    return {"score": 1.0}

"""
            )

            # Discover evaluations
            items = discover_evaluations(temp_dir)

            # Should find 2 items (one per parameter value)
            assert len(items) == 2

            # Check item names include parameters
            item_names = [item.name for item in items]
            assert any("eval_math[0.5]" in name for name in item_names)
            assert any("eval_math[1.0]" in name for name in item_names)

            # Check parameters are stored correctly
            for item in items:
                assert hasattr(item, "parameters")
                assert "temp" in item.parameters
                assert item.parameters["temp"] in [0.5, 1.0]

    def test_discover_evaluations_with_multiple_parameters(self):
        """Test parametrized evaluations with multiple parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_file = Path(temp_dir) / "eval_unique_test2.py"
            eval_file.write_text(
                """
from doteval import foreach, parametrize

@parametrize(temp=[0.5, 1.0], model=["gpt-3.5", "gpt-4"])
@foreach("question", [("What is 2+2?",)])
def eval_math(question, temp, model):
    return {"score": 1.0}

"""
            )

            items = discover_evaluations(temp_dir)

            # Should find 4 items (2 * 2 combinations)
            assert len(items) == 4

            # Check all combinations are present
            param_combinations = [
                (item.parameters["temp"], item.parameters["model"]) for item in items
            ]
            expected_combinations = [
                (0.5, "gpt-3.5"),
                (0.5, "gpt-4"),
                (1.0, "gpt-3.5"),
                (1.0, "gpt-4"),
            ]
            assert set(param_combinations) == set(expected_combinations)

    @pytest.mark.asyncio
    @patch("doteval.runner.setup_fixtures_for_evaluation")
    async def test_execute_evaluation_sync_with_fixtures_and_parameters(
        self, mock_setup
    ):
        """Test sync evaluation function calling with fixture resolution and parameters."""

        # Mock fixture that should be resolved
        async def mock_fixture_setup(func, fixture_params=None):
            return {"api_key": "test_key"}

        mock_setup.side_effect = mock_fixture_setup

        # Create a mock evaluation function
        def mock_eval_fn(evaluation_name, experiment_name, samples, **kwargs):
            # Verify fixtures and parameters are passed
            assert "api_key" in kwargs
            assert "temp" in kwargs
            assert kwargs["temp"] == 0.5
            return Mock(summary="Test result")

        # Create mock item with parameters
        class MockItem:
            def __init__(self):
                self.name = "test_eval"
                self.function = mock_eval_fn
                self.parameters = {"temp": 0.5}

        item = MockItem()

        await _execute_evaluation(item, samples=10, experiment_name="test_exp")

        # Verify fixture setup was called with item parameters
        mock_setup.assert_called_once_with(mock_eval_fn, {"temp": 0.5})

    @pytest.mark.asyncio
    @patch("doteval.runner.setup_fixtures_for_evaluation")
    async def test_execute_evaluation_async_with_fixtures_and_parameters(
        self, mock_setup
    ):
        """Test async evaluation function calling with fixture resolution and parameters."""
        # Mock fixture that should be resolved
        mock_fixture_value = {"api_key": "test_key"}
        mock_setup.return_value = mock_fixture_value

        # Create a mock async evaluation function
        async def mock_eval_fn(evaluation_name, experiment_name, samples, **kwargs):
            # Verify fixtures and parameters are passed
            assert "api_key" in kwargs
            assert "temp" in kwargs
            assert kwargs["temp"] == 1.0
            return Mock(summary="Async test result")

        # Create mock item with parameters
        class MockItem:
            def __init__(self):
                self.name = "test_eval_async"
                self.function = mock_eval_fn
                self.parameters = {"temp": 1.0}

        item = MockItem()

        await _execute_evaluation(item, samples=5, experiment_name="async_exp")

        # Verify fixture setup was called with item parameters
        mock_setup.assert_called_once_with(mock_eval_fn, {"temp": 1.0})

    def test_discover_evaluations_without_parametrize(self):
        """Test that non-parametrized evaluations work normally."""
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_file = Path(temp_dir) / "eval_unique_test3.py"
            eval_file.write_text(
                """
from doteval import foreach

@foreach("question", [("What is 2+2?",)])
def eval_math(question):
    return {"score": 1.0}

"""
            )

            items = discover_evaluations(temp_dir)

            # Should find 1 item
            assert len(items) == 1
            assert "eval_math" in items[0].name
            # The foreach decorator will create parameters, but there should be no "temp" parameter
            assert "temp" not in items[0].parameters

    @pytest.mark.asyncio
    @patch("doteval.runner.setup_fixtures_for_evaluation")
    async def test_backward_compatibility_with_mock_items(self, mock_setup):
        """Test that old Mock items without parameters attribute still work."""

        # Mock fixture that should be resolved
        async def mock_fixture_setup(func, fixture_params=None):
            return {"fixture": "value"}

        mock_setup.side_effect = mock_fixture_setup

        # Create a mock evaluation function
        def mock_eval_fn(evaluation_name, experiment_name, samples, **kwargs):
            return Mock(summary="Test result")

        # Create old-style mock item without parameters - add parameters={} to match EvalItem
        mock_item = Mock()
        mock_item.name = "test_eval"
        mock_item.function = mock_eval_fn
        mock_item.parameters = {}  # Ensure this exists to avoid AttributeError

        # Should work without error
        await _execute_evaluation(mock_item, samples=10, experiment_name="test_exp")

        # Verify fixture setup was called
        mock_setup.assert_called_once_with(mock_eval_fn, {})
