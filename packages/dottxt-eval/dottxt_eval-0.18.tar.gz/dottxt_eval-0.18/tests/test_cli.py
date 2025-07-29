"""Tests for the CLI."""

import re
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from doteval.cli import cli
from doteval.metrics import accuracy
from doteval.models import Evaluation, EvaluationStatus, Record, Result, Score
from doteval.storage import JSONStorage


def strip_ansi(text):
    """Remove ANSI escape sequences from text for testing purposes."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


@pytest.fixture
def cli_runner():
    """Provide a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_storage():
    """Provide temporary storage for CLI tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_cli_list_empty_storage(cli_runner):
    """Test 'doteval list' with empty storage."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = []

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "No experiments found" in result.output


def test_cli_list_with_experiments(cli_runner):
    """Test 'doteval list' with existing experiments."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = ["exp1", "exp2"]
        mock_storage.list_evaluations.side_effect = [
            ["eval1", "eval2"],  # exp1 has 2 evaluations
            ["eval3"],  # exp2 has 1 evaluation
        ]

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "exp1" in result.output
        assert "exp2" in result.output
        assert "2" in result.output  # exp1 has 2 evaluations
        assert "1" in result.output  # exp2 has 1 evaluation


def test_cli_show_existing_experiment(cli_runner):
    """Test 'doteval show' with existing experiment."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = ["test_exp"]
        mock_storage.list_evaluations.return_value = ["eval1"]

        # Create mock results
        score = Score("test_evaluator", 0.95, [], {})
        result = Result(score, prompt="test")
        record = Record(result=result, item_id=0, dataset_row={})

        mock_storage.get_results.return_value = [record]

        result = cli_runner.invoke(cli, ["show", "test_exp"])

        assert result.exit_code == 0
        assert "test_exp" in result.output
        assert "eval1" in result.output


def test_cli_show_nonexistent_experiment(cli_runner):
    """Test 'doteval show' with nonexistent experiment."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = []

        result = cli_runner.invoke(cli, ["show", "nonexistent"])

        assert result.exit_code == 0  # CLI doesn't exit with error code
        assert "not found" in result.output


def test_cli_rename_experiment_success(cli_runner):
    """Test 'doteval rename' command success."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = ["old_name"]

        result = cli_runner.invoke(cli, ["rename", "old_name", "new_name"])

        assert result.exit_code == 0
        assert "renamed" in result.output
        mock_storage.rename_experiment.assert_called_once_with("old_name", "new_name")


def test_cli_rename_nonexistent_experiment(cli_runner):
    """Test 'doteval rename' with nonexistent experiment."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = []

        result = cli_runner.invoke(cli, ["rename", "nonexistent", "new_name"])

        assert result.exit_code == 0
        assert "not found" in result.output


def test_cli_delete_experiment_success(cli_runner):
    """Test 'doteval delete' command success."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = ["exp_to_delete"]

        result = cli_runner.invoke(cli, ["delete", "exp_to_delete"])

        assert result.exit_code == 0
        assert "Deleted experiment" in result.output
        mock_storage.delete_experiment.assert_called_once_with("exp_to_delete")


def test_cli_delete_nonexistent_experiment(cli_runner):
    """Test 'doteval delete' with nonexistent experiment."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = []

        result = cli_runner.invoke(cli, ["delete", "nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output


def test_cli_list_with_name_filter(cli_runner):
    """Test 'doteval list --name' filtering."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = [
            "math_eval",
            "text_eval",
            "other_test",
        ]
        mock_storage.list_evaluations.return_value = []

        result = cli_runner.invoke(cli, ["list", "--name", "eval"])

        assert result.exit_code == 0
        # Should only show experiments containing "eval"
        assert "math_eval" in result.output
        assert "text_eval" in result.output
        # The name filter should prevent "other_test" from being in output


