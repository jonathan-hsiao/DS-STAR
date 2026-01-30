from src.ds_star.llm_providers.providers import BaseProvider
from src.ds_star.prompts.prompts import (
    PROMPT__VERIFIER,
)

class VerifierAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def verify_plan(self, plan: list[str], code: str, results: str, question: str) -> bool:
        pass