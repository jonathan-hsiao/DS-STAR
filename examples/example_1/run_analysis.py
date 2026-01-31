"""Example: run DS-Star to answer a question using data in examples/example_1/data/."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
def _load_env() -> None:
    root = Path(__file__).resolve()
    for _ in range(5):
        root = root.parent
        env_file = root / ".env"
        if env_file.is_file():
            load_dotenv(env_file)
            break

_load_env()

from ds_star import DSStar, DSStarConfig

# Path to data directory (relative to this script)
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

def main() -> None:
    config = DSStarConfig(
        # llm_provider="gemini",
        # llm_model="gemini-2.5-pro",
        # llm_api_key=os.environ.get("GEMINI_API_KEY"),
        llm_provider="openai",
        llm_model="gpt-5.2",
        llm_api_key=os.environ.get("OPENAI_API_KEY"),
        max_iterations = 5,
        max_debug_attempts = 3,
        execution_timeout_seconds = 600,
    )
    dsstar_pipeline = DSStar(config=config)

    question = "What is the total value of all products (quantity * price)?"

    code, output = dsstar_pipeline.run_analysis(
        question=question,
        data_directory=str(DATA_DIR),
        output_directory=str(OUTPUT_DIR),
        guidelines="Print only the final numeric answer, no explanation.",
    )

    print("Question:", question)
    print("\nFinal code:\n")
    print(code)
    print("\nOutput:\n")
    print(output)


if __name__ == "__main__":
    main()