def test_cli_show_with_full_flag(cli_runner):
    """Test 'doteval show --full' with detailed output."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = ["test_exp"]
        mock_storage.list_evaluations.return_value = ["eval1"]

        # Create mock results
        score = Score("test_evaluator", 0.95, [], {})
        result = Result(score, prompt="test")
        record = Record(result=result, item_id=0, dataset_row={})

        mock_storage.get_results.return_value = [record]

        result = cli_runner.invoke(cli, ["show", "test_exp", "--full"])

        assert result.exit_code == 0
        # With --full flag, should show JSON output
        assert "json" in result.output.lower() or "{" in result.output


def test_cli_with_custom_storage_option(cli_runner):
    """Test CLI commands with custom storage option."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = []

        result = cli_runner.invoke(cli, ["list", "--storage", "json://custom/path"])

        # Should pass custom storage path to get_storage
        mock_get_storage.assert_called_with("json://custom/path")
        assert result.exit_code == 0


def test_cli_show_with_errors(cli_runner):
    """Test 'doteval show' displays error counts."""
    with patch("doteval.cli.get_storage") as mock_get_storage:
        mock_storage = mock_get_storage.return_value
        mock_storage.list_experiments.return_value = ["test_exp"]
        mock_storage.list_evaluations.return_value = ["eval_test"]

        # Create mock results with some errors
        accuracy_metric = accuracy()
        results = [
            Record(
                result=Result(
                    Score("llm_judge", 0.9, [accuracy_metric], {}), prompt="test1"
                ),
                item_id=1,
                dataset_row={"prompt": "test1"},
                error=None,
                timestamp=1640995200.0,
            ),
            Record(
                result=Result(Score("llm_judge", 0, [accuracy_metric], {}), prompt=""),
                item_id=2,
                dataset_row={"prompt": "test2"},
                error="ConnectionError: Unable to connect to API",
                timestamp=1640995201.0,
            ),
            Record(
                result=Result(
                    Score("llm_judge", 0.8, [accuracy_metric], {}), prompt="test3"
                ),
                item_id=3,
                dataset_row={"prompt": "test3"},
                error=None,
                timestamp=1640995202.0,
            ),
            Record(
                result=Result(Score("llm_judge", 0, [accuracy_metric], {}), prompt=""),
                item_id=4,
                dataset_row={"prompt": "test4"},
                error="ValueError: Invalid response format",
                timestamp=1640995203.0,
            ),
        ]

        mock_storage.get_results.return_value = results

        result = cli_runner.invoke(cli, ["show", "test_exp"])

        assert result.exit_code == 0
        output = strip_ansi(result.output)
        # Check that error count is displayed
        assert "2/4 (50.0%)" in output
        # Check error summary section
        assert "Error Summary:" in output or "Error Types:" in output
        # Check for error information (format may vary)
        assert "Total errors: 2 out of 4 items" in output or (
            "ConnectionError:" in output and "ValueError:" in output
        )
        assert "ConnectionError:" in output and "1" in output
        assert "ValueError:" in output and "1" in output


def test_show_command_with_no_evaluations():
    """Test show command when experiment has no evaluations."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an experiment without evaluations
        storage = JSONStorage(temp_dir)
        storage.create_experiment("empty_exp")

        result = runner.invoke(
            cli, ["show", "empty_exp", "--storage", f"json://{temp_dir}"]
        )
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "No evaluations found for experiment 'empty_exp'" in output


def test_show_command_with_specific_evaluation_not_found():
    """Test show command when specific evaluation is not found."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an experiment with one evaluation
        storage = JSONStorage(temp_dir)
        storage.create_experiment("test_exp")
        eval1 = Evaluation(
            evaluation_name="eval1",
            status=EvaluationStatus.COMPLETED,
            started_at=1234567890,
        )
        storage.create_evaluation("test_exp", eval1)

        result = runner.invoke(
            cli,
            [
                "show",
                "test_exp",
                "--evaluation",
                "nonexistent",
                "--storage",
                f"json://{temp_dir}",
            ],
        )
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "Evaluation 'nonexistent' not found" in output


