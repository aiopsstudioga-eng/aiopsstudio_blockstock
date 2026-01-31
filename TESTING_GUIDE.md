# Reporting Features Testing Guide

## Test Setup ✅

Sample data has been created with:
- **5 inventory items** (Beans, Rice, Pasta, Soup, Cereal)
- **4 purchase transactions** (initial stock + restock)
- **3 donation transactions** (from church, community center, grocery store)
- **9 distribution transactions**:
  - 6 client distributions
  - 1 spoilage (damaged cans)
  - 2 internal use (training samples)

## Testing Steps

### 1. Navigate to Reports Page

1. Launch application: `python src/main.py` ✅ (Running)
2. Click **"📈 Reports"** in the sidebar
3. You should see three report cards:
   - 💰 Financial Report (Blue)
   - 🎁 Impact Report (Green)
   - 📊 Stock Status (Orange)

### 2. Test Financial Report (COGS)

**Purpose:** Track real money spent on distributed items

**Steps:**
1. Leave date range as default (last month)
2. Click **"Generate"** on the blue Financial Report card
3. Confirm dialog should show:
   - Total COGS: ~$150-200 (varies by weighted average)
   - Distributions: 9 total
4. Click **"Yes"** to open the PDF
5. **Verify PDF contains:**
   - Summary table with:
     - Client Distributions
     - Spoilage/Waste
     - Internal Use
     - Total COGS
   - Detailed transaction list with dates, items, quantities, costs

**Expected Results:**
- ✅ PDF opens in Preview (macOS) or default PDF viewer
- ✅ Professional formatting with blue headers
- ✅ All 9 distributions listed
- ✅ COGS calculated using weighted average cost
- ✅ File saved to `reports/financial_report_YYYY-MM-DD.pdf`

### 3. Test Impact Report (FMV)

**Purpose:** Show value of donations for donor newsletters

**Steps:**
1. Click **"Generate"** on the green Impact Report card
2. Confirm dialog should show:
   - Total Donations (FMV): $290.00
     - 50 Beans @ $2.00 = $100
     - 100 Soup @ $1.50 = $150
     - 40 Cereal @ $3.50 = $140
   - Donations: 3
3. Click **"Yes"** to open the Excel file
4. **Verify Excel contains:**
   - **Summary sheet:**
     - Total Donations Received (FMV)
     - Total Value Distributed to Clients
     - Number of Donations
     - Number of Client Distributions
   - **Donations sheet:**
     - Date, Item, SKU, Quantity, Fair Market Value, Donor

**Expected Results:**
- ✅ Excel opens in Excel/Numbers
- ✅ Two sheets: Summary and Donations
- ✅ All 3 donations listed with donor names
- ✅ FMV totals correct
- ✅ File saved to `reports/impact_report_YYYY-MM-DD.xlsx`

### 4. Test Stock Status Report

**Purpose:** Identify items needing reorder

**Steps:**
1. Click **"Generate"** on the orange Stock Status card
2. Confirm dialog should show:
   - Total Items: 5
   - Total Value: varies
   - Low stock warnings (if any items below threshold)
3. Click **"Yes"** to open the PDF
4. **Verify PDF contains:**
   - Summary statistics
   - Items requiring attention (if any below threshold)
   - Status indicators (OUT OF STOCK, LOW)

**Expected Results:**
- ✅ PDF opens with stock status
- ✅ Orange/red color scheme for alerts
- ✅ All 5 items accounted for
- ✅ Low stock items highlighted
- ✅ File saved to `reports/stock_status_YYYY-MM-DD.pdf`

### 5. Test Transaction History Export

**Purpose:** Complete audit trail export

**Steps:**
1. Click **"Export to Excel"** button at bottom of Reports page
2. Confirm dialog should show:
   - Transactions: 16 total (4 purchases + 3 donations + 9 distributions)
3. Click **"Yes"** to open the Excel file
4. **Verify Excel contains:**
   - All 16 transactions
   - Columns: Date, Type, Item, SKU, Quantity, Unit Cost, FMV, COGS, Reason, Supplier, Donor, Notes

**Expected Results:**
- ✅ Excel opens with complete transaction log
- ✅ All transaction types included (PURCHASE, DONATION, DISTRIBUTION)
- ✅ Financial details accurate
- ✅ Supplier/donor names preserved
- ✅ File saved to `reports/transaction_history_YYYY-MM-DD.xlsx`

### 6. Test Date Range Filtering

**Steps:**
1. Change **"From"** date to 2 weeks ago
2. Change **"To"** date to today
3. Generate Financial Report again
4. **Verify:**
   - Only transactions in date range included
   - Totals reflect filtered data
   - Confirmation dialog shows updated counts

**Expected Results:**
- ✅ Date filtering works correctly
- ✅ Reports only include transactions in range
- ✅ Totals recalculate properly

## Sample Data Summary

### Current Inventory (after all transactions):

| Item | Purchased | Donated | Distributed | Remaining |
|------|-----------|---------|-------------|-----------|
| Canned Black Beans | 100 | 50 | 70 | 80 |
| White Rice | 300 lbs | 0 | 125 lbs | 175 lbs |
| Spaghetti | 75 boxes | 0 | 20 boxes | 55 boxes |
| Tomato Soup | 0 | 100 | 30 | 70 |
| Corn Flakes | 0 | 40 | 3 | 37 |

### Expected Financial Report Totals:

**Client Distributions:**
- Beans: 70 @ weighted avg cost
- Rice: 125 @ weighted avg cost (~$0.77)
- Pasta: 20 @ $1.25 = $25.00
- Soup: 25 @ $0 (donated) = $0
- Total: ~$150-160

**Spoilage:**
- Soup: 5 @ $0 = $0

**Internal Use:**
- Cereal: 3 @ $0 = $0

**Total COGS: ~$150-160**

### Expected Impact Report Totals:

**Total Donations (FMV):** $290.00
- Beans: 50 @ $2.00 = $100.00
- Soup: 100 @ $1.50 = $150.00
- Cereal: 40 @ $3.50 = $140.00

## Troubleshooting

### Reports not generating?
- Check `reports/` directory exists (created automatically)
- Check console for errors
- Verify sample data was created successfully

### PDFs/Excel files not opening?
- Check default applications for .pdf and .xlsx files
- Files are saved to `reports/` directory - can open manually
- On macOS: Preview for PDF, Numbers/Excel for .xlsx

### Wrong totals?
- Verify weighted average cost calculations
- Check date range filter
- Review transaction history export for all transactions

## Success Criteria

✅ All three report types generate successfully  
✅ PDFs have professional formatting  
✅ Excel files have multiple sheets with proper formatting  
✅ Financial totals match weighted average cost calculations  
✅ Impact report shows correct FMV totals  
✅ Stock status identifies low stock items  
✅ Transaction export includes all transactions  
✅ Date filtering works correctly  
✅ Files open automatically after generation  
✅ Reports saved to `reports/` directory with timestamped names

---

**Application is running!** Navigate to the Reports page and start testing! 🎉
