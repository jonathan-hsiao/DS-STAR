from datetime import datetime, timezone
from pathlib import Path

from ds_star.models.models import DataSummary
from ds_star.pipeline.utils import format_plan_for_prompt


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
        self._run_metadata = self.output_dir / "run_metadata"

        # Start each run with a fresh plan_log
        self._plan_log.write_text("", encoding="utf-8")

        # Write run_metadata with start timestamp
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._run_metadata.write_text(
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

    def log_plan(self, plan: list[str], code: str, iteration: int) -> None:
        """Append plan and code to plan_log. iteration=0 for initial plan, else iteration number."""
        header = self._run_id_header if iteration == 0 else ""
        section = "Initial plan" if iteration == 0 else f"--- Iteration {iteration} ---"
        plan_str = "\n".join(f"Step {i+1}: {step}" for i, step in enumerate(plan))
        block = f"{header}{section}\n\nPlan:\n{plan_str}\n\nCode:\n{code}\n\n"
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
        """Update run_metadata with end timestamp."""
        ended_at = datetime.now(timezone.utc).isoformat()
        self._run_metadata.write_text(
            f"run_id: {self.run_id}\nstarted_at: {self._started_at}\nended_at: {ended_at}\n",
            encoding="utf-8",
        )
