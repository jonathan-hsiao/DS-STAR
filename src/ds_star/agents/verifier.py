from ds_star.llm_providers.providers import BaseProvider
from ds_star.prompts.prompts import (
    PROMPT__VERIFIER,
)
from ds_star.pipeline.utils import format_plan_for_prompt

class VerifierAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def verify_plan(self, plan: list[str], code: str, results: str, question: str) -> bool:
        formatted_plan, _ = format_plan_for_prompt(plan)
        prompt = PROMPT__VERIFIER.format(
            current_plan=formatted_plan,
            code=code,
            results=results,
            question=question,
        )
        response = self.llm_provider.generate_response(prompt)
        return self._parse_verifier_response(response.strip())

    def _parse_verifier_response(self, response: str) -> bool:
        if "yes" in response.lower() and "no" not in response.lower():
            return True
        elif "no" in response.lower() and "yes" not in response.lower():
            return False
        else:
            return False # default to False if unclear