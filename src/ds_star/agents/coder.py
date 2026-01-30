from src.ds_star.llm_providers.providers import BaseProvider
from src.ds_star.prompts.prompts import (
    PROMPT__CODER_INITIAL,
    PROMPT__CODER_ITERATE,
)

class CoderAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def code_initial_plan(self, plan: list[str], data_summaries: list[str]) -> str:
        pass

    def code_plan(self, plan: list[str], data_summaries: list[str], base_code: str) -> str:
        pass