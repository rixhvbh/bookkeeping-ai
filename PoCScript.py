import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# === File Paths ===
input_path = 'Input/Proof of Concept.xlsx'
vendor_map_path = 'Input/vendor_mapping.csv'
output_path = 'Output/categorized_output.xlsx'

# === Load the sheet named 'Ledger Sample'
df = pd.read_excel(input_path, sheet_name='Ledger Sample')

# === Clean Vendor Column
df['Vendor'] = df['Description.1'].astype(str).str.strip().str.lower()

# === Load vendor mapping CSV
vendor_df = pd.read_csv(vendor_map_path)

# === Create vendor mapping dictionary
vendor_dict = {}
for index, row in vendor_df.iterrows():
    vendor = str(row['vendor_name']).strip().lower()
    category = row['category']
    account_type = row['account_type']
    vendor_dict[vendor] = (category, account_type)

# === Categorization function
def categorize(vendor):
    if 'e-transfer' in vendor:
        return 'E-TRANSFER', ''
    for v_key in vendor_dict:
        if v_key in vendor:
            return vendor_dict[v_key]
    return 'Uncategorized', ''

# === Apply categorization
df['Category'], df['Account Type'] = zip(*df['Vendor'].apply(categorize))

# === Write to Excel with highlighting for E-TRANSFER
with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Categorized')

    workbook = writer.book
    worksheet = writer.sheets['Categorized']
    yellow_fill = workbook.add_format({'bg_color': '#FFFF00'})

    for i, value in enumerate(df['Category']):
        if value == 'E-TRANSFER':
            worksheet.set_row(i + 1, None, yellow_fill)

print("✅ Categorized output saved in 'Output/categorized_output.xlsx'")


