from typing import Optional

from ds_star.llm_providers.providers import BaseProvider
from ds_star.prompts.prompts import (
    PROMPT__FINALIZER,
)
from ds_star.pipeline.utils import (
    format_data_summaries_for_prompt,
    extract_code_from_llm_response,
)
from ds_star.models.models import DataSummary

class FinalizerAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def finalize_solution_code(
            self,
            question: str,
            data_summaries: list[DataSummary],
            code: str,
            results: str,
            guidelines: Optional[str] = None,
        ) -> str:
        formatted_data_summaries = format_data_summaries_for_prompt(data_summaries)
        prompt = PROMPT__FINALIZER.format(
            data_summaries=formatted_data_summaries,
            code=code,
            results=results,
            question=question,
            guidelines=guidelines or "No additional guidelines",
        )
        response = self.llm_provider.generate_response(prompt)
        return extract_code_from_llm_response(response)