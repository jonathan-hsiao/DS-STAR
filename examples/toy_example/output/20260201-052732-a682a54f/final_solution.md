# Final solution

**Run ID:** `20260201-052732-a682a54f`

## Question

What is the total value of all products after applying each product's discount?

## Plan

Step #1: Load `inventory.csv` and `discounts.csv` into dataframes and inner-join them on the `product` column to attach each product’s `discount_pct` to its `quantity` and `price`.

Step #2: Compute each product’s discounted total as `quantity * price * (1 - discount_pct/100)` in a new column, then sum that column to get the total value after discounts.

## Code

```python
import pandas as pd

inventory_df = pd.read_csv("data/inventory.csv")
discounts_df = pd.read_csv("data/discounts.csv")

merged_df = inventory_df.merge(discounts_df, on="product", how="inner")
merged_df["discounted_total"] = (
    merged_df["quantity"] * merged_df["price"] * (1 - merged_df["discount_pct"] / 100.0)
)

print(merged_df["discounted_total"].sum())
```

## Output

```
117.5

```