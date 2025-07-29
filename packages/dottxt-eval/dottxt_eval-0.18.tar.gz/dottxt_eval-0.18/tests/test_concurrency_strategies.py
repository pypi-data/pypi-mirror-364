"""Tests for concurrency strategies."""

import asyncio
import time

import pytest

from doteval.concurrency import (
    AdaptiveStrategy,
    BatchStrategy,
    SequentialStrategy,
    SlidingWindowStrategy,
)


class TestSequentialStrategy:
    """Test the sequential execution strategy."""

    def test_sequential_execution(self):
        """Test that tasks are executed sequentially."""
        strategy = SequentialStrategy()
        execution_order = []

        def create_tasks():
            for i in range(5):

                def task(task_id=i):
                    execution_order.append(task_id)
                    return f"result_{task_id}"

                yield task

        results = list(strategy.execute(create_tasks()))

        # Check execution order is sequential
        assert execution_order == [0, 1, 2, 3, 4]
        assert results == ["result_0", "result_1", "result_2", "result_3", "result_4"]

    def test_sequential_with_progress_callback(self):
        """Test sequential execution with progress callback."""
        strategy = SequentialStrategy()
        progress_results = []

        def progress_callback(result):
            progress_results.append(result)

        def create_tasks():
            for i in range(3):

                def task(task_id=i):
                    return f"result_{task_id}"

                yield task

        results = list(strategy.execute(create_tasks(), progress_callback))

        assert results == ["result_0", "result_1", "result_2"]
        assert progress_results == ["result_0", "result_1", "result_2"]

    def test_sequential_with_exception(self):
        """Test that exceptions are propagated."""
        strategy = SequentialStrategy()

        def create_tasks():
            yield lambda: "result_0"
            yield lambda: (_ for _ in ()).throw(ValueError("test error"))
            yield lambda: "result_2"

        results = []
        with pytest.raises(ValueError, match="test error"):
            for result in strategy.execute(create_tasks()):
                results.append(result)

        # Only the first task should have completed
        assert results == ["result_0"]


class TestBatchStrategy:
    """Test the batch execution strategy."""

    def test_batch_execution(self):
        """Test that tasks are executed in batches."""
        strategy = BatchStrategy(batch_size=3)
        execution_times = []

        def create_tasks():
            for i in range(7):

                def task(task_id=i):
                    execution_times.append(task_id)
                    return f"result_{task_id}"

                yield task

        results = list(strategy.execute(create_tasks()))

        # Check all tasks executed
        assert len(execution_times) == 7
        assert len(results) == 7
        assert results == [f"result_{i}" for i in range(7)]

    def test_batch_with_progress_callback(self):
        """Test batch execution with progress callback."""
        strategy = BatchStrategy(batch_size=2)
        progress_results = []

        def progress_callback(result):
            progress_results.append(result)

        def create_tasks():
            for i in range(5):

                def task(task_id=i):
                    return f"result_{task_id}"

                yield task

        results = list(strategy.execute(create_tasks(), progress_callback))

        assert len(results) == 5
        assert len(progress_results) == 5
        assert progress_results == [f"result_{i}" for i in range(5)]


class TestSlidingWindowStrategy:
    """Test the sliding window async execution strategy."""

    @pytest.mark.asyncio
    async def test_sliding_window_execution(self):
        """Test that tasks are executed with concurrency control."""
        strategy = SlidingWindowStrategy(max_concurrency=2)
        currently_running = 0
        max_concurrent = 0

        def create_tasks():
            for i in range(5):

                async def task(task_id=i):
                    nonlocal currently_running, max_concurrent
                    currently_running += 1
                    max_concurrent = max(max_concurrent, currently_running)
                    await asyncio.sleep(0.01)  # Simulate work
                    currently_running -= 1
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        # Check all tasks completed
        assert len(results) == 5
        assert all(r.startswith("result_") for r in results)
        # Check concurrency was limited
        assert max_concurrent <= 2

    @pytest.mark.asyncio
    async def test_sliding_window_with_progress_callback(self):
        """Test sliding window execution with progress callback."""
        strategy = SlidingWindowStrategy(max_concurrency=3)
        progress_results = []

        def progress_callback(result):
            progress_results.append(result)

        def create_tasks():
            for i in range(4):

                async def task(task_id=i):
                    await asyncio.sleep(0.001)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks(), progress_callback):
            results.append(result)

        assert len(results) == 4
        assert len(progress_results) == 4

    @pytest.mark.asyncio
    async def test_sliding_window_with_exception(self):
        """Test that exceptions in tasks are propagated."""
        strategy = SlidingWindowStrategy(max_concurrency=2)

        def create_tasks():
            async def task1():
                await asyncio.sleep(0.01)
                return "result_1"

            async def task2():
                await asyncio.sleep(0.005)
                raise ValueError("test error")

            async def task3():
                return "result_3"

            yield task1
            yield task2
            yield task3

        results = []

        with pytest.raises(ValueError, match="test error"):
            async for result in strategy.execute(create_tasks()):
                results.append(result)

        # The strategy executes tasks concurrently, so we might get some results
        # before the exception is raised
        assert len(results) <= 3  # At most all results if exception is last


