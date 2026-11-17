"""
Benchmark suite runner: Evaluates agent architectures against a test dataset of algorithmic tasks.
"""

from typing import List, Dict, Any
from .schemas import TaskSpec, BenchmarkReport
from .orchestrator import MultiAgentOrchestrator


class BenchmarkRunner:
    def __init__(self, orchestrator: MultiAgentOrchestrator):
        self.orchestrator = orchestrator

    def run_benchmark(self, tasks: List[TaskSpec]) -> BenchmarkReport:
        total = len(tasks)
        passed = 0
        total_iterations = 0
        detailed_results: List[Dict[str, Any]] = []

        for task in tasks:
            result = self.orchestrator.solve_task(task)
            if result["success"]:
                passed += 1
            total_iterations += result["iterations"]
            detailed_results.append(result)

        pass_rate = (passed / total * 100.0) if total > 0 else 0.0
        avg_iterations = (total_iterations / total) if total > 0 else 0.0

        return BenchmarkReport(
            total_tasks=total,
            passed_tasks=passed,
            pass_rate=pass_rate,
            total_iterations=total_iterations,
            avg_iterations_per_task=avg_iterations,
            results=detailed_results,
        )
