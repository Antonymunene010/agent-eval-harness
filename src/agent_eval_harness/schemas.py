"""
Data models and schemas for tasks, agent messages, execution outputs, and benchmark reports.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TaskSpec(BaseModel):
    task_id: str
    prompt: str
    test_cases: List[str] = Field(default_factory=list, description="Python assert statements")
    entrypoint: str = "solution"
    timeout_seconds: float = 3.0


class AgentMessage(BaseModel):
    role: str  # "planner", "coder", "evaluator", "system"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""
    error_type: Optional[str] = None
    execution_time_ms: float = 0.0


class BenchmarkReport(BaseModel):
    total_tasks: int
    passed_tasks: int
    pass_rate: float
    total_iterations: int
    avg_iterations_per_task: float
    results: List[Dict[str, Any]]
