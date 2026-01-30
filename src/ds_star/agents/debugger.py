from ds_star.llm_providers.providers import BaseProvider
from ds_star.prompts.prompts import (
    PROMPT__DEBUGGER_SUMMARIZE,
    PROMPT__DEBUGGER_FIX_ANALYZER,
    PROMPT__DEBUGGER_FIX_SOLUTION,
)
from ds_star.pipeline.utils import (
    extract_code_from_llm_response,
    format_data_summaries_for_prompt,
)
from ds_star.models.models import DataSummary

class DebuggerAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def summarize_error(self, error: str) -> str:
        prompt = PROMPT__DEBUGGER_SUMMARIZE.format(error=error)
        response = self.llm_provider.generate_response(prompt)
        return response

    def debug_analyzer_code(self, error: str, original_code: str) -> str:
        summarized_error = self.summarize_error(error)
        prompt = PROMPT__DEBUGGER_FIX_ANALYZER.format(error=summarized_error, code=original_code)
        response = self.llm_provider.generate_response(prompt)
        return extract_code_from_llm_response(response)

    def debug_solution_code(self, error: str, original_code: str, data_summaries: list[DataSummary]) -> str:
        summarized_error = self.summarize_error(error)
        formatted_data_summaries = format_data_summaries_for_prompt(data_summaries)
        prompt = PROMPT__DEBUGGER_FIX_SOLUTION.format(
            error=summarized_error, 
            code=original_code,
            data_summaries=formatted_data_summaries,
        )
        response = self.llm_provider.generate_response(prompt)
        return extract_code_from_llm_response(response)