class TestAdaptiveStrategy:
    """Test the adaptive concurrency execution strategy."""

    @pytest.mark.asyncio
    async def test_adaptive_basic_execution(self):
        """Test that adaptive strategy can execute tasks."""
        strategy = AdaptiveStrategy(
            initial_concurrency=2,
            adaptation_interval=0.1,  # Fast adaptation for testing
            min_concurrency=1,
            max_concurrency=10,
        )

        def create_tasks():
            for i in range(5):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 5
        assert all(r.startswith("result_") for r in results)

    @pytest.mark.asyncio
    async def test_adaptive_with_progress_callback(self):
        """Test adaptive strategy with progress callback."""
        strategy = AdaptiveStrategy(
            initial_concurrency=2,
            adaptation_interval=0.05,
        )
        progress_results = []

        def progress_callback(result):
            progress_results.append(result)

        def create_tasks():
            for i in range(4):

                async def task(task_id=i):
                    await asyncio.sleep(0.001)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks(), progress_callback):
            results.append(result)

        assert len(results) == 4
        assert len(progress_results) == 4
        assert set(results) == set(progress_results)

    @pytest.mark.asyncio
    async def test_adaptive_throughput_tracking(self):
        """Test that adaptive strategy tracks throughput."""
        strategy = AdaptiveStrategy(
            initial_concurrency=2,
            adaptation_interval=0.05,
        )

        def create_tasks():
            for i in range(10):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        stats = strategy.get_stats()
        assert stats["total_completed"] == 10
        assert stats["total_tasks"] == 10
        assert stats["throughput"] is not None
        assert stats["throughput"] > 0

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_adjustment(self):
        """Test that adaptive strategy can adjust concurrency."""
        strategy = AdaptiveStrategy(
            initial_concurrency=2,
            adaptation_interval=0.05,  # Fast adaptation
            min_concurrency=1,
            max_concurrency=20,
            stability_window=1,  # Quick decisions
        )

        # Create enough tasks to allow adaptation to happen
        def create_tasks():
            for i in range(30):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)  # Some work time
                    return f"result_{task_id}"

                yield task

        results = []

        async for result in strategy.execute(create_tasks()):
            results.append(result)

        final_stats = strategy.get_stats()

        # Should have completed all tasks
        assert len(results) == 30

        # Strategy should have some adaptation history or at least be functioning
        assert final_stats["total_completed"] == 30
        assert final_stats["throughput"] is not None

    @pytest.mark.asyncio
    async def test_adaptive_error_handling(self):
        """Test that adaptive strategy handles errors properly."""
        strategy = AdaptiveStrategy(
            initial_concurrency=2,
            adaptation_interval=0.05,
            error_backoff_factor=0.5,
        )

        def create_tasks():
            # First few tasks succeed
            for i in range(3):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

            # Then a task fails
            async def failing_task():
                await asyncio.sleep(0.01)
                raise ValueError("test error")

            yield failing_task

        results = []

        with pytest.raises(ValueError, match="test error"):
            async for result in strategy.execute(create_tasks()):
                results.append(result)

        # Should have gotten some results before the error
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_adaptive_stats_collection(self):
        """Test that adaptive strategy collects comprehensive stats."""
        strategy = AdaptiveStrategy(
            initial_concurrency=3,
            adaptation_interval=0.05,
        )

        def create_tasks():
            for i in range(8):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        stats = strategy.get_stats()

        # Verify all expected stats are present
        assert "current_concurrency" in stats
        assert "throughput" in stats
        assert "total_completed" in stats
        assert "total_tasks" in stats
        assert "recent_errors" in stats
        assert "adaptation_history" in stats

        # Verify stats values make sense
        assert stats["total_completed"] == 8
        assert stats["total_tasks"] == 8
        assert stats["recent_errors"] == 0
        assert isinstance(stats["adaptation_history"], list)

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_limits(self):
        """Test that adaptive strategy respects concurrency limits."""
        strategy = AdaptiveStrategy(
            initial_concurrency=5,
            min_concurrency=2,
            max_concurrency=8,
            adaptation_interval=0.01,
        )

        def create_tasks():
            for i in range(6):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        # Strategy should respect limits
        assert strategy.current_concurrency >= 2
        assert strategy.current_concurrency <= 8
        assert len(results) == 6

    @pytest.mark.asyncio
    async def test_adaptive_throughput_measurement(self):
        """Test throughput measurement accuracy."""
        strategy = AdaptiveStrategy(
            initial_concurrency=2,
            adaptation_interval=0.1,
        )

        start_time = time.time()

        def create_tasks():
            for i in range(10):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        end_time = time.time()
        elapsed = end_time - start_time

        stats = strategy.get_stats()
        measured_throughput = stats["throughput"]

        # Rough throughput check (should be in reasonable range)
        if measured_throughput is not None:
            expected_throughput = 10 / elapsed
            # Allow for some variance due to overhead and timing
            assert measured_throughput > 0
            assert measured_throughput < expected_throughput * 2  # Not too high

    def test_throughput_tracker_get_recent_throughput(self):
        """Test ThroughputTracker.get_recent_throughput method."""
        from doteval.concurrency.adaptive import ThroughputTracker

        tracker = ThroughputTracker(window_size=10)

        # Test with no data
        assert tracker.get_recent_throughput() is None

        # Test with insufficient data
        tracker.record_completion(1.0)
        assert tracker.get_recent_throughput() is None

        # Test with sufficient data
        tracker.record_completion(2.0)
        tracker.record_completion(3.0)
        tracker.record_completion(4.0)
        tracker.record_completion(5.0)

        # Should get recent throughput for last 5 completions
        recent = tracker.get_recent_throughput(last_n=5)
        assert recent is not None
        assert recent > 0

        # Test with zero time span
        tracker.record_completion(5.0)  # Same timestamp
        recent = tracker.get_recent_throughput(last_n=2)
        assert recent is None

    @pytest.mark.asyncio
    async def test_adaptive_error_backoff_logic(self):
        """Test error backoff logic in adaptive strategy."""
        strategy = AdaptiveStrategy(
            initial_concurrency=4,
            adaptation_interval=0.05,
            error_backoff_factor=0.5,
        )

        def create_tasks():
            # First task succeeds (much faster than second task)
            async def task1():
                await asyncio.sleep(0.001)  # Very quick task
                return "result_1"

            yield task1

            # Second task succeeds too (but slower)
            async def task2():
                await asyncio.sleep(0.005)
                return "result_2"

            yield task2

            # Third task fails
            async def task3():
                await asyncio.sleep(0.01)
                raise ValueError("error 1")

            yield task3

        results = []
        error_raised = False

        try:
            async for result in strategy.execute(create_tasks()):
                results.append(result)
        except ValueError:
            error_raised = True

        # Should have some results and error should be raised
        assert error_raised, "Expected ValueError to be raised"
        assert len(results) >= 1, f"Expected at least 1 result, got {len(results)}"

    @pytest.mark.asyncio
    async def test_adaptive_no_tasks_handling(self):
        """Test adaptive strategy with no tasks (empty iterator)."""
        strategy = AdaptiveStrategy(
            initial_concurrency=2,
            adaptation_interval=0.05,
        )

        def create_tasks():
            # Empty iterator
            return
            yield  # Never reached

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 0
        assert strategy.total_tasks == 0

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_increase_logic(self):
        """Test different concurrency increase scenarios."""
        strategy = AdaptiveStrategy(
            initial_concurrency=5,
            adaptation_interval=0.02,
            stability_window=1,  # Quick decisions
            min_concurrency=1,
            max_concurrency=100,
        )

        # Test increase from small values (should add 2)
        strategy.current_concurrency = 8
        strategy._increase_concurrency()
        assert strategy.current_concurrency == 10

        # Test increase from medium values (should multiply by 1.2)
        strategy.current_concurrency = 20
        strategy._increase_concurrency()
        assert strategy.current_concurrency == int(20 * 1.2)

        # Test increase from large values (should multiply by 1.1)
        strategy.current_concurrency = 60
        strategy._increase_concurrency()
        assert strategy.current_concurrency == int(60 * 1.1)

        # Test max concurrency limit
        strategy.current_concurrency = 95
        strategy._increase_concurrency()
        assert strategy.current_concurrency == 100  # Should be capped

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_decrease_logic(self):
        """Test concurrency decrease scenarios."""
        strategy = AdaptiveStrategy(
            initial_concurrency=10,
            min_concurrency=2,
            max_concurrency=100,
        )

        # Test normal decrease
        strategy.current_concurrency = 20
        strategy._decrease_concurrency()
        assert strategy.current_concurrency == int(20 * 0.8)

        # Test decrease with custom factor
        strategy.current_concurrency = 10
        strategy._decrease_concurrency(factor=0.5)
        assert strategy.current_concurrency == 5

        # Test min concurrency limit
        strategy.current_concurrency = 3
        strategy._decrease_concurrency()
        assert strategy.current_concurrency == 2  # Should be capped at min

    @pytest.mark.asyncio
    async def test_adaptive_stability_window_logic(self):
        """Test stability window logic for consistent increases/decreases."""
        strategy = AdaptiveStrategy(
            initial_concurrency=5,
            adaptation_interval=0.01,
            stability_window=3,  # Need 3 consecutive improvements
            min_concurrency=1,
            max_concurrency=50,
            increase_threshold=0.98,  # Need > 98% improvement to increase
        )

        # Set up initial state with some throughput history
        strategy.last_throughput = 10.0

        # Mock throughput tracker to simulate improving performance
        def mock_improving_throughput():
            # Simulate improving throughput over time
            return strategy.last_throughput * 1.1  # 10% improvement each time

        strategy.throughput_tracker.get_throughput = mock_improving_throughput

        initial_concurrency = strategy.current_concurrency

        # First adaptation - should not increase yet (need stability_window)
        strategy._adapt_concurrency()
        assert strategy.consecutive_increases == 1
        assert strategy.current_concurrency == initial_concurrency

        # Second adaptation - still not enough
        strategy._adapt_concurrency()
        assert strategy.consecutive_increases == 2
        assert strategy.current_concurrency == initial_concurrency

        # Third adaptation - should increase now
        strategy._adapt_concurrency()
        assert strategy.consecutive_increases == 0  # Reset after increase
        assert strategy.current_concurrency > initial_concurrency

        # Test decreasing throughput scenario
        def mock_decreasing_throughput():
            return strategy.last_throughput * 0.8  # 20% decrease each time

        strategy.throughput_tracker.get_throughput = mock_decreasing_throughput
        strategy.last_throughput = 10.0

        current_concurrency = strategy.current_concurrency

        # First decrease
        strategy._adapt_concurrency()
        assert strategy.consecutive_decreases == 1
        assert strategy.current_concurrency == current_concurrency

        # Second decrease
        strategy._adapt_concurrency()
        assert strategy.consecutive_decreases == 2
        assert strategy.current_concurrency == current_concurrency

        # Third decrease - should decrease now
        strategy._adapt_concurrency()
        assert strategy.consecutive_decreases == 0  # Reset after decrease
        assert strategy.current_concurrency < current_concurrency

    @pytest.mark.asyncio
    async def test_adaptive_multiple_errors_backoff(self):
        """Test multiple errors cause stronger backoff."""
        strategy = AdaptiveStrategy(
            initial_concurrency=8,
            error_backoff_factor=0.7,
        )

        # Set up with some throughput data first
        strategy.throughput_tracker.get_throughput = lambda: 10.0

        # Simulate multiple errors
        strategy.recent_errors = 3
        initial_concurrency = strategy.current_concurrency

        # Should decrease by factor^errors = 0.7^3
        strategy._adapt_concurrency()
        expected_concurrency = max(
            int(initial_concurrency * (0.7**3)), strategy.min_concurrency
        )
        assert strategy.current_concurrency == expected_concurrency
        assert strategy.recent_errors == 0  # Should reset after adaptation
