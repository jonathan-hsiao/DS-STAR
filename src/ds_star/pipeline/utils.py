import re

from ds_star.models.models import DataSummary


def extract_code_from_llm_response(response: str) -> str:
    """Extract Python code from an LLM response that may contain markdown code blocks or raw code.

    Handles all DS-Star prompt formats: analyzer, coder (initial/iterate), debugger, finalizer.
    Supports ```python, ```py, or bare ``` fences; falls back to raw response if no block found.
    """
    if not response or not response.strip():
        return ""

    text = response.strip()

    # Match fenced code blocks: optional language (python/py), then content until closing ```
    # re.DOTALL so . matches newline; prefer Python-tagged blocks
    pattern = re.compile(
        r"```(?:python|py)?\s*\n(.*?)```",
        re.DOTALL | re.IGNORECASE,
    )
    matches = pattern.findall(text)

    if matches:
        # Prefer non-empty blocks; take first (prompts ask for "single code block")
        for block in matches:
            code = block.strip()
            if code:
                return code

    # No fenced block or all empty: treat entire response as code (e.g. raw LLM output)
    return text


def format_data_summaries_for_prompt(data_summaries: list[DataSummary]) -> str:
    """Format a list of DataSummary objects as a text string for use in a prompt.

    Each summary is formatted as:
    - Data file #N: <data_file_name>
    - Summary: <summary>
    """
    return "\n\n".join([
        f"Data file #{i+1}: {summary.data_file.name}\nSummary: {summary.summary}"
        for i, summary in enumerate(data_summaries)
    ])

def format_plan_for_prompt(plan: list[str], split_latest_step: bool = False) -> str:
    """Format a list of plan steps as a text string for use in a prompt.

    Each step is formatted as:
    - Step #N: <step>
    """
    if split_latest_step:
        current_plan = plan[:-1]
        latest_step = plan[-1]
    else:
        current_plan = plan
        latest_step = None

    current_plan_str = "\n\n".join([
        f"Step #{i+1}: {step}"
        for i, step in enumerate(current_plan)
    ])
    latest_step_str = f"Step #{len(plan)}: {latest_step}" if latest_step else None

    return current_plan_str, latest_step_str