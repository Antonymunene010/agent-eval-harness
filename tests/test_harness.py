"""
Unit tests for sandbox execution, error trapping, timeout handling, and agent self-correction.
"""

import pytest
from agent_eval_harness.schemas import TaskSpec
from agent_eval_harness.sandbox import SandboxedPythonRunner
from agent_eval_harness.orchestrator import MultiAgentOrchestrator


def test_sandbox_success():
    runner = SandboxedPythonRunner()
    code = "def add(a, b):\n    return a + b\n"
    tests = ["assert add(2, 3) == 5", "assert add(-1, 1) == 0"]
    result = runner.run_code_with_tests(code, tests)
    assert result.success is True
    assert result.error_type is None


def test_sandbox_assertion_failure():
    runner = SandboxedPythonRunner()
    code = "def add(a, b):\n    return a - b\n"
    tests = ["assert add(2, 3) == 5"]
    result = runner.run_code_with_tests(code, tests)
    assert result.success is False
    assert result.error_type == "AssertionError"
    assert "Test 1 failed" in result.stderr


def test_sandbox_timeout():
    runner = SandboxedPythonRunner()
    code = "def loop():\n    while True:\n        pass\nloop()\n"
    result = runner.run_code_with_tests(code, [], timeout=0.5)
    assert result.success is False
    assert result.error_type == "TimeoutError"


def test_orchestrator_self_correction():
    """
    Simulate an agent that fails on the 1st attempt and self-corrects on the 2nd attempt.
    """
    call_count = {"count": 0}

    def mock_llm_fn(role, messages):
        if role == "planner":
            return "Plan: Implement factorial function."
        elif role == "coder":
            call_count["count"] += 1
            if call_count["count"] == 1:
                # Buggy implementation on attempt 1 (off by one error)
                return "```python\ndef factorial(n):\n    return 0\n```"
            else:
                # Correct implementation on attempt 2 after feedback
                return "```python\ndef factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)\n```"
        return ""

    task = TaskSpec(
        task_id="task_factorial",
        prompt="Write a recursive factorial function",
        entrypoint="factorial",
        test_cases=["assert factorial(3) == 6", "assert factorial(0) == 1"],
    )

    orchestrator = MultiAgentOrchestrator(llm_fn=mock_llm_fn, max_iterations=3)
    result = orchestrator.solve_task(task)

    assert result["success"] is True
    assert result["iterations"] == 2
    assert "factorial" in result["final_code"]
