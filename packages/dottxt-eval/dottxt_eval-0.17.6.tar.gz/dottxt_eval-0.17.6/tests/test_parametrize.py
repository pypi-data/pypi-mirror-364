import pytest

from doteval import parametrize


def test_parametrize_simple_string_list():
    """Test parametrize with simple string and list of values."""

    @parametrize("temp", [0, 0.5, 1.0])
    def test_func(temp):
        assert temp in [0, 0.5, 1.0]

    # Check that the function has the doteval metadata
    assert hasattr(test_func, "_doteval_parametrize")
    metadata = test_func._doteval_parametrize
    assert metadata["argnames"] == ["temp"]
    assert metadata["argvalues"] == [0, 0.5, 1.0]
    assert metadata["original_args"] == ("temp", [0, 0.5, 1.0])

    # Check that pytest marks are applied
    assert hasattr(test_func, "pytestmark")
    assert any(mark.name == "parametrize" for mark in test_func.pytestmark)


def test_parametrize_dict_format():
    """Test parametrize with dictionary format."""

    @parametrize({"temp": [0, 0.5], "model": ["gpt-4"]})
    def test_func(temp, model):
        assert temp in [0, 0.5]
        assert model == "gpt-4"

    # Check that the function has the doteval metadata
    assert hasattr(test_func, "_doteval_parametrize")
    metadata = test_func._doteval_parametrize
    assert set(metadata["argnames"]) == {"temp", "model"}
    assert metadata["argvalues"] == [(0, "gpt-4"), (0.5, "gpt-4")]
    assert metadata["original_args"] == ({"temp": [0, 0.5], "model": ["gpt-4"]},)


def test_parametrize_kwargs_format():
    """Test parametrize with keyword arguments."""

    @parametrize(temp=[0, 0.5], model=["gpt-4"])
    def test_func(temp, model):
        assert temp in [0, 0.5]
        assert model == "gpt-4"

    # Check that the function has the doteval metadata
    assert hasattr(test_func, "_doteval_parametrize")
    metadata = test_func._doteval_parametrize
    assert set(metadata["argnames"]) == {"temp", "model"}
    assert metadata["argvalues"] == [(0, "gpt-4"), (0.5, "gpt-4")]
    assert metadata["original_kwargs"] == {"temp": [0, 0.5], "model": ["gpt-4"]}


def test_parametrize_multiple_values_dict():
    """Test parametrize with multiple values in dict format."""

    @parametrize({"temp": [0, 0.5], "model": ["gpt-3.5", "gpt-4"]})
    def test_func(temp, model):
        assert temp in [0, 0.5]
        assert model in ["gpt-3.5", "gpt-4"]

    # Check that the function has the doteval metadata
    assert hasattr(test_func, "_doteval_parametrize")
    metadata = test_func._doteval_parametrize
    assert set(metadata["argnames"]) == {"temp", "model"}
    # Should have 2 * 2 = 4 combinations
    assert len(metadata["argvalues"]) == 4
    expected_values = [(0, "gpt-3.5"), (0, "gpt-4"), (0.5, "gpt-3.5"), (0.5, "gpt-4")]
    assert set(metadata["argvalues"]) == set(expected_values)


def test_parametrize_multiple_values_kwargs():
    """Test parametrize with multiple values in kwargs format."""

    @parametrize(temp=[0, 0.5], model=["gpt-3.5", "gpt-4"])
    def test_func(temp, model):
        assert temp in [0, 0.5]
        assert model in ["gpt-3.5", "gpt-4"]

    # Check that the function has the doteval metadata
    assert hasattr(test_func, "_doteval_parametrize")
    metadata = test_func._doteval_parametrize
    assert set(metadata["argnames"]) == {"temp", "model"}
    # Should have 2 * 2 = 4 combinations
    assert len(metadata["argvalues"]) == 4
    expected_values = [(0, "gpt-3.5"), (0, "gpt-4"), (0.5, "gpt-3.5"), (0.5, "gpt-4")]
    assert set(metadata["argvalues"]) == set(expected_values)


def test_parametrize_string_with_commas():
    """Test parametrize with comma-separated string."""

    @parametrize("temp,model", [(0, "gpt-4"), (0.5, "gpt-3.5")])
    def test_func(temp, model):
        assert temp in [0, 0.5]
        assert model in ["gpt-4", "gpt-3.5"]

    # Check that the function has the doteval metadata
    assert hasattr(test_func, "_doteval_parametrize")
    metadata = test_func._doteval_parametrize
    assert metadata["argnames"] == ["temp", "model"]
    assert metadata["argvalues"] == [(0, "gpt-4"), (0.5, "gpt-3.5")]


def test_parametrize_invalid_usage():
    """Test that invalid usage raises ValueError."""
    with pytest.raises(ValueError, match="Invalid parametrize usage"):

        @parametrize()
        def test_func():
            pass

    with pytest.raises(ValueError, match="Invalid parametrize usage"):

        @parametrize([1, 2, 3])  # List without argnames
        def test_func_2():
            pass


def test_parametrize_pytest_compatibility():
    """Test that parametrized functions work with pytest."""

    @parametrize("value", [1, 2, 3])
    def test_values(value):
        assert isinstance(value, int)
        assert value > 0

    # The function should have pytest marks
    assert hasattr(test_values, "pytestmark")
    parametrize_marks = [
        mark for mark in test_values.pytestmark if mark.name == "parametrize"
    ]
    assert len(parametrize_marks) == 1

    # Check the mark arguments
    mark = parametrize_marks[0]
    assert mark.args == ("value", [1, 2, 3])
