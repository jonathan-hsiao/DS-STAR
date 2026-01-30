from pathlib import Path
from typing import Optional

from ds_star.llm_providers.providers import BaseProvider
from ds_star.prompts.prompts import PROMPT__ANALYZER
from ds_star.models.models import DataSummary
from ds_star.pipeline.utils import extract_code_from_llm_response
from ds_star.pipeline.code_runner import CodeRunner

class AnalyzerAgent:
    def __init__(self, llm_provider: BaseProvider, code_runner: CodeRunner):
        self.llm_provider = llm_provider
        self.code_runner = code_runner
        
    def analyze_data_file(self, data_file: Path, code: Optional[str] = None) -> DataSummary:
        # If no code is provided, generate it using the analyzer prompt
        if not code:
            prompt = PROMPT__ANALYZER.format(filename=data_file.name)
            response = self.llm_provider.generate_response(prompt)
            code = extract_code_from_llm_response(response)

        # Execute the analyzer code
        results = self.code_runner.run_code(code)
        
        if results.success:
            summary = results.output
            error = None
        else:
            summary = ""
            error = results.error

        return DataSummary(
            data_file=data_file,
            code=code,
            summary=summary,
            error=error,
        )