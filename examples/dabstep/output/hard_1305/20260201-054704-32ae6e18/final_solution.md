# Final solution

**Run ID:** `20260201-054704-32ae6e18`

## Question

For account type H and the MCC description: Eating Places and Restaurants, what would be the average fee that the card scheme GlobalCard would charge for a transaction value of 10 EUR? Provide the answer in EUR and 6 decimals

## Plan

Step #1: Filter `fees.json` to the rows where `card_scheme == "GlobalCard"` and `account_type` contains `"H"`, then further narrow to those whose `merchant_category_code` list includes the MCC for “Eating Places and Restaurants” (i.e., 5812).

Step #2: For the 3 matching fee rules, compute each fee for a 10 EUR transaction as `fixed_amount + (rate / 10000) * 10`, then take the mean of these three fees.

## Code

```python
import json
from pathlib import Path

fees_path = Path("data/fees.json")

with fees_path.open("r", encoding="utf-8") as f:
    fees = json.load(f)

TARGET_SCHEME = "GlobalCard"
TARGET_ACCOUNT_TYPE = "H"
TARGET_MCC = 5812  # Eating Places and Restaurants
TX_EUR = 10.0

filtered = []
for row in fees:
    if row.get("card_scheme") != TARGET_SCHEME:
        continue

    account_types = row.get("account_type") or []
    if TARGET_ACCOUNT_TYPE not in account_types:
        continue

    mcc_list = row.get("merchant_category_code") or []
    if TARGET_MCC not in mcc_list:
        continue

    filtered.append(row)

fees_for_tx = []
for r in filtered:
    fixed_amount = float(r.get("fixed_amount") or 0.0)
    rate = float(r.get("rate") or 0.0)  # basis points
    fee = fixed_amount + (rate / 10000.0) * TX_EUR
    fees_for_tx.append(fee)

if fees_for_tx:
    mean_fee = sum(fees_for_tx) / len(fees_for_tx)
    print(f"{mean_fee:.6f}")
else:
    print("Not Applicable")
```

## Output

```
0.064000

```