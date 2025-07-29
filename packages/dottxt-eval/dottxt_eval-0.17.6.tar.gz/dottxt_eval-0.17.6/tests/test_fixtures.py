import asyncio
import sys

import pytest

from doteval.fixtures import (
    _get_from_cache,
    clear_session_cache,
    fixture,
    setup_fixtures_for_evaluation,
)


def test_fixture_import():
    """Test that fixture can be imported from doteval."""
    from doteval import fixture

    assert fixture is not None
    assert callable(fixture)


def test_doteval_fixture_as_pytest_wrapper():
    """Test that @doteval.fixture works as a wrapper around pytest.fixture."""

    @fixture(scope="session")
    def session_fixture():
        return "session_value"

    @fixture(scope="evaluation")
    def eval_fixture():
        return "eval_value"

    @fixture(params=["a", "b", "c"])
    def param_fixture(request):
        return f"param_{request.param}"

    # Check that they have pytest fixture metadata
    assert hasattr(session_fixture, "_fixture_function_marker")
    assert hasattr(eval_fixture, "_fixture_function_marker")
    assert hasattr(param_fixture, "_fixture_function_marker")

    # Check that they have doteval metadata
    assert hasattr(session_fixture, "_doteval_fixture")
    assert hasattr(eval_fixture, "_doteval_fixture")
    assert hasattr(param_fixture, "_doteval_fixture")

    # Verify scope mapping
    assert session_fixture._fixture_function_marker.scope == "session"
    assert eval_fixture._fixture_function_marker.scope == "function"

    # Verify doteval metadata
    assert session_fixture._doteval_fixture["scope"] == "session"
    assert eval_fixture._doteval_fixture["scope"] == "evaluation"
    assert param_fixture._doteval_fixture["params"] == ["a", "b", "c"]


def test_doteval_fixture_backwards_compatibility():
    """Test that existing doteval.fixture usage patterns still work."""

    @fixture()  # default scope
    def default_fixture():
        return "default"

    @fixture(scope="session")  # explicit scope
    def scoped_fixture():
        return "scoped"

    @fixture(indirect=True)  # indirect
    def indirect_fixture(request):
        return request.param

    # Should have both pytest and doteval metadata
    assert hasattr(default_fixture, "_fixture_function_marker")
    assert hasattr(default_fixture, "_doteval_fixture")

    assert hasattr(scoped_fixture, "_fixture_function_marker")
    assert hasattr(scoped_fixture, "_doteval_fixture")

    assert hasattr(indirect_fixture, "_fixture_function_marker")
    assert hasattr(indirect_fixture, "_doteval_fixture")


@pytest.mark.asyncio
async def test_pytest_fixture_interoperability():
    """Test that pytest fixtures work alongside doteval fixtures."""

    # Create a regular pytest fixture
    @pytest.fixture(scope="session")
    def pytest_session_fixture():
        return "pytest_session_value"

    # Create a doteval fixture (which is now a pytest wrapper)
    @fixture(scope="session")
    def doteval_session_fixture():
        return "doteval_session_value"

    # Both should have pytest fixture metadata
    assert hasattr(pytest_session_fixture, "_fixture_function_marker")
    assert hasattr(doteval_session_fixture, "_fixture_function_marker")

    # Only doteval fixture should have doteval metadata
    assert not hasattr(pytest_session_fixture, "_doteval_fixture")
    assert hasattr(doteval_session_fixture, "_doteval_fixture")


@pytest.mark.asyncio
async def test_pure_pytest_fixture_resolution():
    """Test that the new fixture resolution system works with actual fixtures."""

    # Create some fixtures using the new @doteval.fixture decorator
    @fixture(scope="session")
    def session_fixture():
        return "session_value"

    @fixture(scope="evaluation")
    def eval_fixture():
        return "eval_value"

    @fixture(params=["a", "b", "c"])
    def param_fixture(request):
        return f"param_{request.param}"

    # Create evaluation function that uses these fixtures
    def eval_with_fixtures(session_fixture, eval_fixture):
        return {"session": session_fixture, "eval": eval_fixture}

    # Manually add fixtures to this module so they can be discovered
    current_module = sys.modules[__name__]
    setattr(current_module, "session_fixture", session_fixture)
    setattr(current_module, "eval_fixture", eval_fixture)
    setattr(current_module, "param_fixture", param_fixture)

    try:
        # Test fixture resolution
        fixtures = await setup_fixtures_for_evaluation(eval_with_fixtures)

        assert "session_fixture" in fixtures
        assert "eval_fixture" in fixtures
        assert fixtures["session_fixture"] == "session_value"
        assert fixtures["eval_fixture"] == "eval_value"

        # Test parametrized fixture
        def eval_with_param(param_fixture):
            return param_fixture

        param_fixtures = await setup_fixtures_for_evaluation(
            eval_with_param, fixture_params={"param_fixture": "a"}
        )

        assert param_fixtures["param_fixture"] == "param_a"

    finally:
        # Clean up
        if hasattr(current_module, "session_fixture"):
            delattr(current_module, "session_fixture")
        if hasattr(current_module, "eval_fixture"):
            delattr(current_module, "eval_fixture")
        if hasattr(current_module, "param_fixture"):
            delattr(current_module, "param_fixture")


