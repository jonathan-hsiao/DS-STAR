"""
Downloads DABstep context files from adyen/DABstep (Hugging Face) into dabstep/data/.
"""
from pathlib import Path
from huggingface_hub import hf_hub_download
import datasets

REPO_ID = "adyen/DABstep"
CONTEXT_FILES = [
    "acquirer_countries.csv",
    "fees.json",
    # "manual.md",
    "merchant_category_codes.csv",
    "merchant_data.json",
    # "payments-readme.md",
    "payments.csv",
]
DATA_DIR = Path(__file__).resolve().parent / "data"
TASKS_DIR = Path(__file__).resolve().parent / "tasks"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename in CONTEXT_FILES:
        path = hf_hub_download(
            repo_id=REPO_ID,
            filename=f"data/context/{filename}",
            repo_type="dataset",
        )
        dest = DATA_DIR / filename
        dest.write_bytes(Path(path).read_bytes())
        print(f"Downloaded {filename} -> {dest}")
    print(f"Done. {len(CONTEXT_FILES)} files in {DATA_DIR}")

    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    dev_task_dataset = datasets.load_dataset("adyen/DABstep", name="tasks", split="dev")
    tasks_df = dev_task_dataset.to_pandas()
    tasks_df.to_csv(TASKS_DIR / "tasks.csv", index=False)
    print(f"Done. {len(tasks_df)} tasks in {TASKS_DIR}")


if __name__ == "__main__":
    main()