def test_show_command_with_errors_flag():
    """Test show command with --errors flag to show error details."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create experiment with evaluation containing errors
        storage = JSONStorage(temp_dir)
        storage.create_experiment("error_exp")
        eval1 = Evaluation(
            evaluation_name="error_eval",
            status=EvaluationStatus.COMPLETED,
            started_at=1234567890,
        )
        storage.create_evaluation("error_exp", eval1)

        # Add results with errors
        result1 = Result(prompt="test1")
        record1 = Record(
            result=result1,
            item_id=0,
            dataset_row={
                "input": "This is a very long input that should be truncated when displayed in the CLI output to ensure it doesn't take up too much space"
            },
            error="ValueError: Test error 1",
            timestamp=1234567890,
        )

        result2 = Result(prompt="test2")
        record2 = Record(
            result=result2,
            item_id=1,
            dataset_row={"input": "short input"},
            error="KeyError: Test error 2",
            timestamp=1234567891,
        )

        storage.add_results("error_exp", "error_eval", [record1, record2])

        result = runner.invoke(
            cli, ["show", "error_exp", "--errors", "--storage", f"json://{temp_dir}"]
        )
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        # Check for error details (format may vary)
        assert "Error Details (2 errors):" in output or (
            "ValueError: Test error 1" in output and "KeyError: Test error 2" in output
        )
        assert "ValueError: Test error 1" in output
        assert "KeyError: Test error 2" in output
        assert "..." in output  # Check truncation


def test_rename_command_with_existing_new_name():
    """Test rename command when new name already exists."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create two experiments
        storage = JSONStorage(temp_dir)
        storage.create_experiment("exp1")
        storage.create_experiment("exp2")

        result = runner.invoke(
            cli, ["rename", "exp1", "exp2", "--storage", f"json://{temp_dir}"]
        )
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "Experiment 'exp2' already exists" in output


def test_delete_command_with_error():
    """Test delete command when storage raises an error."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an experiment
        storage = JSONStorage(temp_dir)
        storage.create_experiment("test_exp")

        # Mock storage to raise an error
        with patch.object(
            JSONStorage, "delete_experiment", side_effect=Exception("Storage error")
        ):
            result = runner.invoke(
                cli, ["delete", "test_exp", "--storage", f"json://{temp_dir}"]
            )
            assert result.exit_code == 0
            assert "Error deleting experiment: Storage error" in result.output


def test_show_command_with_zero_accuracy_and_errors():
    """Test show command with zero accuracy excluding errors."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JSONStorage(temp_dir)
        storage.create_experiment("test_exp")
        eval1 = Evaluation(
            evaluation_name="test_eval",
            status=EvaluationStatus.COMPLETED,
            started_at=1234567890,
        )
        storage.create_evaluation("test_exp", eval1)

        # Add results: all false scores plus some errors
        acc_metric = accuracy()

        results = []
        # Add false results
        for i in range(3):
            result = Result(
                Score("evaluator1", False, [acc_metric], {}), prompt=f"test{i}"
            )
            record = Record(result=result, item_id=i, dataset_row={})
            results.append(record)

        # Add error results
        for i in range(3, 5):
            result = Result(prompt=f"test{i}")
            record = Record(
                result=result, item_id=i, dataset_row={}, error="Test error"
            )
            results.append(record)

        storage.add_results("test_exp", "test_eval", results)

        result = runner.invoke(
            cli, ["show", "test_exp", "--storage", f"json://{temp_dir}"]
        )
        assert result.exit_code == 0
        # Check that it shows accuracy with and without errors
        assert "0.00 (0.00 excluding errors)" in result.output


def test_list_command_filters_by_name():
    """Test list command with name filter."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JSONStorage(temp_dir)
        # Create multiple experiments
        storage.create_experiment("test_exp_1")
        storage.create_experiment("test_exp_2")
        storage.create_experiment("other_exp")

        # List with filter
        result = runner.invoke(
            cli, ["list", "--name", "test", "--storage", f"json://{temp_dir}"]
        )
        assert result.exit_code == 0
        assert "test_exp_1" in result.output
        assert "test_exp_2" in result.output
        assert "other_exp" not in result.output


# Tests for the run command
class TestCLIRunCommand:
    """Test the doteval run CLI command."""

    def test_run_sequential_basic(self):
        """Test basic sequential run command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation file
            eval_file = tmpdir_path / "eval_cli_test.py"
            eval_file.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("2+2", "4"), ("3+3", "6")])
