# DS-Star

Implementation of Google's DS-Star paper.

## Install

```bash
poetry install
# or: pip install -e .
```

## Usage

```python
from ds_star import DSStar, DSStarConfig

config = DSStarConfig(
    llm_provider="gemini",
    llm_model="gemini-2.5-pro",
    llm_api_key="your-api-key",  # or set GEMINI_API_KEY / OPENAI_API_KEY in the environment
    max_iterations = 5,
    max_debug_attempts = 3,
    execution_timeout_seconds = 600,
)
dsstar_pipeline = DSStar(config=config)

code, output = dsstar_pipeline.run_analysis(
    question="Your question about the data",
    data_directory="/path/to/data",
    output_directory="/path/to/outputs",
    guidelines="Optional instructions for the final output.",
)
```
