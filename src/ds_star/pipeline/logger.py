import logging
from datetime import datetime, timezone
from pathlib import Path

from ds_star.models.models import DataSummary
from ds_star.pipeline.utils import format_plan_for_prompt


def _setup_console_logger() -> logging.Logger:
    """Return the package logger, configured for console output if it has no handlers."""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        h = logging.StreamHandler()
        h.setLevel(logging.INFO)
        h.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(h)
    return logger

_logger = _setup_console_logger()


class PipelineLogger:
    """Writes data summaries, plan/code iterations, and final solution to files under output_directory/run_id/."""

    def __init__(self, output_directory: str, run_id: str) -> None:
        self.run_id = run_id
        self._run_id_header = f"run_id: {run_id}\n\n"
        self.output_dir = Path(output_directory) / run_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._data_summaries_log = self.output_dir / "data_summaries_log"
        self._plan_log = self.output_dir / "plan_log"
        self._final_solution = self.output_dir / "final_solution"
        self._metadata = self.output_dir / "metadata"

        # Start each run with a fresh plan_log
        self._plan_log.write_text("", encoding="utf-8")

        # Write metadata with start timestamp
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._metadata.write_text(
            f"run_id: {run_id}\nstarted_at: {self._started_at}\nended_at:\n",
            encoding="utf-8",
        )

    def log_data_summaries(self, data_summaries: list[DataSummary]) -> None:
        """Write data summaries to data_summaries_log."""
        lines = [self._run_id_header]
        for i, s in enumerate(data_summaries, 1):
            lines.append(f"--- Data file #{i}: {s.data_file.name} ---")
            lines.append(f"Summary:\n{s.summary}")
            if s.code:
                lines.append(f"Code:\n{s.code}")
            lines.append("")
        self._data_summaries_log.write_text("\n".join(lines), encoding="utf-8")

    def log_plan(self, plan: list[str], code: str, results: str, iteration: int) -> None:
        """Append plan and code to plan_log. iteration=0 for initial plan, else iteration number."""
        header = self._run_id_header if iteration == 0 else ""
        section = "Initial plan" if iteration == 0 else f"--- Iteration {iteration} ---"
        plan_str, _ = format_plan_for_prompt(plan)
        block = f"{header}{section}\n\nPlan:\n{plan_str}\n\nCode:\n{code}\n\nResults:\n{results}\n\n"
        with self._plan_log.open("a", encoding="utf-8") as f:
            f.write(block)

    def log_final_solution(
        self,
        question: str,
        plan: list[str],
        code: str,
        output: str,
    ) -> None:
        """Write question, plan, final code, and output to final_solution."""
        plan_str, _ = format_plan_for_prompt(plan)
        content = (
            self._run_id_header
            + f"Question:\n{question}\n\n"
            + f"Plan:\n{plan_str}\n\n"
            + f"Code:\n{code}\n\n"
            + f"Output:\n{output}"
        )
        self._final_solution.write_text(content, encoding="utf-8")

    def log_run_end(self) -> None:
        """Update metadata with end timestamp."""
        ended_at = datetime.now(timezone.utc).isoformat()
        self._metadata.write_text(
            f"run_id: {self.run_id}\nstarted_at: {self._started_at}\nended_at: {ended_at}\n",
            encoding="utf-8",
        )

    def log_analyzer_failure(self, data_file_name: str, error: str, code: str) -> None:
        """Write analyzer failure (error + code) for a data file to the output directory."""
        # Sanitize filename for the log file name (e.g. payments-readme.md -> payments-readme_md)
        safe_name = data_file_name.replace(".", "_")
        path = self.output_dir / f"analyzer_failure_{safe_name}.txt"
        path.write_text(
            f"{self._run_id_header}Data file: {data_file_name}\n\nError:\n{error}\n\nCode:\n{code}",
            encoding="utf-8",
        )

    def log_solution_failure(self, error: str, code: str) -> None:
        """Write solution run failure (error + code) to the output directory."""
        path = self.output_dir / "solution_failure"
        path.write_text(
            f"{self._run_id_header}Error:\n{error}\n\nCode:\n{code}",
            encoding="utf-8",
        )

    def info(self, msg: str, *args, **kwargs) -> None:
        """Console logging wrapper; forwards to the standard logging logger."""
        _logger.info(msg, *args, **kwargs)