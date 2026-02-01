# Final solution

**Run ID:** `20260201-054512-d2ce5088`

## Question

For credit transactions, what would be the average fee that the card scheme GlobalCard would charge for a transaction value of 10 EUR?

## Plan

Step #1: Load `fees.json` into a dataframe and filter to rows where `card_scheme == "GlobalCard"` and `is_credit == true` to identify the applicable fee records for credit transactions.

Step #2: Compute the average GlobalCard credit fee for a 10 EUR transaction across the 123 filtered rows using `fee_eur = fixed_amount + (rate/10000)*10`, then take `fee_eur.mean()`.

## Code

```python
import json
import pandas as pd

# Load fees.json
with open("data/fees.json", "r", encoding="utf-8") as f:
    fees = json.load(f)

fees_df = pd.DataFrame(fees)

# Filter to GlobalCard + credit transactions
filtered = fees_df[(fees_df["card_scheme"] == "GlobalCard") & (fees_df["is_credit"] == True)].copy()

# Compute fee for a 10 EUR transaction: fixed_amount + (rate/10000)*amount
txn_amount_eur = 10.0
filtered["fixed_amount"] = pd.to_numeric(filtered["fixed_amount"], errors="coerce")
filtered["rate"] = pd.to_numeric(filtered["rate"], errors="coerce")
filtered["fee_eur"] = filtered["fixed_amount"] + (filtered["rate"] / 10000.0) * txn_amount_eur

avg_fee_eur = float(filtered["fee_eur"].mean())

print(f"{avg_fee_eur:.6f}")
```

## Output

```
0.117667

```