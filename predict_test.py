# File: predict_test.py

import pandas as pd
import joblib
import os

# === Load Trained Model ===
model = joblib.load("Models/model_client_A.pkl")

# === Load Test Data ===
df = pd.read_csv("Input/test.csv")

# === Clean & Preprocess ===
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# 💡 Handle any missing or malformed dates
df['Month'] = df['Date'].dt.month.fillna(0).astype(int)
df['Month'] = df['Month'].apply(lambda x: x if 1 <= x <= 12 else 1)  # Default to Jan if invalid

# Clean Vendor
df['Vendor'] = df['Vendor'].astype(str).str.lower().str.strip()
df['Vendor'] = df['Vendor'].fillna("unknown")

# Compute Amount (if not already present)
if 'Amount' not in df.columns:
    df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
    df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
    df['Amount'] = df['Debit'] - df['Credit']
    df['Amount'] = df['Amount'].abs()

# === Bucket Amount ===
def bucket_amount(x):
    if x < 50:
        return 'low'
    elif x < 500:
        return 'medium'
    else:
        return 'high'

df['AmountBucket'] = df['Amount'].apply(bucket_amount)

# === Predict Categories ===
df['Predicted Category'] = model.predict(df[['Vendor', 'AmountBucket', 'Month']])

# === Save Output ===
os.makedirs("output", exist_ok=True)
df.to_csv("output/predicted_test.csv", index=False)

print("✅ Prediction complete. Output saved to output/predicted_test.csv")
