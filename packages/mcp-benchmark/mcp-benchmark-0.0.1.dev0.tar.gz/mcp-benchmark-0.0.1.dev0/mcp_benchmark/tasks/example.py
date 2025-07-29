
from mcp_benchmark.tasks import task, evaluation_function

@task(
    intent="Add two numbers",
    requires_context=False,
)
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b


@evaluation_function(task=add)
def is_correct(output: int, expected: int) -> bool:
    """Checks if the output is correct."""
    return output == expected
