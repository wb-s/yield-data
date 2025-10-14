import pandas as pd
import requests
from io import StringIO
import os
from datetime import datetime

# CSV URL for 2025 yield curve data
csv_url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2025/all?type=daily_treasury_yield_curve&field_tdr_date_value=2025&page&_format=csv"

# Fetch CSV
response = requests.get(csv_url)
response.raise_for_status()

# Parse CSV into DataFrame
df_new = pd.read_csv(StringIO(response.text))

# Debug: Print Treasury CSV column names to verify
print("Treasury CSV columns:", df_new.columns.tolist())

# Standardize column names to match yield_data_all.csv
df_new.columns = df_new.columns.str.strip()  # Remove whitespace
rename_dict = {
    'Date': 'Date',
    '1 Mo': '1 Mo',
    '1.5 Month': '1.5 Mo',
    '2 Mo': '2 Mo',
    '3 Mo': '3 Mo',
    '4 Mo': '4 Mo',
    '6 Mo': '6 Mo',
    '1 Yr': '1 Yr',
    '2 Yr': '2 Yr',
    '3 Yr': '3 Yr',
    '5 Yr': '5 Yr',
    '7 Yr': '7 Yr',
    '10 Yr': '10 Yr',
    '20 Yr': '20 Yr',
    '30 Yr': '30 Yr'
}
df_new = df_new.rename(columns=rename_dict)

# Keep only relevant columns
relevant_cols = ['Date', '1 Mo', '1.5 Mo', '2 Mo', '3 Mo', '4 Mo', '6 Mo', '1 Yr', '2 Yr', '3 Yr', '5 Yr', '7 Yr', '10 Yr', '20 Yr', '30 Yr']
df_new = df_new[relevant_cols].copy()

# Parse Date column
df_new['Date'] = pd.to_datetime(df_new['Date'], errors='coerce')

# Get the latest row (most recent date)
latest_row = df_new.sort_values('Date').iloc[-1:].copy()

# Load existing data
csv_path = 'year_daily_treasury_rates.csv'
if os.path.exists(csv_path):
    df_all = pd.read_csv(csv_path)
    df_all['Date'] = pd.to_datetime(df_all['Date'])
else:
    df_all = pd.DataFrame(columns=relevant_cols)

# Append if new date, then sort to keep newest first
if latest_row['Date'].iloc[0] not in df_all['Date'].values:
    df_all = pd.concat([latest_row, df_all], ignore_index=True)  # Prepend new row
    df_all = df_all.sort_values('Date', ascending=False).reset_index(drop=True)  # Newest first
    df_all.to_csv(csv_path, index=False)
    print(f"Prepended new data for {latest_row['Date'].iloc[0]} to year_daily_treasury_rates.csv")
else:
    print("No new data to append")

print(f"Current latest date in CSV: {df_all['Date'].max()}")
