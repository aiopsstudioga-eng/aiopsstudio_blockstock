# AIOps Studio - Inventory: User Manual

## Introduction
Welcome to **AIOps Studio - Inventory**, a professional inventory management system designed specifically for food pantries and non-profit organizations. This application helps you track inventory levels, manage costs, and report on your impact.

## Key Features
- **Item Management**: Track items with SKUs, categories, and categories.
- **Color-Coded Workflows**:
  - 💰 **Purchases (Blue)**: Track spending and update weighted average costs.
  - 🎁 **Donations (Green)**: Record donations and track Fair Market Value (FMV).
  - 📤 **Distribution (Orange)**: Distribute to clients and track cost of goods sold (COGS).
- **Reporting**: Generate professional PDF and Excel reports.

---

## 🚀 Getting Started

### Launching the Application
Double-click the **AIOps Studio - Inventory** icon to start the program.

### The Dashboard
The dashboard gives you a quick overview of your inventory:
- **Total Items**: Number of unique items in the system.
- **Total Value**: Total financial value of your inventory.
- **Low Stock**: Alerts for items running low.

---

## 📦 Managing Items

### Adding a New Item
1. Go to the **Items** page or click **Inventory > New Item** in the menu.
2. Click **"+ New Item"**.
3. Fill in the details:
   - **SKU**: Unique identifier (e.g., `BEAN001`).
   - **Name**: Item name (e.g., `Canned Black Beans`).
   - **UOM**: Unit of Measure (e.g., `Can`, `Lb`, `Box`).
   - **Reorder Threshold**: Count at which you want to be alerted.
4. Click **Save**.

### Editing an Item
Double-click any item in the list or select it and click **Edit**.

### Deleting an Item
Select an item and click **Delete**. *Note: Items are "soft deleted" to preserve transaction history.*

---

## 📥 Recording Intake

### Purchases (Blue)
Use this when you spend money on inventory.
1. Click **Intake** in the sidebar.
2. Select **💰 Purchase**.
3. Select the item, enter Quantity and Unit Cost.
4. Click **Record Purchase**.
*This updates the "Weighted Average Cost" of your inventory.*

### Donations (Green)
Use this when you receive free items.
1. Click **Intake** in the sidebar.
2. Select **🎁 Donation**.
3. Select the item, enter Quantity and Fair Market Value (FMV).
4. Click **Record Donation**.
*Donations have a $0.00 cost to you but track value for impact reporting.*

---

## 📤 Distributing Items

### Recording Distribution (Orange)
1. Click **Distribution** in the sidebar.
2. Select **📤 Record Distribution**.
3. FIll in the form:
   - **Item**: Select the item to distribute.
   - **Quantity**: Amount leaving inventory.
   - **Reason Code**:
     - **Client Distribution**: Standard distribution to families/individuals.
     - **Spoilage/Expiration**: Damaged or expired goods.
     - **Internal Use**: Items used by staff/volunteers.
4. Click **Confirm Distribution**.

---

## 📈 Reporting

Access reports via the **Reports** tab.

### 1. Financial Report (COGS)
- **Use for:** Accounting and grant reporting.
- **Shows:** Real money spent on distributed items.
- **Format:** PDF.

### 2. Impact Report (FMV)
- **Use for:** Donor newsletters and impact statements.
- **Shows:** Value of donated goods received and distributed.
- **Format:** Excel.

### 3. Stock Status Report
- **Use for:** Reordering and inventory counts.
- **Shows:** Current stock levels and low-stock alerts.
- **Format:** PDF.

### 4. Transaction History
- **Use for:** Auditing.
- **Shows:** Complete log of every movement in the system.
- **Format:** Excel export.

---

## 🔧 Troubleshooting

### "Database Locked" Error
If you see this error, ensure no other instance of the application is open.

### "Insufficient Inventory"
You cannot distribute more items than you have on hand. Check your stock levels.

### Backups
Go to **File > Backup Database** to save a copy of your data data to a safe location.

---
*© 2026 AIOps Studio*
