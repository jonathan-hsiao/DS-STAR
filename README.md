# DS-Star

Implementation of Google's paper "DS-STAR: Data Science Agent via Iterative Planning and Verification" ([arXiv](https://arxiv.org/pdf/2509.21825)).

### TL;DR
Answers factoid questions over structured or unstructured data (CSV, JSON, Markdown, etc.) using an iterative process:
- Analyzer agent first summarizes data files.
- Five agents in a loop: Planner → Coder → execute code → Debugger → Verifier (exit loop on success) → Router.
- Finalizer agent produces final answer under specified guidelines.

## Install

```bash
poetry install
```

## Usage

### Directory layout

Generated code runs with **cwd = parent of your data folder**, so it expects files under `data/` and writes solution and logs to a sibling `output/` folder.

```
your_project/
├── data/          # All data files in this folder are analyzed
└── output/        # Outputs: final_solution, plan_log, data_summaries_log, metadata
```

### Minimal Python script

```python
from ds_star import DSStar, DSStarConfig

config = DSStarConfig(
    llm_provider="gemini",       # or "openai"
    llm_model="gemini-2.5-pro",
    llm_api_key="your-api-key",  # or set GEMINI_API_KEY / OPENAI_API_KEY env var
    max_iterations=5,
    max_debug_attempts=3,
    execution_timeout_seconds=600,
)
pipeline = DSStar(config=config)

code, output = pipeline.run_analysis(
    question="Your question about the data",
    data_directory="/path/to/data",
    output_directory="/path/to/output",
    guidelines="Optional format instructions for the final answer."
)
```

### Examples

- **`examples/toy_example/`** - small CSV data, single-question.
- **`examples/dabstep/`** - [DABstep](https://huggingface.co/datasets/adyen/DABstep) benchmark data; two easy + two hard tasks.