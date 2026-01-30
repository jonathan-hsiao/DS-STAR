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

from ds_star import DSStar
from ds_star.pipeline.ds_star import DSStarConfig

# Path to data directory (relative to this script)
DATA_DIR = Path(__file__).resolve().parent / "data"


def main() -> None:
    config = DSStarConfig(
        llm_provider="gemini",
        llm_model="gemini-2.5-pro",
        llm_api_key=os.environ.get("GEMINI_API_KEY"),
        max_iterations=3,
    )
    agent = DSStar(config=config)

    question = "What is the total value of all products (quantity * price)?"
    code, output = agent.run_analysis(
        question=question,
        data_directory=str(DATA_DIR),
        guidelines="Print only the final numeric answer, no explanation.",
    )

    print("Question:", question)
    print("\nFinal code:\n")
    print(code)
    print("\nOutput:\n")
    print(output)


if __name__ == "__main__":
    main()
