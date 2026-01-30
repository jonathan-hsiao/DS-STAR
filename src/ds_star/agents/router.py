from src.ds_star.llm_providers.providers import BaseProvider
from src.ds_star.prompts.prompts import (
    PROMPT__ROUTER,
)

class RouterAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def route(
        self, 
        plan: list[str],
        results: str,
        question: str,
        data_summaries: list[str],
    ) -> str:
        pass