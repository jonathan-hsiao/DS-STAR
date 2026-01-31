import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

from ds_star.agents import (
    AnalyzerAgent,
    CoderAgent,
    DebuggerAgent,
    FinalizerAgent,
    PlannerAgent,
    RouterAgent,
    VerifierAgent,
)
from ds_star.llm_providers.providers import (
    BaseProvider,
    GeminiProvider,
    OpenAIProvider,
)
from ds_star.pipeline.code_runner import CodeRunner
from ds_star.pipeline.logger import PipelineLogger
from ds_star.models.models import (
    DataSummary, 
    CodeRunnerResults, 
    RouterResponse,
    PlanCodeHistory,
)


@dataclass
class DSStarConfig:
    """Config for DS-Star pipeline."""
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-pro"
    llm_api_key: Optional[str] = None
    max_iterations: int = 5
    max_debug_attempts: int = 3
    execution_timeout_seconds: int = 600


@dataclass
class DSStarAgents:
    analyzer: AnalyzerAgent
    coder: CoderAgent
    debugger: DebuggerAgent
    finalizer: FinalizerAgent
    planner: PlannerAgent
    router: RouterAgent
    verifier: VerifierAgent


class DSStar:
    def __init__(self, config: DSStarConfig):
        self.config = config
        self.llm_provider = self._initialize_llm_provider()
        self.code_runner = CodeRunner(timeout_seconds=self.config.execution_timeout_seconds)
        self.agents = self._initialize_agents()
        self.plan_code_history = PlanCodeHistory(plan_steps=[], cumulative_code=[])

    def _initialize_llm_provider(self) -> BaseProvider:
        if self.config.llm_provider == "gemini":
            return GeminiProvider(model=self.config.llm_model, api_key=self.config.llm_api_key)
        elif self.config.llm_provider == "openai":
            return OpenAIProvider(model=self.config.llm_model, api_key=self.config.llm_api_key)
        else:
            raise ValueError(f"Invalid provider: {self.config.llm_provider}")
        
    def _initialize_agents(self) -> DSStarAgents:
        return DSStarAgents(
            analyzer=AnalyzerAgent(llm_provider=self.llm_provider, code_runner=self.code_runner),
            coder=CoderAgent(self.llm_provider),
            debugger=DebuggerAgent(self.llm_provider),
            finalizer=FinalizerAgent(self.llm_provider),
            planner=PlannerAgent(self.llm_provider),
            router=RouterAgent(self.llm_provider),
            verifier=VerifierAgent(self.llm_provider),
        )

    def _generate_run_id(self) -> str:
        # hybrid run_id: timestamp (sortable) + short random (unique)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        suffix = uuid.uuid4().hex[:8]
        return f"{ts}-{suffix}"

    def _analyze_data_files(self, data_directory: str) -> list[DataSummary]:
        # Find data files in the data directory
        data_path = Path(data_directory)
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory does not exist: {data_directory}")
        if not data_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {data_directory}")
        try:
            data_files = [
                p for p in data_path.iterdir()
                if p.is_file()
            ]
        except PermissionError as e:
            raise PermissionError(f"Cannot read data directory: {data_directory}") from e

        # Analyze each data file with debug loop
        data_summaries = []
        for data_file in data_files:
            data_summary = self.agents.analyzer.analyze_data_file(data_file)
            if data_summary.error:
                for i in range(self.config.max_debug_attempts):
                    updated_analyzer_code = self.agents.debugger.debug_analyzer_code(
                        error=data_summary.error,
                        original_code=data_summary.code,
                    )
                    data_summary = self.agents.analyzer.analyze_data_file(
                        data_file=data_file,
                        code=updated_analyzer_code,
                    )
                    if not data_summary.error:
                        break
                if data_summary.error:
                    raise ValueError(f"Failed to analyze data file: {data_file.resolve()} {data_summary.error}")
            data_summaries.append(data_summary)

        return data_summaries

    def _run_solution_code(self, code: str, data_summaries: list[DataSummary]) -> CodeRunnerResults:
        # Uses run cwd set at start of run_analysis (thread-safe via contextvar)
        results = self.code_runner.run_code(code)
        if results.error:
            for i in range(self.config.max_debug_attempts):
                updated_code = self.agents.debugger.debug_solution_code(
                    error=results.error,
                    original_code=code,
                    data_summaries=data_summaries,
                )
                results = self.code_runner.run_code(updated_code)
                if not results.error:
                    break
            if results.error:
                raise ValueError(f"Failed to run solution code: {code} {results.error}")
        return results

    def _remove_plan_steps(self, plan: list[str], code: str, router_response: RouterResponse) -> tuple[list[str], str]:
        """Apply router remove_step decision; return (updated_plan, updated_code)."""
        # No changes if router response does not specify removing a step
        if router_response.decision != "remove_step" or router_response.step_to_remove is None:
            return plan, code

        # If removing the first step, reset the entire plan and code
        if router_response.step_to_remove == 1:
            self.plan_code_history.plan_steps = []
            self.plan_code_history.cumulative_code = []
            return [], ""

        # step_to_remove is 1-based; convert to 0-based index
        idx = router_response.step_to_remove - 1
        # Invalid index to remove, do nothing
        if idx < 0 or idx >= len(plan):
            return plan, code
        # Remove the step and everything after it, reset plan and code to the previous step
        code_history = self.plan_code_history.cumulative_code
        rewinded_plan = plan[:idx]
        rewinded_code_history = code_history[:idx]
        self.plan_code_history.plan_steps = rewinded_plan
        self.plan_code_history.cumulative_code = rewinded_code_history
        return rewinded_plan, rewinded_code_history[-1]

    def run_analysis(
            self,
            question: str,
            data_directory: str,
            output_directory: str,
            guidelines: Optional[str] = None,
        ) -> tuple[str, str]:

        # Generate run ID and initialize logger
        run_id = self._generate_run_id()
        logger = PipelineLogger(output_directory=output_directory, run_id=run_id)

        # Set cwd so generated code can use "data/<file>"; run_code uses this when cwd is not passed.
        self.code_runner.cwd = Path(data_directory).parent
        logger.info("Starting run_id=%s with cwd=%s", run_id, self.code_runner.cwd)

        # Analyze the data files
        data_summaries = self._analyze_data_files(data_directory)
        logger.log_data_summaries(data_summaries)
        logger.info("Created data summaries for %d file(s).", len(data_summaries))

        # Generate the initial plan
        plan = self.agents.planner.initialize_plan(question=question, data_summaries=data_summaries)
        self.plan_code_history.plan_steps = plan

        # Code the initial plan
        code = self.agents.coder.code_initial_plan(plan=plan, data_summaries=data_summaries)
        self.plan_code_history.cumulative_code.append(code)

        # Execute the initial plan (with debug loop)
        results = self._run_solution_code(code=code, data_summaries=data_summaries)
        code = results.code
        self.plan_code_history.cumulative_code[-1] = code
        logger.log_plan(plan=plan, code=code, iteration=0)
        logger.info("Created initial plan and code with successful execution.")

        # Refinement loop
        for i in range(self.config.max_iterations):
            logger.info("Starting refinement iteration %d.", i + 1)

            # Verify current plan, code, and results
            is_verified = self.agents.verifier.verify_plan(
                plan=plan,
                code=code,
                results=results.output,
                question=question,
            )
            if is_verified:
                logger.info("Plan and code verified successfully.")
                break

            # Route (add step or remove steps)
            router_response = self.agents.router.route(
                plan=plan,
                results=results.output,
                question=question,
                data_summaries=data_summaries,
            )
            plan, code = self._remove_plan_steps(plan=plan, code=code, router_response=router_response)

            # Update the plan with next step
            plan = self.agents.planner.update_plan(
                question=question,
                data_summaries=data_summaries,
                current_plan=plan,
                results=results.output,
            )
            self.plan_code_history.plan_steps = plan

            # Code the updated plan with next step
            code = self.agents.coder.code_plan(plan=plan, data_summaries=data_summaries, base_code=code)
            self.plan_code_history.cumulative_code.append(code)

            # Execute the updated plan (with debug loop)
            results = self._run_solution_code(code=code, data_summaries=data_summaries)
            code = results.code
            self.plan_code_history.cumulative_code[-1] = code
            logger.log_plan(plan=plan, code=code, iteration=i+1)
            logger.info("Updated plan and code with successful execution (iteration %d).", i + 1)

        # Finalize solution code
        final_solution_code = self.agents.finalizer.finalize_solution_code(
            question=question,
            data_summaries=data_summaries,
            code=code,
            results=results.output,
            guidelines=guidelines,
        )

        # Execute the finalized code (with debug loop)
        final_solution_result = self._run_solution_code(
            code=final_solution_code, data_summaries=data_summaries
        )
        final_solution_code = final_solution_result.code
        logger.info("Finalized solution code with successful execution.")

        # Log final solution
        logger.log_final_solution(
            question=question,
            plan=plan,
            code=final_solution_code,
            output=final_solution_result.output,
        )

        logger.log_run_end()
        logger.info("Completed run_id=%s.", run_id)
        return final_solution_code, final_solution_result.output
