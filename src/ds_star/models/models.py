from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class DataSummary:
    data_file: Path
    code: str
    summary: str
    error: Optional[str] = None

@dataclass
class CodeRunnerResults:
    code: str
    output: str
    error: Optional[str] = None
    success: bool = True
    timeout_exceeded: bool = False
    exit_code: Optional[int] = None

@dataclass
class RouterResponse:
    decision: str
    step_to_remove: Optional[int] = None

@dataclass
class AnalysisHistory:
    plan_steps: list[str]
    cumulative_code: list[str]
    cumulative_results: list[CodeRunnerResults]