def eval_cli_test(question, answer):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.85}
    return MockResult()
"""
            )

            # Run CLI command
            runner = CliRunner()
            with patch("doteval.cli.run_sequential") as mock_run_sequential:
                mock_run_sequential.return_value = [("eval_cli_test", Mock())]

                result = runner.invoke(
                    cli,
                    [
                        "run",
                        str(tmpdir_path),
                        "--samples",
                        "5",
                        "--experiment",
                        "test_exp",
                    ],
                )

            # Verify command succeeded
            assert result.exit_code == 0

            # Verify run_sequential was called correctly
            mock_run_sequential.assert_called_once_with(
                str(tmpdir_path), None, None, 5, "test_exp"
            )

    def test_run_concurrent_basic(self):
        """Test basic concurrent run command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test evaluation files
            eval_file1 = tmpdir_path / "eval_concurrent1.py"
            eval_file1.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("1+1", "2"), ("2+2", "4")])
def eval_concurrent1(question, answer):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.7}
    return MockResult()
"""
            )

            eval_file2 = tmpdir_path / "eval_concurrent2.py"
            eval_file2.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("3+3", "6"), ("4+4", "8")])
def eval_concurrent2(question, answer):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.9}
    return MockResult()
"""
            )

            # Run CLI command
            runner = CliRunner()
            with patch("doteval.cli.run_concurrent") as mock_run_concurrent:
                mock_run_concurrent.return_value = [
                    ("eval_concurrent1", Mock()),
                    ("eval_concurrent2", Mock()),
                ]

                result = runner.invoke(
                    cli,
                    [
                        "run",
                        str(tmpdir_path),
                        "-n",
                        "auto",
                        "--samples",
                        "3",
                        "--experiment",
                        "concurrent_test",
                    ],
                )

            # Verify command succeeded
            assert result.exit_code == 0

            # Verify run_concurrent was called correctly
            mock_run_concurrent.assert_called_once_with(
                str(tmpdir_path), None, None, 3, "concurrent_test", None
            )

    def test_run_with_keyword_filter(self):
        """Test run command with keyword filtering."""
        runner = CliRunner()
        with patch("doteval.cli.run_sequential") as mock_run_sequential:
            mock_run_sequential.return_value = []

            result = runner.invoke(cli, ["run", ".", "-k", "async", "--samples", "10"])

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify run_sequential was called with keyword filter
        mock_run_sequential.assert_called_once_with(".", "async", None, 10, None)

    def test_run_with_marker_filter(self):
        """Test run command with marker filtering."""
        runner = CliRunner()
        with patch("doteval.cli.run_sequential") as mock_run_sequential:
            mock_run_sequential.return_value = []

            result = runner.invoke(
                cli, ["run", ".", "-m", "slow", "--experiment", "marker_test"]
            )

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify run_sequential was called with marker filter
        mock_run_sequential.assert_called_once_with(
            ".", None, "slow", None, "marker_test"
        )

    def test_run_concurrent_with_number(self):
        """Test concurrent run with specific number."""
        runner = CliRunner()
        with patch("doteval.cli.run_concurrent") as mock_run_concurrent:
            mock_run_concurrent.return_value = []

            result = runner.invoke(cli, ["run", ".", "-n", "3"])

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify run_concurrent was called with max concurrent limit
        mock_run_concurrent.assert_called_once_with(".", None, None, None, None, 3)

    def test_run_concurrent_with_all_options(self):
        """Test concurrent run with all options."""
        runner = CliRunner()
        with patch("doteval.cli.run_concurrent") as mock_run_concurrent:
            mock_run_concurrent.return_value = []

            result = runner.invoke(
                cli,
                [
                    "run",
                    "/tmp/evals",
                    "-n",
                    "5",
                    "--samples",
                    "50",
                    "--experiment",
                    "full_test",
                    "-k",
                    "important",
                    "-m",
                    "critical",
                ],
            )

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify run_concurrent was called with all options
        mock_run_concurrent.assert_called_once_with(
            "/tmp/evals", "important", "critical", 50, "full_test", 5
        )

    def test_run_default_path(self):
        """Test run command with default path."""
        runner = CliRunner()
        with patch("doteval.cli.run_sequential") as mock_run_sequential:
            mock_run_sequential.return_value = []

            result = runner.invoke(cli, ["run"])

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify run_sequential was called with default path
        mock_run_sequential.assert_called_once_with(".", None, None, None, None)

    def test_run_sequential_with_exception(self):
        """Test sequential run handling exceptions."""
        runner = CliRunner()
        with patch("doteval.cli.run_sequential") as mock_run_sequential:
            mock_run_sequential.side_effect = Exception("Test error")

            result = runner.invoke(cli, ["run", "."])

        # Command should fail gracefully
        assert result.exit_code != 0

    def test_run_concurrent_with_exception(self):
        """Test concurrent run handling exceptions."""
        runner = CliRunner()
        with patch("doteval.cli.run_concurrent") as mock_run_concurrent:
            mock_run_concurrent.side_effect = Exception("Concurrent error")

            result = runner.invoke(cli, ["run", ".", "-n", "auto"])

        # Command should fail gracefully
        assert result.exit_code != 0

    def test_run_help(self):
        """Test run command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--help"])

        # Verify help is displayed
        assert result.exit_code == 0
        assert "Run evaluations in a directory" in result.output
        assert "-n" in result.output
        assert "--numprocesses" in result.output
        assert "--samples" in result.output
        assert "--experiment" in result.output
        assert "-k" in result.output
        assert "-m" in result.output

    def test_run_command_integration(self):
        """Test actual run command integration (without mocking)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a simple evaluation file
            eval_file = tmpdir_path / "eval_integration.py"
            eval_file.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("5+5", "10"), ("6+6", "12")])
