import pandas as pd
import os
from datetime import datetime

# === Load the predicted transactions ===
df = pd.read_csv("output/predicted_test.csv")

# === Chart of Accounts Mapping ===
chart_of_accounts = {
    'Food Purchases': ('Food Purchases', 'Expense', 'Debit'),
    'Service Revenue': ('Service Revenue', 'Revenue', 'Credit'),
    'Office Supplies': ('Office Supplies', 'Expense', 'Debit'),
    'Consulting Income': ('Consulting Income', 'Revenue', 'Credit'),
    'Utilities': ('Utilities', 'Expense', 'Debit'),
    'Rent Expense': ('Rent Expense', 'Expense', 'Debit'),
    'Interest Income': ('Interest Income', 'Revenue', 'Credit'),
    'Miscellaneous Expense': ('Miscellaneous Expense', 'Expense', 'Debit'),
    'Bank Charges': ('Bank Charges', 'Expense', 'Debit'),
    'Travel Expense': ('Travel Expense', 'Expense', 'Debit'),
    'Advertising': ('Advertising', 'Expense', 'Debit'),
    'Salaries': ('Salaries', 'Expense', 'Debit'),
    'Loan Payable': ('Loan Payable', 'Liability', 'Credit'),
    'Accounts Receivable': ('Accounts Receivable', 'Asset', 'Debit'),
    'Accounts Payable': ('Accounts Payable', 'Liability', 'Credit'),
    'Cash': ('Cash', 'Asset', 'Debit'),
    'Bank': ('Bank', 'Asset', 'Debit'),
    'Owner’s Equity': ('Owner’s Equity', 'Equity', 'Credit'),
    'Drawings': ('Drawings', 'Equity', 'Debit'),
    # Add additional accounts as necessary
}


# === Flags, Cleanup, and Column Normalization ===
df['Is_E_Transfer'] = df['Vendor'].str.contains('e-transfer', case=False, na=False)
df['Vendor'] = df['Vendor'].astype(str).str.title()
df['Predicted Category'] = df['Predicted Category'].astype(str).str.title()

# Ensure Date column exists and is datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# === Build Journal Entries ===
journal_entries = []

for idx, row in df.iterrows():
    category = row['Predicted Category']
    vendor = row['Vendor']
    date = row['Date']

    if pd.isna(category) or category not in chart_of_accounts:
        continue

    # Compute amount
    debit = row.get('Debit', 0) or 0
    credit = row.get('Credit', 0) or 0
    amount = debit if debit > 0 else credit
    if amount == 0:
        continue  # skip blank amounts

    account_name, account_type, drcr = chart_of_accounts[category]

    if drcr == 'Debit':
        journal_entries.append({
            'Date': date,
            'Description': vendor,
            'Account': account_name,
            'Debit': amount,
            'Credit': '',
            'Is_E_Transfer': row['Is_E_Transfer']
        })
        journal_entries.append({
            'Date': date,
            'Description': vendor,
            'Account': 'Cash/Bank',
            'Debit': '',
            'Credit': amount,
            'Is_E_Transfer': row['Is_E_Transfer']
        })
    else:
        journal_entries.append({
            'Date': date,
            'Description': vendor,
            'Account': 'Cash/Bank',
            'Debit': amount,
            'Credit': '',
            'Is_E_Transfer': row['Is_E_Transfer']
        })
        journal_entries.append({
            'Date': date,
            'Description': vendor,
            'Account': account_name,
            'Debit': '',
            'Credit': amount,
            'Is_E_Transfer': row['Is_E_Transfer']
        })

# === Convert to DataFrame and Beautify ===
journal_df = pd.DataFrame(journal_entries)
journal_df['Debit'] = pd.to_numeric(journal_df['Debit'], errors='coerce').fillna(0)
journal_df['Credit'] = pd.to_numeric(journal_df['Credit'], errors='coerce').fillna(0)

# === Validate DR/CR ===
total_debit = journal_df['Debit'].sum()
total_credit = journal_df['Credit'].sum()
journal_balanced = abs(total_debit - total_credit) < 0.01

# === Beautify Headers ===
journal_df.columns = [col.replace("_", " ").title() for col in journal_df.columns]

# === Export Journal Entries to Excel ===
os.makedirs("output", exist_ok=True)
journal_df.to_excel("output/journal_entries.xlsx", index=False)

# === Trial Balance Summary ===
trial_balance = journal_df.groupby("Account").agg({
    "Debit": "sum",
    "Credit": "sum"
}).reset_index()
trial_balance.to_excel("output/trial_balance_summary.xlsx", index=False)

# === Append to Log ===
log_file_path = "logs/run_log.txt"
os.makedirs("logs", exist_ok=True)

with open(log_file_path, 'a', encoding='utf-8') as log:
    log.write(f"\n=== Journal Entry Log: {datetime.now()} ===\n")
    log.write(f"Total Entries: {len(journal_df)}\n")
    log.write(f"Unique Accounts Used: {journal_df['Account'].nunique()}\n")
    log.write(f"Total Debit: {total_debit:.2f}\n")
    log.write(f"Total Credit: {total_credit:.2f}\n")
    log.write("Journal Balanced ✅\n" if journal_balanced else "🚨 Journal Unbalanced ❌\n")




######
print(df['Month'].unique())  # Check what months are being passed
print(df[['Vendor', 'AmountBucket', 'Month']].head())
