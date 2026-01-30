from src.ds_star.llm_providers.providers import BaseProvider
from src.ds_star.prompts.prompts import (
    PROMPT__DEBUGGER_SUMMARIZE,
    PROMPT__DEBUGGER_FIX_ANALYZER,
    PROMPT__DEBUGGER_FIX_SOLUTION,
)

class DebuggerAgent:
    def __init__(self, llm_provider: BaseProvider):
        self.llm_provider = llm_provider