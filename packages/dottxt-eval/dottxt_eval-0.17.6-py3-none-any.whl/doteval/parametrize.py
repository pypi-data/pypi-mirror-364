import itertools

import pytest


class DotevalParam:
    """Wrapper that provides both doteval API and pytest compatibility."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        # Convert doteval API to pytest.mark.parametrize
        if len(self.args) == 2 and isinstance(self.args[0], str):
            # Simple: @parametrize("temp", [0, 0.5, 1.0])
            argnames = self.args[0]
            argvalues = self.args[1]

        elif len(self.args) == 1 and isinstance(self.args[0], dict):
            # Dict: @parametrize({"temp": [0, 0.5], "model": ["gpt-4"]})
            params_dict = self.args[0]
            argnames = list(params_dict.keys())
            argvalues = list(itertools.product(*params_dict.values()))

        elif self.kwargs:
            # Kwargs: @parametrize(temp=[0, 0.5], model=["gpt-4"])
            argnames = list(self.kwargs.keys())
            argvalues = list(itertools.product(*self.kwargs.values()))

        else:
            raise ValueError("Invalid parametrize usage")

        # Store doteval metadata
        func._doteval_parametrize = {
            "argnames": argnames if isinstance(argnames, list) else argnames.split(","),
            "argvalues": argvalues,
            "original_args": self.args,
            "original_kwargs": self.kwargs,
        }

        # Apply pytest's parametrize so discovery works
        return pytest.mark.parametrize(argnames, argvalues)(func)


# Make it feel native
parametrize = DotevalParam
