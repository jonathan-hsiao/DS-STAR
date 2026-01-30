from typing import Optional
from dataclasses import dataclass

from src.ds_star.agents import (
    AnalyzerAgent,
    CoderAgent,
    DebuggerAgent,
    FinalizerAgent,
    PlannerAgent,
    RouterAgent,
    VerifierAgent,
)
from src.ds_star.llm_providers.providers import (
    BaseProvider,
    GeminiProvider,
    OpenAIProvider,
)
from src.ds_star.pipeline.code_runner import CodeRunner


@dataclass
class DSStarConfig:
    """Config for DS-Star pipeline."""
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-pro"
    llm_api_key: Optional[str] = None
    max_iterations: int = 5


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
        self.agents = self._initialize_agents()
        self.code_runner = CodeRunner()

    def _initialize_llm_provider(self) -> BaseProvider:
        if self.config.llm_provider == "gemini":
            return GeminiProvider(model=self.config.llm_model, api_key=self.config.llm_api_key)
        elif self.config.llm_provider == "openai":
            return OpenAIProvider(model=self.config.llm_model, api_key=self.config.llm_api_key)
        else:
            raise ValueError(f"Invalid provider: {self.config.llm_provider}")
        
    def _initialize_agents(self) -> DSStarAgents:
        return DSStarAgents(
            analyzer=AnalyzerAgent(self.llm_provider),
            coder=CoderAgent(self.llm_provider),
            debugger=DebuggerAgent(self.llm_provider),
            finalizer=FinalizerAgent(self.llm_provider),
            planner=PlannerAgent(self.llm_provider),
            router=RouterAgent(self.llm_provider),
            verifier=VerifierAgent(self.llm_provider),
        )

    def _analyze_data_files(self, data_directory: str) -> str:
        data_file_names = find_data_files(data_directory)
        data_summaries = []
        for data_file_name in data_file_names:
            data_summary = self.agents.analyzer_agent.analyze_data_file(data_file_name, data_directory)
            # TODO if error call debugger agent to debug the data file

            data_summaries.append(data_summary)
        return data_summaries

    def _run_code(self, code: str) -> str:
        results = self.code_runner.run_code(code)
        # TODO if error call debugger agent to debug the code
        return results

    def _remove_plan_steps(self, plan: list[str], router_response: str) -> list[str]:
        # TODO implement remove steps if specified in router response
        return plan

    def run_analysis(
            self,
            question: str,
            data_directory: str,
            guidelines: Optional[str] = None,
        ) -> str:

        # Analyze the data files
        data_summaries = self._analyze_data_files(data_directory)

        # Generate the initial plan
        plan = []
        plan.append(self.agents.planner.initialize_plan(question, data_summaries))

        # Code the initial plan
        code = self.agents.coder.code_initial_plan(plan, data_summaries)

        # Execute the initial plan
        results = self._run_code(code)

        # Refinement loop
        for i in range(self.config.max_iterations):

            # Verify current plan, code, and results
            is_verified = self.agents.verifier.verify_plan(plan, code, results, question)
            if is_verified:
                break

            # Route
            router_response = self.agents.router.route(plan, results, question, data_summaries)
            plan = self._remove_plan_steps(plan, router_response)

            # Update the plan
            plan = self.agents.planner.update_plan(question, data_summaries, plan, results)

            # Code the updated plan
            code = self.agents.coder.code_plan(plan, data_summaries, code)

            # Execute the updated plan
            results = self._run_code(code)

        # Finalize solution code
        code = self.agents.finalizer.finalize_code(
            question, data_summaries, code, results, guidelines
        )

        # Execute the finalized code
        results = self._run_code(code)

        return code, results
