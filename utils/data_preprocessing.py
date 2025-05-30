# File: utils/data_preprocessing.py

import pandas as pd
import os

# === FILE PATHS ===
input_file = "Input/Proof of Concept.xlsx"
vendor_map_file = "Input/vendor_mapping.csv"
train_output = "Input/train.csv"
test_output = "Input/test.csv"

# === Load Data ===
df = pd.read_excel(input_file, sheet_name='Ledger Sample')
vendor_map = pd.read_csv(vendor_map_file)

# === Vendor Mapping to Dict ===
vendor_dict = {
    str(row['vendor_name']).strip().lower(): (row['category'], row['account_type'])
    for _, row in vendor_map.iterrows()
}

# === Clean Vendor Field ===
df['Vendor'] = df['Description.1'].astype(str).str.strip().str.lower()

# === Remove rows with missing Vendor info ===
df = df[df['Vendor'].notna() & (df['Vendor'] != '')]

# === Assign Categories and Account Type ===
def categorize(vendor):
    if 'e-transfer' in vendor:
        return 'E-TRANSFER', ''
    for key in vendor_dict:
        if key in vendor:
            return vendor_dict[key]
    return 'Uncategorized', ''

df['Category'], df['Account Type'] = zip(*df['Vendor'].apply(categorize))

# === Drop E-TRANSFERS for now ===
df = df[df['Category'] != 'E-TRANSFER']

# === Select and Rename Columns ===
df_final = df[['Date.1', 'Vendor', 'Debit ', 'Credit', 'Category']].copy()
df_final.columns = ['Date', 'Vendor', 'Debit', 'Credit', 'Category']

# === Create train and test sets ===
train_df = df_final[df_final['Category'] != 'Uncategorized']
test_df = df_final[df_final['Category'] == 'Uncategorized'].drop(columns=['Category'])

# === Save them ===
os.makedirs("Input", exist_ok=True)
train_df.to_csv(train_output, index=False)
test_df.to_csv(test_output, index=False)

print(f"✅ Preprocessing Complete:\n - Train: {train_df.shape}\n - Test: {test_df.shape}")
