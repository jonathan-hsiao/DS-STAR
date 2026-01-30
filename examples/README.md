# Examples

Instructions for running the examples locally in a virtual environment.

## 1. Create and activate a virtual environment

From the DS-Star project root (the folder containing `pyproject.toml`):

```bash
poetry install
poetry shell
```

Poetry creates and uses a venv automatically. (Without Poetry: `python -m venv .venv` then `source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\activate` on Windows.)

## 2. Install the project

If you didn’t use Poetry in step 1:

```bash
pip install -e .
```

Optional data-analysis extras (matplotlib, seaborn, scipy, plotly, scikit-learn):

```bash
poetry install --with data-analysis
```

## 3. Add your API key

Set up a `.env` file in the project root and add your key (`.env` is gitignored):

```bash
cat > .env << 'EOF'
GEMINI_API_KEY=your-gemini-api-key
EOF
```

Replace `your-gemini-api-key` with your actual key (or edit `.env` after).

## 4. Run an example

From the project root:

```bash
python examples/example_1/run_analysis.py
```

Without activating the shell: `poetry run python examples/example_1/run_analysis.py`

---

### Example 1: Answer a question from data

Uses DS-Star on `data/sales.csv` to answer: *What is the total value of all products (quantity × price)?* See `example_1/` for the script and data.
