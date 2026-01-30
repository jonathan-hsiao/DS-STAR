from typing import Optional

from src.ds_star.llm_providers.providers import BaseProvider
from src.ds_star.prompts.prompts import (
    PROMPT__FINALIZER,
)

class FinalizerAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider

    def finalize_code(
            self,
            question: str,
            data_summaries: list[str],
            code: str,
            results: str,
            guidelines: Optional[str] = None,
        ) -> str:
        pass