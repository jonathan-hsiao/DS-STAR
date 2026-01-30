from src.ds_star.llm_providers.providers import BaseProvider
from src.ds_star.prompts.prompts import PROMPT__ANALYZER

class AnalyzerAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def analyze_data_file(self, data_file_name: str, data_directory: str) -> str:
        pass