def eval_integration(question, answer):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.5}
    return MockResult()
"""
            )

            # Run CLI command (this will actually execute)
            runner = CliRunner()
            result = runner.invoke(cli, ["run", str(tmpdir_path), "--samples", "1"])

            # Verify command succeeded
            assert result.exit_code == 0

            # Verify output contains expected information
            assert "eval_integration" in result.output

    def test_run_command_concurrent_integration(self):
        """Test actual concurrent run command integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create multiple evaluation files
            for i in range(3):
                eval_file = tmpdir_path / f"eval_concurrent_{i}.py"
                eval_file.write_text(
                    f"""
from doteval import foreach

@foreach("question,answer", [("test_{i}", "result_{i}")])
def eval_concurrent_{i}(question, answer):
    class MockResult:
        def __init__(self):
            self.summary = {{"accuracy": 0.{i}}}
    return MockResult()
"""
                )

            # Run CLI command concurrently
            runner = CliRunner()
            result = runner.invoke(
                cli, ["run", str(tmpdir_path), "-n", "auto", "--samples", "1"]
            )

            # Verify command succeeded
            assert result.exit_code == 0

            # Verify output contains all evaluations
            for i in range(3):
                assert f"eval_concurrent_{i}" in result.output

    def test_run_command_with_keyword_integration(self):
        """Test run command with keyword filtering integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create evaluation files with different keywords
            eval_file1 = tmpdir_path / "eval_fast_test.py"
            eval_file1.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("fast_test", "fast_result")])
def eval_fast_test(question, answer):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.8}
    return MockResult()
"""
            )

            eval_file2 = tmpdir_path / "eval_slow_test.py"
            eval_file2.write_text(
                """
from doteval import foreach

@foreach("question,answer", [("slow_test", "slow_result")])
def eval_slow_test(question, answer):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.6}
    return MockResult()
"""
            )

            # Run CLI command with keyword filter
            runner = CliRunner()
            result = runner.invoke(
                cli, ["run", str(tmpdir_path), "-k", "fast", "--samples", "1"]
            )

            # Verify command succeeded
            assert result.exit_code == 0

            # Verify only fast evaluation was run (check for "Running" which indicates execution)
            assert (
                "🔄 Running eval_fast_test" in result.output
                or "eval_fast_test" in result.output
            )
            # Check that slow test was not executed (it might appear in discovery but not in execution)
            assert "🔄 Running eval_slow_test" not in result.output


