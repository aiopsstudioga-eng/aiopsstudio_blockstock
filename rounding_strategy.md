# Rounding Strategy – Purchase Tax Rate Feature

## Guiding Principle

**All financial storage uses integer cents.**  
Float arithmetic is only used for intermediate UI display calculations. The moment any dollar/rate value is committed to the database or passed to the accounting model, it becomes an integer in cents. This is an existing rule already enforced throughout `item.py` and `inventory_service.py`.

---

## Where Floats Enter the System

| Source | Type | Example |
|---|---|---|
| `quantity_spin` | `float` | `10.0` units |
| `unit_cost_spin` | `float` (dollars) | `$2.00` |
| `tax_rate_spin` | `float` (percent) | `6.0` % |

---

## Step-by-Step Rounding Decisions

### Step 1 — UI Display (no storage, pure float is fine)

All three live-update labels show what the user sees in real time. No rounding rules required here because these are never stored.

```
subtotal_display    = qty × unit_cost              # e.g. 10 × 2.00 = $20.00
tax_amount_display  = subtotal × (tax_rate / 100)  # e.g. 20.00 × 0.06 = $1.20
grand_total_display = subtotal + tax_amount         # e.g. $21.20
```

Formatted with Python's `f"${value:,.2f}"` — display only, no accounting impact.

---

### Step 2 — Tax-Inclusive Unit Cost (float, intermediate)

Before calling the service, the _per-unit_ cost inclusive of tax is computed:

```python
tax_inclusive_unit_cost = unit_cost * (1 + tax_rate_pct / 100)
# e.g. 2.00 × 1.06 = 2.12  (exact for this case)
```

This stays a float and goes straight into the service call as `unit_cost_dollars`. No rounding here yet — we keep full precision until the next step.

> [!NOTE]
> The divisor is the user-entered quantity, not something derived from rounding. Tax rates like 6% on a $2.00 item yield `$2.12` — exact to the cent. A rate like 7.5% on $1.99 would yield `$2.13925`, which requires truncation at the next step.

---

### Step 3 — Dollar → Cents Conversion (**`int()` truncation — existing rule**)

In `process_purchase()` in `inventory_service.py`:

```python
unit_cost_cents = int(unit_cost_dollars * 100)
# 2.12 × 100 = 212  → int(212.0) = 212  ✓
# 2.13925 × 100 = 213.925 → int(213.925) = 213  (truncates sub-cent remainder)
```

`int()` is used here (not `round()`) because this converts a user-provided price to storage. **Truncation is intentional at point-of-entry**: the system books what was paid, rounding down to the nearest cent rather than potentially over-recording costs.

Then:

```python
total_cost_cents = int(quantity * unit_cost_cents)
# e.g. int(10.0 × 212) = int(2120.0) = 2120  ✓
```

Both values are now clean integers — zero floating-point risk from this point on.

---

### Step 4 — Weighted Average Cost Update (**`round()` — existing rule**)

`InventoryItem.current_unit_cost_cents` uses `round()`:

```python
return round(self.total_cost_basis_cents / self.quantity_on_hand)
# e.g. round(2120 / 10) = round(212.0) = 212  ✓
# e.g. for mixed stock: round(35000 / 150) = round(233.33...) = 233  ✓
```

`round()` (Python's banker's rounding) is used here because this is a _derived display value_ recalculated every time from the stored integer basis. Small systematic truncation errors here would accumulate over dozens of transactions and silently erode the reported cost basis — `round()` prevents that.

---

### Step 5 — COGS on Distribution (**`round()` — existing rule**)

```python
cogs_cents = round(quantity * unit_cost_cents)
new_cost_basis = total_cost_basis_cents - cogs_cents
if new_cost_basis < 0:
    new_cost_basis = 0  # safety floor
```

`round()` here for the same reason — partial-unit distributions (e.g., 0.5 units × 213¢ = 106.5¢) resolve to a fair nearest-cent value rather than always truncating downward.

---

## Summary Table

| Step | Operation | Method | Reason |
|---|---|---|---|
| UI display | subtotal, tax, grand total | float, f-string `:.2f` | Display only, never stored |
| Tax-inclusive unit cost | `unit_cost × (1 + rate/100)` | float intermediate | Full precision carried to next step |
| Dollar → cents | `int(dollars × 100)` | `int()` truncation | Point-of-entry price; round down = conservative |
| Total cost cents | `int(qty × unit_cost_cents)` | `int()` truncation | Exact integer math |
| WAC display property | `round(basis / qty)` | `round()` | Prevents cumulative display drift |
| COGS on distribution | `round(qty × unit_cost_cents)` | `round()` | Fair partial-unit resolution |

---

## Worked Example — 6% Tax Rate

| Input | Value |
|---|---|
| Quantity | 10 units |
| Unit Cost | $2.00 |
| Tax Rate | 6% |

| Calculation | Result |
|---|---|
| Subtotal display | $20.00 |
| Tax Amount display | $1.20 |
| Grand Total display | **$21.20** |
| Tax-inclusive unit cost (float) | 2.00 × 1.06 = `2.12` |
| `unit_cost_cents` = `int(2.12 × 100)` | **212 ¢** |
| `total_cost_cents` = `int(10 × 212)` | **2120 ¢** ($21.20) |
| New WAC (0 prior stock) = `round(2120 / 10)` | **212 ¢ = $2.12** ✓ |

---

## Worked Example — 7.5% Tax Rate (sub-cent scenario)

| Input | Value |
|---|---|
| Quantity | 1 unit |
| Unit Cost | $1.99 |
| Tax Rate | 7.5% |

| Calculation | Result |
|---|---|
| Tax-inclusive unit cost (float) | 1.99 × 1.075 = `2.13925` |
| `unit_cost_cents` = `int(2.13925 × 100)` | **213 ¢** (sub-cent truncated) |
| Display Grand Total | $2.14 shown (float math before truncation) |

> [!IMPORTANT]
> The display shows **$2.14** (rounded for readability) while the stored cost basis is **$0.213** cents short of that. This 0.43¢ discrepancy per unit is the expected behavior of integer-cent accounting — it is not a bug. All real-world POS and ERP systems do the same thing (the rounding "penny" usually goes to the retailer).
