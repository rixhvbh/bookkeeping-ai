import pandas as pd
from openpyxl.styles import PatternFill
from datetime import datetime

# === File Paths ===
input_file = "Input/Proof of Concept.xlsx"
vendor_map_file = "Input/vendor_mapping.csv"
output_file = "Output/categorized_output_final.xlsx"
uncategorized_csv = "Output/uncategorized_vendors.csv"
log_file = "Logs/processing_log.txt"

# === Load the Ledger Sample Sheet ===
df = pd.read_excel(input_file, sheet_name='Ledger Sample')

# === Clean & Standardize Vendor Column ===
df['Vendor'] = df['Description.1'].astype(str).str.strip().str.lower()

# === Load Vendor Mapping as Dictionary ===
vendor_df = pd.read_csv(vendor_map_file)
vendor_dict = {
    str(row['vendor_name']).strip().lower(): (row['category'], row['account_type'])
    for _, row in vendor_df.iterrows()
}

# === Categorize Transactions ===
def categorize(vendor):
    if 'e-transfer' in vendor:
        return 'E-TRANSFER', ''
    for key in vendor_dict:
        if key in vendor:
            return vendor_dict[key]
    return 'Uncategorized', ''

df['Category'], df['Account Type'] = zip(*df['Vendor'].apply(categorize))

# === Export Uncategorized Vendors for Feedback Loop ===
uncategorized = df[df['Category'] == 'Uncategorized']['Vendor'].drop_duplicates()
uncategorized.to_csv(uncategorized_csv, index=False)

# === Create Summary Sheet ===
summary_df = df.groupby('Category').agg(
    Count=('Category', 'count'),
    Total_Debit=('Debit ', 'sum'),  # NOTE: there's a space after 'Debit '
    Total_Credit=('Credit', 'sum')
).reset_index()

# === Final Columns to Export ===
columns_to_keep = ['Date.1', 'Vendor', 'Debit ', 'Credit', 'Category', 'Account Type']
df_final = df[columns_to_keep].rename(columns={'Date.1': 'Date', 'Debit ': 'Debit'})

# === Export to Excel: Sheet 1 = Categorized, Sheet 2 = Summary ===
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    df_final.to_excel(writer, sheet_name='Categorized', index=False)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

    workbook = writer.book
    worksheet = writer.sheets['Categorized']
    yellow_format = workbook.add_format({'bg_color': '#FFFF00'})

    # === Highlight E-TRANSFER rows in yellow ===
    for i, category in enumerate(df['Category']):
        if category == 'E-TRANSFER':
            worksheet.set_row(i + 1, None, yellow_format)

# === Save Processing Stats ===
with open(log_file, 'w') as log:
    log.write(f"Log Timestamp: {datetime.now()}\n")
    log.write(f"Total Transactions: {len(df)}\n")
    log.write(f"Unique Categories: {df['Category'].nunique()}\n")
    log.write(f"E-Transfers: {sum(df['Category'] == 'E-TRANSFER')}\n")
    log.write(f"Uncategorized Vendors: {len(uncategorized)}\n")
