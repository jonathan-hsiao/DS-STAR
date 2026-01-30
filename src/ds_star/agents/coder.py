from ds_star.llm_providers.providers import BaseProvider
from ds_star.prompts.prompts import (
    PROMPT__CODER_INITIAL,
    PROMPT__CODER_ITERATE,
)
from ds_star.pipeline.utils import (
    format_data_summaries_for_prompt,
    format_plan_for_prompt,
    extract_code_from_llm_response,
)
from ds_star.models.models import DataSummary

class CoderAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def code_initial_plan(self, plan: list[str], data_summaries: list[DataSummary]) -> str:
        formatted_data_summaries = format_data_summaries_for_prompt(data_summaries)
        formatted_plan, _ = format_plan_for_prompt(plan)
        prompt = PROMPT__CODER_INITIAL.format(
            data_summaries=formatted_data_summaries,
            current_plan=formatted_plan,
        )
        response = self.llm_provider.generate_response(prompt)
        return extract_code_from_llm_response(response)

    def code_plan(self, plan: list[str], data_summaries: list[DataSummary], base_code: str) -> str:
        if len(plan) == 1:
            return self.code_initial_plan(plan, data_summaries)
            
        formatted_data_summaries = format_data_summaries_for_prompt(data_summaries)
        formatted_current_plan, formatted_latest_step = format_plan_for_prompt(
            plan=plan, 
            split_latest_step=True,
        )
        prompt = PROMPT__CODER_ITERATE.format(
            data_summaries=formatted_data_summaries,
            previous_plan_steps=formatted_current_plan,
            latest_plan_step=formatted_latest_step,
            base_code=base_code,
        )
        response = self.llm_provider.generate_response(prompt)
        return extract_code_from_llm_response(response)