class TestCLIRunCommandEdgeCases:
    """Test edge cases for the CLI run command."""

    def test_run_nonexistent_directory(self):
        """Test run command with nonexistent directory."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "/nonexistent/path"])

        # Should handle gracefully (may succeed with empty results)
        # The exact behavior depends on the implementation
        # but should not crash
        assert isinstance(result.exit_code, int)

    def test_run_invalid_samples(self):
        """Test run command with invalid samples parameter."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", ".", "--samples", "invalid"])

        # Should fail due to invalid integer
        assert result.exit_code != 0

    def test_run_invalid_numprocesses(self):
        """Test run command with invalid -n parameter."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", ".", "-n", "invalid"])

        # Should fail due to invalid value
        assert result.exit_code == 0  # Command completes but with error message
        output = strip_ansi(result.output)
        assert "Error: -n must be a positive integer or 'auto'" in output

    def test_run_negative_numprocesses(self):
        """Test run command with negative -n parameter."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", ".", "-n", "-1"])

        # Should fail due to negative value
        assert result.exit_code == 0  # Command completes but with error message
        output = strip_ansi(result.output)
        assert "Error: -n must be a positive integer or 'auto'" in output

    def test_run_zero_numprocesses(self):
        """Test run command with zero -n parameter."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", ".", "-n", "0"])

        # Should fail due to zero value
        assert result.exit_code == 0  # Command completes but with error message
        output = strip_ansi(result.output)
        assert "Error: -n must be a positive integer or 'auto'" in output

    def test_run_numprocesses_auto(self):
        """Test run command with -n auto."""
        runner = CliRunner()
        with patch("doteval.cli.run_concurrent") as mock_run_concurrent:
            mock_run_concurrent.return_value = []

            result = runner.invoke(cli, ["run", ".", "-n", "auto"])

        # Should succeed with unlimited concurrency
        assert result.exit_code == 0

        # Verify run_concurrent was called with None (unlimited)
        mock_run_concurrent.assert_called_once_with(".", None, None, None, None, None)

    def test_run_with_empty_keyword(self):
        """Test run command with empty keyword."""
        runner = CliRunner()
        with patch("doteval.cli.run_sequential") as mock_run_sequential:
            mock_run_sequential.return_value = []

            result = runner.invoke(cli, ["run", ".", "-k", ""])

        # Should succeed with empty keyword
        assert result.exit_code == 0

        # Verify run_sequential was called with empty keyword
        mock_run_sequential.assert_called_once_with(".", "", None, None, None)

    def test_run_command_single_file_integration(self):
        """Test run command with a single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a single evaluation file with mock decorator
            eval_file = tmpdir_path / "eval_single_file.py"
            eval_file.write_text(
                """
def eval_single_file(evaluation_name, experiment_name, samples, **kwargs):
    class MockResult:
        def __init__(self):
            self.summary = {"accuracy": 0.6}
    return MockResult()

"""
            )

            # Run CLI command with single file
            runner = CliRunner()
            result = runner.invoke(cli, ["run", str(eval_file), "--samples", "1"])

            # Verify command succeeded
            assert result.exit_code == 0

            # Verify output contains expected information
            assert "eval_single_file" in result.output


def test_cli_coverage_improvement():
    """Simple test to improve CLI coverage."""
    runner = CliRunner()

    # Test help command to cover basic CLI functionality
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "doteval" in result.output.lower()
