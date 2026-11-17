"""
Multi-Agent Orchestration loop: Planner -> Coder -> Evaluator -> Self-Correction Loop.
"""

from typing import Callable, Optional, Dict, Any, List
import re
from .schemas import TaskSpec, AgentMessage, ExecutionResult
from .sandbox import SandboxedPythonRunner


class MultiAgentOrchestrator:
    def __init__(
        self,
        llm_fn: Optional[Callable[[str, List[AgentMessage]], str]] = None,
        sandbox: Optional[SandboxedPythonRunner] = None,
        max_iterations: int = 3,
    ):
        self.llm_fn = llm_fn
        self.sandbox = sandbox or SandboxedPythonRunner()
        self.max_iterations = max_iterations

    def _extract_code_blocks(self, text: str) -> str:
        """Extract Python code blocks from markdown fences or bare code."""
        pattern = r"```(?:python)?\s*(.*?)\s*```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()
        return text.strip()

    def solve_task(self, task: TaskSpec) -> Dict[str, Any]:
        """
        Executes the collaborative agent loop:
        1. Planner specifies requirements.
        2. Coder writes Python code.
        3. Sandbox tests code.
        4. If failure, Coder self-corrects using execution traceback.
        """
        history: List[AgentMessage] = []
        iterations = 0
        final_code = ""
        last_exec_result: Optional[ExecutionResult] = None

        # 1. Planner Phase
        plan_content = f"Break down implementation for: {task.prompt}"
        if self.llm_fn:
            plan = self.llm_fn("planner", [AgentMessage(role="user", content=task.prompt)])
        else:
            plan = f"# Plan: 1. Parse inputs. 2. Implement core logic for {task.entrypoint}. 3. Handle edge cases."

        history.append(AgentMessage(role="planner", content=plan))

        # 2. Collaborative Code & Feedback Loop
        current_error_feedback = ""
        for i in range(1, self.max_iterations + 1):
            iterations += 1

            coder_prompt = (
                f"Task: {task.prompt}\n"
                f"Entrypoint: {task.entrypoint}\n"
                f"Plan: {plan}\n"
            )
            if current_error_feedback:
                coder_prompt += f"\nPrevious attempt failed with error:\n{current_error_feedback}\nPlease correct the implementation."

            if self.llm_fn:
                raw_code = self.llm_fn("coder", history + [AgentMessage(role="user", content=coder_prompt)])
                code = self._extract_code_blocks(raw_code)
            else:
                # Deterministic fallback logic for mock testing
                code = f"def {task.entrypoint}(*args, **kwargs):\n    pass"

            history.append(AgentMessage(role="coder", content=code, metadata={"iteration": i}))
            final_code = code

            # 3. Evaluator / Sandbox Execution
            exec_result = self.sandbox.run_code_with_tests(
                code=code,
                test_cases=task.test_cases,
                timeout=task.timeout_seconds,
            )
            last_exec_result = exec_result

            if exec_result.success:
                history.append(AgentMessage(
                    role="evaluator",
                    content="All test cases passed successfully.",
                    metadata={"iteration": i, "status": "PASSED"},
                ))
                break
            else:
                current_error_feedback = f"{exec_result.error_type}: {exec_result.stderr}"
                history.append(AgentMessage(
                    role="evaluator",
                    content=f"Execution failed:\n{current_error_feedback}",
                    metadata={"iteration": i, "status": "FAILED"},
                ))

        success = last_exec_result.success if last_exec_result else False
        return {
            "task_id": task.task_id,
            "success": success,
            "iterations": iterations,
            "final_code": final_code,
            "execution_result": last_exec_result.model_dump() if last_exec_result else {},
            "history": [msg.model_dump() for msg in history],
        }
