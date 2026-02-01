# Final solution

**Run ID:** `20260201-054430-d811bace`

## Question

What is the top country (ip_country) for fraud? A. NL, B. BE, C. ES, D. FR

## Plan

Step #1: Load `payments.csv` and compute the fraud rate by `ip_country` (e.g., group by `ip_country`, calculate `mean(has_fraudulent_dispute)`), then compare the rates for NL, BE, ES, and FR.

## Code

```python
import pandas as pd

# Load payments.csv
df = pd.read_csv("data/payments.csv")

# Ensure has_fraudulent_dispute is boolean
if df["has_fraudulent_dispute"].dtype == "object":
    df["has_fraudulent_dispute"] = df["has_fraudulent_dispute"].map(
        {"True": True, "False": False, True: True, False: False}
    )

# Options mapping
options = {"A": "NL", "B": "BE", "C": "ES", "D": "FR"}
countries = list(options.values())

# Compute fraud rate for the specified countries and find the top one
fraud_rates = df[df["ip_country"].isin(countries)].groupby("ip_country")["has_fraudulent_dispute"].mean()
top_country = fraud_rates.idxmax()

# Convert country code back to option letter
top_letter = next(k for k, v in options.items() if v == top_country)

print(f"{top_letter}. {top_country}")
```

## Output

```
B. BE

```