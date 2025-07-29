# Fixture Integration

doteval integrates with pytest-style fixtures to provide efficient resource sharing for LLM evaluations.

## Overview

Fixtures in doteval allow you to:

- **Share expensive resources** like models across multiple evaluations
- **Initialize once, use many times** - avoiding repeated model loading
- **Manage dependencies** like API clients, databases, or configuration
- **Control resource scope** (session vs evaluation)

## Why Fixtures Matter for LLM Evaluations

**Performance**: Loading a model once vs. loading it for each of 1000+ samples
**Resource sharing**: Multiple evaluations can share the same model instance
**Configuration**: Centralized setup for API keys, model parameters, etc.

## Basic Fixture Usage

Create fixtures using the `@fixture` decorator from doteval:

```python
from doteval import fixture, foreach
from doteval.evaluators import exact_match

@fixture(scope="session")
def model():
    """Initialize model once for all evaluations."""
    # This expensive operation happens only once
    return YourModel()

@fixture(scope="session")
def template():
    """Create a prompt template."""
    return "Q: {question}\nA:"

dataset = [("What is 2+2?", "4"), ("What is 3+3?", "6")]

@foreach("question,answer", dataset)
def eval_math_with_fixtures(question, answer, model, template):
    prompt = template.format(question=question)
    result = model.generate(prompt)
    return exact_match(result, answer)
```

## Fixture Scopes

doteval supports two fixture scopes:

### Session Scope
- **When**: Resources shared across all evaluations in a session
- **Use for**: Expensive models, database connections, configuration
- **Lifecycle**: Created once at session start, destroyed at session end

```python
@fixture(scope="session")
def expensive_model():
    """Load expensive model once per session."""
    return load_large_model()  # Called only once

@fixture(scope="session")
def database_connection():
    """Share database connection across evaluations."""
    return create_db_connection()
```

### Evaluation Scope
- **When**: Fresh resources for each evaluation function
- **Use for**: Temporary directories, fresh API clients, per-evaluation state
- **Lifecycle**: Created fresh for each evaluation, destroyed after evaluation

```python
@fixture(scope="evaluation")
def api_client():
    """Create fresh API client for each evaluation."""
    return APIClient(rate_limit=60)

@fixture(scope="evaluation")
def temp_directory():
    """Create temporary directory for each evaluation."""
    return tempfile.mkdtemp()
```

## Parametrized Fixtures

Use parametrized fixtures to run evaluations across different configurations:

```python
@fixture(params=["gpt-4", "claude-3", "gemini-pro"])
def model_name(request):
    """Parametrized fixture for different model names."""
    return request.param

@fixture(params=[0.0, 0.5, 1.0])
def temperature(request):
    """Parametrized fixture for different temperature values."""
    return request.param

@foreach("question,answer", dataset)
def eval_with_params(question, answer, model_name, temperature):
    """This evaluation runs for all parameter combinations."""
    model = load_model(model_name, temperature=temperature)
    result = model.generate(question)
    return exact_match(result, answer)
```

## Indirect Fixtures

Indirect fixtures process input parameters before use:

```python
@fixture(indirect=True)
def dataset_sample(request):
    """Process dataset samples with additional metadata."""
    sample = request.param
    return {
        "id": sample.get("id", "unknown"),
        "question": sample.get("question", ""),
        "expected": sample.get("expected", None),
        "processed": True
    }

@foreach("sample", samples)
def eval_with_indirect(sample, dataset_sample):
    """Uses processed sample from indirect fixture."""
    return exact_match(
        model.generate(dataset_sample["question"]),
        dataset_sample["expected"]
    )
```

## Async Fixtures

doteval supports async fixtures for asynchronous resource initialization:

```python
@fixture(scope="session")
async def async_model():
    """Async fixture for loading models asynchronously."""
    model = await load_async_model()
    await model.initialize()
    return model

@foreach("question,answer", dataset)
async def eval_async_with_fixture(question, answer, async_model):
    """Async evaluation using async fixtures."""
    result = await async_model.generate_async(question)
    return exact_match(result, answer)
```

## Fixture Organization

### Module-Level Fixtures
Define fixtures in your evaluation modules:

```python
# eval_math.py
from doteval import fixture, foreach

@fixture(scope="session")
def math_model():
    return MathSpecificModel()

@foreach("problem,solution", math_dataset)
def eval_math_problems(problem, solution, math_model):
    return math_model.solve(problem) == solution
```

### Shared Fixtures with confeval.py
Create shared fixtures in `confeval.py` for reuse across evaluations:

```python
# confeval.py
from doteval import fixture

@fixture(scope="session")
def shared_model():
    """Model shared across all evaluations."""
    return YourSharedModel()

@fixture(scope="session")
def config():
    """Configuration shared across evaluations."""
    return {
        "max_tokens": 1000,
        "timeout": 30,
        "api_key": os.getenv("API_KEY")
    }
```

Then use in any evaluation file:

```python
# eval_reasoning.py
@foreach("prompt,expected", reasoning_dataset)
def eval_reasoning(prompt, expected, shared_model, config):
    """Uses fixtures from confeval.py automatically."""
    result = shared_model.generate(
        prompt,
        max_tokens=config["max_tokens"]
    )
    return exact_match(result, expected)
```

## Running Evaluations with Fixtures

Use the doteval CLI to run evaluations with fixtures:

```bash
# Basic evaluation - fixtures are automatically resolved
doteval run eval_math.py --experiment math_baseline

# With parameters for parametrized fixtures
doteval run eval_models.py --experiment model_comparison --samples 1000

# Resume interrupted evaluation - session fixtures are cached
doteval run eval_math.py --experiment math_baseline  # Resumes and reuses session fixtures
```

## Best Practices

### Fixture Scope Selection

```python
# Session scope for expensive, immutable resources
@fixture(scope="session")
def large_language_model():
    return load_expensive_model()  # Called once

# Evaluation scope for stateful or temporary resources
@fixture(scope="evaluation")
def api_client_with_state():
    return StatefulAPIClient()  # Fresh instance per evaluation
```

### Error Handling

```python
@fixture(scope="session")
def robust_model():
    """Fixture with error handling."""
    try:
        return load_model()
    except Exception as e:
        # Log error, return fallback, or re-raise
        logger.error(f"Model loading failed: {e}")
        return FallbackModel()
```

### Resource Cleanup

```python
@fixture(scope="session")
def managed_resource():
    """Fixture with cleanup."""
    resource = create_expensive_resource()
    yield resource  # Provide resource to evaluations
    # Cleanup after all evaluations complete
    resource.cleanup()
```

## Integration with Standard pytest Fixtures

doteval fixtures work alongside standard pytest fixtures:

```python
import pytest
from doteval import fixture

# Standard pytest fixture
@pytest.fixture(scope="session")
def pytest_config():
    return {"setting": "value"}

# doteval fixture
@fixture(scope="session")
def doteval_model():
    return YourModel()

# Both can be used together
@foreach("question,answer", dataset)
def eval_mixed_fixtures(question, answer, pytest_config, doteval_model):
    """Uses both pytest and doteval fixtures."""
    result = doteval_model.generate(question)
    return exact_match(result, answer)
```

## Fixture Discovery

doteval automatically discovers fixtures from:
1. **confeval.py** - Shared fixtures for all evaluations
2. **Evaluation modules** - Module-specific fixtures
3. **Standard pytest fixtures** - Full compatibility

No additional configuration required - fixtures are resolved automatically based on evaluation function parameters.