@pytest.mark.asyncio
async def test_async_fixtures():
    """Test async fixtures work correctly."""

    @fixture()
    async def async_fixture():
        await asyncio.sleep(0.01)
        return "async_value"

    def eval_with_async(async_fixture):
        return async_fixture

    # Manually add fixture to module
    current_module = sys.modules[__name__]
    setattr(current_module, "async_fixture", async_fixture)

    try:
        fixtures = await setup_fixtures_for_evaluation(eval_with_async)
        assert fixtures["async_fixture"] == "async_value"
    finally:
        if hasattr(current_module, "async_fixture"):
            delattr(current_module, "async_fixture")


@pytest.mark.asyncio
async def test_indirect_fixtures():
    """Test indirect fixture functionality."""

    @fixture(indirect=True)
    def indirect_fixture(request):
        return f"indirect_{request.param}"

    def eval_with_indirect(indirect_fixture):
        return indirect_fixture

    # Manually add fixture to module
    current_module = sys.modules[__name__]
    setattr(current_module, "indirect_fixture", indirect_fixture)

    try:
        fixtures = await setup_fixtures_for_evaluation(
            eval_with_indirect, fixture_params={"indirect_fixture": "test_value"}
        )
        assert fixtures["indirect_fixture"] == "indirect_test_value"
    finally:
        if hasattr(current_module, "indirect_fixture"):
            delattr(current_module, "indirect_fixture")


@pytest.mark.asyncio
async def test_no_fixtures_needed():
    """Test evaluation function that doesn't need any fixtures."""

    def eval_func():
        return "no_fixtures"

    fixtures = await setup_fixtures_for_evaluation(eval_func)
    assert fixtures == {}


@pytest.mark.asyncio
async def test_missing_fixtures():
    """Test evaluation function that references non-existent fixtures."""

    def eval_func(nonexistent_fixture):
        return nonexistent_fixture

    # Should return empty dict when fixtures aren't found
    fixtures = await setup_fixtures_for_evaluation(eval_func)
    assert fixtures == {}


def test_get_from_cache_with_session_scoped_fixture():
    """Test _get_from_cache function with session-scoped fixture."""
    # Clear cache first
    clear_session_cache()

    # Store something in cache
    from doteval.fixtures import _session_fixture_cache

    _session_fixture_cache["test_key"] = "cached_value"

    # Test cache hit for session-scoped fixture
    result = _get_from_cache("test_key", is_session_scoped=True)
    assert result == "cached_value"

    # Test cache miss for non-session-scoped fixture
    result = _get_from_cache("test_key", is_session_scoped=False)
    assert result is None

    # Test cache miss for unknown key
    result = _get_from_cache("unknown_key", is_session_scoped=True)
    assert result is None


def test_clear_session_cache_function():
    """Test that clear_session_cache properly clears the cache."""
    from doteval.fixtures import _session_fixture_cache

    # Add something to cache
    _session_fixture_cache["test_key"] = "test_value"
    assert len(_session_fixture_cache) == 1

    # Clear cache
    clear_session_cache()
    assert len(_session_fixture_cache) == 0


@pytest.mark.asyncio
async def test_confeval_import_failure_handling():
    """Test that setup_fixtures_for_evaluation handles confeval import failures gracefully."""
    # Mock sys.modules to simulate import failure
    original_modules = sys.modules.copy()

    # Remove confeval if it exists and create a function that needs fixtures
    if "confeval" in sys.modules:
        del sys.modules["confeval"]

    def eval_func(some_fixture):
        return "test"

    try:
        # This should not raise an exception even if confeval can't be imported
        fixtures = await setup_fixtures_for_evaluation(eval_func)
        assert fixtures == {}  # No fixtures found, but no error
    finally:
        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)


@pytest.mark.asyncio
async def test_session_scoped_fixture_with_parameters():
    """Test session-scoped fixture with parameters to cover cache key generation."""
    clear_session_cache()

    @fixture(scope="session", params=["value1", "value2"])
    def param_session_fixture(request):
        return f"session_{request.param}"

    def eval_with_param_session(param_session_fixture):
        return param_session_fixture

    # Add fixture to module
    current_module = sys.modules[__name__]
    setattr(current_module, "param_session_fixture", param_session_fixture)

    try:
        # First call - should execute and cache
        fixtures1 = await setup_fixtures_for_evaluation(
            eval_with_param_session, fixture_params={"param_session_fixture": "value1"}
        )
        assert fixtures1["param_session_fixture"] == "session_value1"

        # Second call with same param - should use cache
        fixtures2 = await setup_fixtures_for_evaluation(
            eval_with_param_session, fixture_params={"param_session_fixture": "value1"}
        )
        assert fixtures2["param_session_fixture"] == "session_value1"

        # Third call with different param - should execute again
        fixtures3 = await setup_fixtures_for_evaluation(
            eval_with_param_session, fixture_params={"param_session_fixture": "value2"}
        )
        assert fixtures3["param_session_fixture"] == "session_value2"

    finally:
        if hasattr(current_module, "param_session_fixture"):
            delattr(current_module, "param_session_fixture")
        clear_session_cache()
