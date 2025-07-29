import asyncio
import inspect
import sys
from typing import Any, Dict, List, Optional, Union

import pytest

# Global fixture cache for session-scoped fixtures
_session_fixture_cache: Dict[str, Any] = {}


class DotevalFixture:
    """Wrapper that provides doteval API while using pytest.fixture internally.

    This follows the same pattern as @doteval.parametrize - providing a
    doteval-friendly API while leveraging pytest's actual functionality.
    """

    def __init__(
        self,
        scope="evaluation",
        indirect: Union[bool, List[str]] = False,
        params: Optional[List[Any]] = None,
    ):
        self.scope = scope
        self.indirect = indirect
        self.params = params

    def __call__(self, func):
        # Map doteval scope to pytest scope
        scope_mapping = {
            "evaluation": "function",  # evaluation -> function scope
            "session": "session",  # session -> session scope
        }
        pytest_scope = scope_mapping.get(self.scope, "function")

        # Store doteval metadata on the function for later use
        func._doteval_fixture = {
            "scope": self.scope,
            "indirect": self.indirect,
            "params": self.params,
            "original_func": func,
        }

        # Apply pytest.fixture with appropriate parameters
        if self.params:
            # For parametrized fixtures, use pytest's params
            return pytest.fixture(scope=pytest_scope, params=self.params)(func)
        else:
            # Regular fixture
            return pytest.fixture(scope=pytest_scope)(func)


def get_fixture_names_from_function(func) -> List[str]:
    """Extract fixture parameter names from a function signature."""
    if hasattr(func, "__wrapped__") and func.__wrapped__ is not func:
        sig = inspect.signature(func.__wrapped__)
    else:
        sig = inspect.signature(func)

    return [param_name for param_name in sig.parameters]


def discover_fixtures_in_module(module) -> Dict[str, Any]:
    """Discover all pytest fixtures (including doteval fixtures) in a module."""
    fixtures = {}

    for name, obj in inspect.getmembers(module):
        # Check if it's a pytest fixture (includes doteval fixtures)
        if hasattr(obj, "_fixture_function_marker"):
            fixtures[name] = obj

    return fixtures


def _create_request_object(param_value):
    """Create a request-like object for parametrized/indirect fixtures."""
    return type("Request", (), {"param": param_value})()


async def _execute_fixture_function(fixture_func, request=None):
    """Execute fixture function handling both async and sync cases."""
    if asyncio.iscoroutinefunction(fixture_func):
        return await fixture_func(request) if request else await fixture_func()
    else:
        return fixture_func(request) if request else fixture_func()


def _get_cache_key(fixture_name: str, param_value=None) -> str:
    """Generate consistent cache key for fixtures."""
    return f"{fixture_name}[{param_value}]" if param_value is not None else fixture_name


def _get_from_cache(cache_key: str, is_session_scoped: bool):
    """Retrieve fixture from cache if available and session-scoped."""
    if is_session_scoped and cache_key in _session_fixture_cache:
        return _session_fixture_cache[cache_key]
    return None


def _store_in_cache(cache_key: str, result, is_session_scoped: bool):
    """Store fixture result in cache if session-scoped."""
    if is_session_scoped:
        _session_fixture_cache[cache_key] = result


async def setup_fixtures_for_evaluation(
    eval_func, fixture_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Setup fixtures for an evaluation function using pytest's fixture system.

    This is the key function that bridges doteval evaluations with pytest fixtures.

    Args:
        eval_func: The evaluation function that needs fixtures
        fixture_params: Optional parameter values for indirect/parametrized fixtures

    Returns:
        Dictionary of fixture name -> fixture value for the evaluation function
    """
    if fixture_params is None:
        fixture_params = {}

    # Get fixture names needed by the evaluation function
    fixture_names = get_fixture_names_from_function(eval_func)

    # Discover available fixtures from confeval.py and eval function's module
    available_fixtures = {}

    # Try to load fixtures from confeval.py
    try:
        import confeval

        available_fixtures.update(discover_fixtures_in_module(confeval))
    except ImportError:
        pass

    # Also check the evaluation function's own module
    eval_module = sys.modules.get(eval_func.__module__)
    if eval_module:
        available_fixtures.update(discover_fixtures_in_module(eval_module))

    # Resolve fixtures
    resolved_fixtures = {}

    for fixture_name in fixture_names:
        if fixture_name in available_fixtures:
            fixture_obj = available_fixtures[fixture_name]

            # Get the actual fixture function
            fixture_func = getattr(fixture_obj, "_fixture_function", fixture_obj)

            # Get doteval fixture metadata
            doteval_meta = getattr(fixture_obj, "_doteval_fixture", {})
            is_session_scoped = doteval_meta.get("scope") == "session"

            # Determine fixture type and parameters
            has_params = doteval_meta.get("params") and fixture_name in fixture_params
            is_indirect = (
                doteval_meta.get("indirect") and fixture_name in fixture_params
            )
            param_value = (
                fixture_params.get(fixture_name)
                if (has_params or is_indirect)
                else None
            )

            # Generate cache key
            cache_key = _get_cache_key(fixture_name, param_value)

            # Check cache first
            cached_result = _get_from_cache(cache_key, is_session_scoped)
            if cached_result is not None:
                resolved_fixtures[fixture_name] = cached_result
                continue

            # Execute fixture
            request = (
                _create_request_object(param_value) if param_value is not None else None
            )
            result = await _execute_fixture_function(fixture_func, request)

            resolved_fixtures[fixture_name] = result

            # Store in cache if session-scoped
            _store_in_cache(cache_key, result, is_session_scoped)

    return resolved_fixtures


def clear_session_cache():
    """Clear the session fixture cache. Useful for testing."""
    global _session_fixture_cache
    _session_fixture_cache.clear()


# Make it feel native - just like @doteval.parametrize
fixture = DotevalFixture
