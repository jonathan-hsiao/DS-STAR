"""
Runs DSStar pipeline on DABstep dev tasks dataset (two easy and two hard tasks).
Run the get_dabstep_data.py script first to download the data and tasks for analysis.
"""
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from ds_star import DSStar, DSStarConfig

# Load .env from project root (walk up from this file)
_root = Path(__file__).resolve().parent
for _ in range(5):
    _root = _root.parent
    if (_root / ".env").is_file():
        load_dotenv(_root / ".env")
        break

# Paths (relative to this script)
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
OUTPUT_DIR = SCRIPT_DIR / "output"
TASKS_PATH = SCRIPT_DIR / "tasks" / "tasks.csv"


def load_tasks() -> pd.DataFrame:
    # Load DABstep dev tasks dataset
    df = pd.read_csv(TASKS_PATH)
    df = df[df["answer"] != "Not Applicable"].reset_index(drop=True)
    return df


def main() -> None:
    # Load two easy and two hard tasks from DABstep dev tasks dataset
    tasks = load_tasks()
    easy_tasks = tasks[tasks["level"] == "easy"].iloc[:2]
    hard_tasks = tasks[tasks["level"] == "hard"].iloc[:2]

    # configure and initialize DSStar pipeline
    config = DSStarConfig(
        llm_provider="openai",                        # openai or gemini
        llm_model="gpt-5.2",
        llm_api_key=os.environ.get("OPENAI_API_KEY"), # OPENAI_API_KEY or GEMINI_API_KEY
        max_iterations = 8,
        max_debug_attempts = 3,
        execution_timeout_seconds = 600,
    )
    dsstar_pipeline = DSStar(config=config)

    # run DSStar pipeline on two easy and two hard tasks
    for label, subset in [("easy", easy_tasks), ("hard", hard_tasks)]:
        for _, row in subset.iterrows():
            question = row["question"]
            guidelines = row["guidelines"]
            run_output_dir = OUTPUT_DIR / f"{label}_{int(row['task_id'])}"
            run_output_dir.mkdir(parents=True, exist_ok=True)

            print(f"--- {label.upper()} task_id={row['task_id']} ---")
            print("Question:", question)
            code, output = dsstar_pipeline.run_analysis(
                question=question,
                data_directory=str(DATA_DIR),
                output_directory=str(run_output_dir),
                guidelines=guidelines,
                reuse_data_summaries=True,
            )
            print("Output:", output)
            print()


if __name__ == "__main__":
    main()
