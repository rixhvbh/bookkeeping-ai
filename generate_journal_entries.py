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
    'Cash Sales': ('Sales - Cash', 'Revenue', 'Credit'),
    'Rent': ('Rent Expense', 'Expense', 'Debit'),
    'Bank Charges': ('Bank Charges', 'Expense', 'Debit'),
    'Miscellaneous': ('Misc Expenses', 'Expense', 'Debit'),
    'Stripe': ('Service Revenue', 'Revenue', 'Credit'),
    'Paypal': ('Service Revenue', 'Revenue', 'Credit'),
}

# === Flags and Cleanup ===
df['Is_E_Transfer'] = df['Vendor'].str.contains('e-transfer', case=False, na=False)
df['Vendor'] = df['Vendor'].astype(str).str.title()
df['Predicted Category'] = df['Predicted Category'].astype(str).str.title()

# === Build Journal Entries ===
journal_entries = []

for idx, row in df.iterrows():
    category = row['Predicted Category']
    vendor = row['Vendor']
    date = row['Date']

    if pd.isna(category) or category not in chart_of_accounts:
        continue

    # Compute Amount from Debit/Credit
    debit = row.get('Debit', 0) or 0
    credit = row.get('Credit', 0) or 0
    amount = debit if debit > 0 else credit

    account_name, account_type, drcr = chart_of_accounts[category]

    if drcr == 'Debit':
        journal_entries.append({
            'Date': date,
            'Description': vendor,
            'Account': account_name,
            'Debit': amount,
            'Credit': ''
        })
        journal_entries.append({
            'Date': date,
            'Description': vendor,
            'Account': 'Cash/Bank',
            'Debit': '',
            'Credit': amount
        })
    else:
        journal_entries.append({
            'Date': date,
            'Description': vendor,
            'Account': 'Cash/Bank',
            'Debit': amount,
            'Credit': ''
        })
        journal_entries.append({
            'Date': date,
            'Description': vendor,
            'Account': account_name,
            'Debit': '',
            'Credit': amount
        })


# === Convert to DataFrame and Beautify ===
journal_df = pd.DataFrame(journal_entries)
journal_df['Debit'] = pd.to_numeric(journal_df['Debit'], errors='coerce').fillna(0)
journal_df['Credit'] = pd.to_numeric(journal_df['Credit'], errors='coerce').fillna(0)

# === Validate DR/CR ===
total_debit = journal_df['Debit'].sum()
total_credit = journal_df['Credit'].sum()
journal_balanced = abs(total_debit - total_credit) < 0.01

# === Export Journal Entries to Excel ===
os.makedirs("output", exist_ok=True)
journal_df.to_excel("output/journal_entries.xlsx", index=False)

# === Trial Balance Summary ===
trial_balance = journal_df.groupby('Account').agg({
    'Debit': 'sum',
    'Credit': 'sum'
}).reset_index()
trial_balance.to_excel("output/trial_balance_summary.xlsx", index=False)

# === Append to Log ===
log_file_path = "logs/run_log.txt"
os.makedirs("logs", exist_ok=True)

with open(log_file_path, 'a') as log:
    log.write(f"\n=== Journal Entry Log: {datetime.now()} ===\n")
    log.write(f"Total Entries: {len(journal_df)}\n")
    log.write(f"Unique Accounts Used: {journal_df['Account'].nunique()}\n")
    log.write(f"Total Debit: {total_debit:.2f}\n")
    log.write(f"Total Credit: {total_credit:.2f}\n")
    log.write("Journal Balanced: YES\n" if journal_balanced else "Journal Balanced: NO (Check DR/CR mismatch!)\n")
