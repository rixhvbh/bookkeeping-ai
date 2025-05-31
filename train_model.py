# File: train_model.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime

# === Load and Preprocess Data ===
df = pd.read_csv("Input/train.csv")

# Ensure date format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Create Month Feature
df['Month'] = df['Date'].dt.month

# Clean text
df['Vendor'] = df['Vendor'].astype(str).str.lower().str.strip()

# 💡 Fix: Compute Amount column
df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
df['Amount'] = df['Debit'] - df['Credit']
df['Amount'] = df['Amount'].abs()

# Create amount buckets
def bucket_amount(x):
    if x < 50:
        return 'low'
    elif x < 500:
        return 'medium'
    else:
        return 'high'

df['AmountBucket'] = df['Amount'].apply(bucket_amount)

# === Features and Target ===
X = df[['Vendor', 'AmountBucket', 'Month']]
y = df['Category']

# === Train-Test Split ===
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# === Preprocessing Pipeline ===
preprocessor = ColumnTransformer(
    transformers=[
        ('vendor', TfidfVectorizer(), 'Vendor'),
        ('amount', OneHotEncoder(handle_unknown='ignore'), ['AmountBucket']),
        ('month', OneHotEncoder(handle_unknown='ignore'), ['Month']),
    ]
)

# === Full ML Pipeline ===
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier())
])

# === Train Model ===
pipeline.fit(X_train, y_train)

# === Save Model ===
os.makedirs("Models", exist_ok=True)
joblib.dump(pipeline, "Models/model_client_A.pkl")

# === Accuracy Check ===
acc = pipeline.score(X_val, y_val)
print(f"✅ Model trained successfully! Accuracy on validation set: {acc:.2f}")

# === Optional Log Append ===
os.makedirs("Logs", exist_ok=True)
with open("Logs/run_log.txt", 'a', encoding='utf-8') as log:
    log.write(f"\n=== Model Training Log: {datetime.now()} ===\n")
    log.write(f"Total Records: {len(df)}\n")
    log.write(f"Accuracy: {acc:.2f}\n")
    log.write(f"Categories: {df['Category'].nunique()}\n")
