from src.ds_star.llm_providers.providers import BaseProvider
from src.ds_star.prompts.prompts import (
    PROMPT__PLANNER_INITIAL,
    PROMPT__PLANNER_ITERATE,
)

class PlannerAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def initialize_plan(self, question: str, data_summaries: list[str]) -> str:
        pass

    def update_plan(self, question: str, data_summaries: list[str], current_plan: list[str], results: str) -> list[str]:
        pass