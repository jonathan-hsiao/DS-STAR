import re

from ds_star.llm_providers.providers import BaseProvider
from ds_star.prompts.prompts import (
    PROMPT__ROUTER,
)
from ds_star.models.models import DataSummary, RouterResponse
from ds_star.pipeline.utils import (
    format_data_summaries_for_prompt,
    format_plan_for_prompt,
)


class RouterAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def route(
        self,
        plan: list[str],
        results: str,
        question: str,
        data_summaries: list[DataSummary],
    ) -> RouterResponse:
        formatted_data_summaries = format_data_summaries_for_prompt(data_summaries)
        formatted_plan, _ = format_plan_for_prompt(plan)
        num_steps = len(plan)
        prompt = PROMPT__ROUTER.format(
            question=question,
            data_summaries=formatted_data_summaries,
            current_plan=formatted_plan,
            results=results,
            num_steps=num_steps,
        )
        response = self.llm_provider.generate_response(prompt)
        return self._parse_router_response(response.strip(), num_steps)

    def _parse_router_response(self, response: str, num_steps: int) -> RouterResponse:
        """Parse LLM output into ADD_STEP or remove_step with earliest valid step number."""
        if not response:
            return RouterResponse(decision="add_step") # default to add new step if no response

        if "add step" in response.lower():
            return RouterResponse(decision="add_step")

        # Find all "Step N" mentions (1-based); remove the earliest valid step
        matches = re.findall(r"step\s*(\d+)", response.lower())
        valid_steps = [int(m) for m in matches if 1 <= int(m) <= num_steps]
        if valid_steps:
            return RouterResponse(decision="remove_step", step_to_remove=min(valid_steps))

        return RouterResponse(decision="add_step") # default to add new step