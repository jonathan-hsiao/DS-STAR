from ds_star.llm_providers.providers import BaseProvider
from ds_star.prompts.prompts import (
    PROMPT__PLANNER_INITIAL,
    PROMPT__PLANNER_ITERATE,
)
from ds_star.models.models import DataSummary
from ds_star.pipeline.utils import (
    format_data_summaries_for_prompt, 
    format_plan_for_prompt,
)

class PlannerAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def initialize_plan(
            self,
            question: str,
            data_summaries: list[DataSummary],
        ) -> list[str]:
        formatted_data_summaries = format_data_summaries_for_prompt(data_summaries)
        prompt = PROMPT__PLANNER_INITIAL.format(
            question=question, 
            data_summaries=formatted_data_summaries
        )
        response = self.llm_provider.generate_response(prompt)
        return [response]

    def update_plan(
            self,
            question: str,
            data_summaries: list[DataSummary],
            current_plan: list[str],
            results: str,
        ) -> list[str]:

        # If the plan is empty, initialize a new plan
        if len(current_plan) == 0:
            return self.initialize_plan(question=question, data_summaries=data_summaries)

        formatted_data_summaries = format_data_summaries_for_prompt(data_summaries)
        formatted_current_plan, _ = format_plan_for_prompt(current_plan)
        prompt = PROMPT__PLANNER_ITERATE.format(
            question=question,
            data_summaries=formatted_data_summaries,
            current_plan=formatted_current_plan,
            results=results,
        )
        response = self.llm_provider.generate_response(prompt)
        current_plan.append(response)
        return current_plan