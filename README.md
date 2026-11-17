# agent-eval-harness

An extensible framework for **Autonomous Multi-Agent Orchestration & Evaluation Benchmarking**.

This repository implements a collaborative multi-agent architecture (Planner $\to$ Coder $\to$ Evaluator) equipped with isolated subprocess code execution, schema validation, and automated self-correction loops.

---

## Architecture Overview

```
User Task Specification
         │
         ▼
┌───────────────────┐
│   Planner Agent   │  Decomposes task into structured sub-requirements
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│    Coder Agent    │  Generates executable Python implementation
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Sandboxed Runner  │  Executes code + unit assertions in isolated process
└────────┬──────────┘
         │
    ┌────┴────────────────────────┐
    │ Passed?                     │
    ├──────────────┬──────────────┤
    │ YES          │ NO           │
    ▼              ▼              ▼
[Success]   Capture Traceback & Error Type
                   │
                   ▼
       Feed diagnostics to Coder
       (Self-Correction Loop, max N iterations)
```

---

## Features

* **Multi-Agent State Machine:** Clear separation of concerns between planning, coding, and validation.
* **Isolated Subprocess Execution Sandbox:** Runs generated code in separate Python processes with strict execution timeouts (preventing infinite loops and memory leaks).
* **Automatic Error Classification:** Differentiates `AssertionError`, `SyntaxError`, `TimeoutError`, and runtime exceptions for actionable feedback.
* **Self-Correction Feedback Loop:** Automatically prompts the coding agent with execution tracebacks until tests pass or the iteration budget is exhausted.
* **Benchmark Reporting:** Evaluates architectures over batches of tasks, measuring Pass@1, Pass@k, iteration efficiency, and execution latency.

---

## Project Structure

```
agent-eval-harness/
├── src/
│   └── agent_eval_harness/
│       ├── __init__.py        # Public module exports
│       ├── schemas.py         # Pydantic data schemas
│       ├── sandbox.py         # Subprocess runner with timeout enforcement
│       ├── orchestrator.py    # Multi-agent coordination loop
│       └── benchmark.py       # Benchmark suite and metrics aggregator
├── tests/
│   └── test_harness.py        # Sandbox and self-correction unit tests
├── demo.py                    # Benchmark run over sample algorithmic tasks
├── pyproject.toml
└── README.md
```

---

## Quickstart

### 1. Installation
```bash
git clone https://github.com/Antonymunene010/agent-eval-harness.git
cd agent-eval-harness

python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
```

### 2. Run the Benchmark Demo
```bash
python demo.py
```

### 3. Run Unit Tests
```bash
pytest tests/ -v
```

---

## Evaluation Metrics

The harness outputs standardized metrics for evaluating agent capabilities:
* **Pass Rate (%):** Percentage of tasks where all unit tests passed.
* **Average Iterations:** Mean number of code-eval-refine attempts per task.
* **Mean Latency (ms):** Average time spent per sandbox execution.
* **Error Distribution:** Breakdown of syntax errors vs logical assertion failures.

---

## Author
**Antony Munene** — [GitHub](https://github.com/Antonymunene010) • [LinkedIn](https://www.linkedin.com/in/antony-munene-ml/)
License: MIT
