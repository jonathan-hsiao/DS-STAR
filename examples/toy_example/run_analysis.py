"""
Runs DSStar pipeline on a toy example.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from ds_star import DSStar, DSStarConfig

# Load .env from project root (walk up from this file)
_root = Path(__file__).resolve().parent
for _ in range(5):
    _root = _root.parent
    if (_root / ".env").is_file():
        load_dotenv(_root / ".env")
        break

# Path to data directory (relative to this script)
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

def main() -> None:
    config = DSStarConfig(
        llm_provider="openai",                        # openai or gemini
        llm_model="gpt-5.2",
        llm_api_key=os.environ.get("OPENAI_API_KEY"), # OPENAI_API_KEY or GEMINI_API_KEY
        max_iterations = 5,
        max_debug_attempts = 3,
        execution_timeout_seconds = 600,
    )
    dsstar_pipeline = DSStar(config=config)

    question = (
        "What is the total value of all products after applying each product's discount?"
    )

    code, output = dsstar_pipeline.run_analysis(
        question=question,
        data_directory=str(DATA_DIR),
        output_directory=str(OUTPUT_DIR),
        guidelines="Print only the final numeric answer (total discounted value), no explanation.",
        reuse_data_summaries=False,
    )

    print("Question:", question)
    print("\nOutput:\n")
    print(output)

if __name__ == "__main__":
    main()
