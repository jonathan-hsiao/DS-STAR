# DS-Star

Implementation of Google's DS-Star paper.

## Install

```bash
poetry install
# or: pip install -e .
```

## Usage

```python
from ds_star import DSStar
from ds_star.pipeline.ds_star import DSStarConfig

config = DSStarConfig(
    llm_provider="gemini",
    llm_model="gemini-2.5-pro",
    llm_api_key="your-api-key",  # or set GEMINI_API_KEY / OPENAI_API_KEY in the environment
)
ds_star_pipeline = DSStar(config=config)

code, output = ds_star_pipeline.run_analysis(
    question="Your question about the data",
    data_directory="/path/to/data",
    guidelines="Optional instructions for the final output.",
)
```
