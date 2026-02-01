# Final solution

**Run ID:** `20260201-054049-586f44e2`

## Question

Which issuing country has the highest number of transactions?

## Plan

Step #1: Load `payments.csv` and compute a frequency count of the `issuing_country` column (e.g., `value_counts()`), then identify which country has the maximum count.

## Code

```python
import pandas as pd

df = pd.read_csv("data/payments.csv")
top_country = df["issuing_country"].value_counts(dropna=False).idxmax()
print(top_country)
```

## Output

```
NL

```