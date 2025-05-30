import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

input_path = 'Input/Proof of Concept.xlsx'
vendor_map_path = 'Input/vendor_mapping.csv'
output_path = 'Output/categorized_output.xlsx'

df = pd.read_excel(input_path, sheet_name='Ledger Sample')

df['Vendor'] = df['Description.1'].astype(str).str.strip().str.lower()

vendor_df = pd.read_csv(vendor_map_path)

vendor_dict = {}
for index, row in vendor_df.iterrows():
    vendor = str(row['vendor_name']).strip().lower()
    category = row['category']
    account_type = row['account_type']
    vendor_dict[vendor] = (category, account_type)

def categorize(vendor):
    if 'e-transfer' in vendor:
        return 'E-TRANSFER', ''
    for v_key in vendor_dict:
        if v_key in vendor:
            return vendor_dict[v_key]
    return 'Uncategorized', ''

df['Category'], df['Account Type'] = zip(*df['Vendor'].apply(categorize))

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Categorized')

    workbook = writer.book
    worksheet = writer.sheets['Categorized']
    yellow_fill = workbook.add_format({'bg_color': '#FFFF00'})

    for i, value in enumerate(df['Category']):
        if value == 'E-TRANSFER':
            worksheet.set_row(i + 1, None, yellow_fill)

print("✅ Categorized output saved in 'Output/categorized_output.xlsx'")


