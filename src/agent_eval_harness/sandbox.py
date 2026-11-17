"""
Isolated Python subprocess execution sandbox with timeout enforcement and error interception.
"""

import sys
import subprocess
import time
from typing import List
from .schemas import ExecutionResult


class SandboxedPythonRunner:
    def __init__(self, default_timeout: float = 3.0):
        self.default_timeout = default_timeout

    def run_code_with_tests(self, code: str, test_cases: List[str], timeout: float = None) -> ExecutionResult:
        """
        Executes candidate code followed by test assertions in an isolated Python interpreter.
        """
        timeout = timeout or self.default_timeout

        # Construct self-contained evaluation script
        harness_script = code + "\n\n# --- Test Assertions ---\n"
        for idx, test in enumerate(test_cases, 1):
            escaped_test = test.replace('\\', '\\\\').replace('"', '\\"')
            harness_script += (
                f"try:\n"
                f"    {test}\n"
                f"except AssertionError:\n"
                f"    raise AssertionError(\"Test {idx} failed: {escaped_test}\")\n"
            )

        t0 = time.perf_counter()
        try:
            process = subprocess.run(
                [sys.executable, "-c", harness_script],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000

            if process.returncode == 0:
                return ExecutionResult(
                    success=True,
                    stdout=process.stdout,
                    stderr=process.stderr,
                    execution_time_ms=elapsed_ms,
                )
            else:
                error_type = "ExecutionError"
                if "AssertionError" in process.stderr:
                    error_type = "AssertionError"
                elif "SyntaxError" in process.stderr:
                    error_type = "SyntaxError"
                elif "NameError" in process.stderr:
                    error_type = "NameError"
                elif "TypeError" in process.stderr:
                    error_type = "TypeError"

                return ExecutionResult(
                    success=False,
                    stdout=process.stdout,
                    stderr=process.stderr,
                    error_type=error_type,
                    execution_time_ms=elapsed_ms,
                )

        except subprocess.TimeoutExpired:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            return ExecutionResult(
                success=False,
                stderr=f"TimeoutExpired: Execution exceeded limit of {timeout}s",
                error_type="TimeoutError",
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            return ExecutionResult(
                success=False,
                stderr=str(e),
                error_type=type(e).__name__,
                execution_time_ms=elapsed_ms,
            )
