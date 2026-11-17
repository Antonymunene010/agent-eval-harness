#!/usr/bin/env python3
"""
Autonomous Multi-Agent Evaluation Demo:
Demonstrates automated task decomposition, execution in a sandboxed runner,
error-feedback loop, and benchmark metric compilation.
"""

from agent_eval_harness.schemas import TaskSpec
from agent_eval_harness.orchestrator import MultiAgentOrchestrator
from agent_eval_harness.benchmark import BenchmarkRunner


def simulated_agent_brain(role: str, messages) -> str:
    """
    Deterministic solver engine simulating intelligent agent reasoning.
    """
    last_msg = messages[-1].content
    if role == "planner":
        return "1. Identify edge cases. 2. Implement solution adhering strictly to input/output constraints. 3. Return clean function."
    elif role == "coder":
        if "fibonacci" in last_msg:
            return "```python\ndef fibonacci(n: int) -> int:\n    if n <= 0: return 0\n    elif n == 1: return 1\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n```"
        elif "reverse_words" in last_msg:
            return "```python\ndef reverse_words(s: str) -> str:\n    return ' '.join(s.strip().split()[::-1])\n```"
        elif "is_prime" in last_msg:
            return "```python\ndef is_prime(n: int) -> bool:\n    if n < 2: return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0: return False\n    return True\n```"
        else:
            return "```python\ndef solution(*args): return True\n```"
    return ""


def main():
    print("==================================================")
    print(" AUTONOMOUS MULTI-AGENT EVALUATION HARNESS DEMO   ")
    print("==================================================")

    # 1. Define benchmark task suite
    tasks = [
        TaskSpec(
            task_id="algo_001_fib",
            prompt="Write a function fibonacci(n) returning the n-th Fibonacci number.",
            entrypoint="fibonacci",
            test_cases=[
                "assert fibonacci(0) == 0",
                "assert fibonacci(1) == 1",
                "assert fibonacci(10) == 55",
            ],
        ),
        TaskSpec(
            task_id="algo_002_words",
            prompt="Write a function reverse_words(s) reversing the order of words in a string.",
            entrypoint="reverse_words",
            test_cases=[
                "assert reverse_words('hello world') == 'world hello'",
                "assert reverse_words('  quick brown fox  ') == 'fox brown quick'",
            ],
        ),
        TaskSpec(
            task_id="algo_003_prime",
            prompt="Write a function is_prime(n) checking primality.",
            entrypoint="is_prime",
            test_cases=[
                "assert is_prime(2) == True",
                "assert is_prime(17) == True",
                "assert is_prime(4) == False",
                "assert is_prime(1) == False",
            ],
        ),
    ]

    print(f"[*] Loaded {len(tasks)} algorithmic benchmark tasks.\n")

    # 2. Run benchmark
    orchestrator = MultiAgentOrchestrator(llm_fn=simulated_agent_brain, max_iterations=3)
    runner = BenchmarkRunner(orchestrator)
    report = runner.run_benchmark(tasks)

    # 3. Print summary report
    print("--------------------------------------------------")
    print(" BENCHMARK RESULTS")
    print("--------------------------------------------------")
    print(f"Total Tasks:          {report.total_tasks}")
    print(f"Passed Tasks:         {report.passed_tasks}")
    print(f"Pass Rate:            {report.pass_rate:.1f}%")
    print(f"Avg Iterations/Task:  {report.avg_iterations_per_task:.2f}")
    print("--------------------------------------------------")

    for res in report.results:
        status = "PASSED [OK]" if res["success"] else "FAILED [X]"
        print(f"Task {res['task_id']:<18} | {status} | {res['iterations']} iteration(s)")

    print("\n[*] Multi-Agent evaluation completed successfully.")


if __name__ == "__main__":
    main()
