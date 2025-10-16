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

# Remove any rows with invalid dates
df_new = df_new.dropna(subset=['Date'])

print(f"Fetched {len(df_new)} rows from Treasury (date range: {df_new['Date'].min()} to {df_new['Date'].max()})")

# Load existing data
csv_path = 'year_daily_treasury_rates.csv'
if os.path.exists(csv_path):
    df_all = pd.read_csv(csv_path)
    df_all['Date'] = pd.to_datetime(df_all['Date'])
    print(f"Existing CSV has {len(df_all)} rows (latest date: {df_all['Date'].max()})")
else:
    df_all = pd.DataFrame(columns=relevant_cols)
    print("No existing CSV found, creating new one")

# Find missing dates: new data not already in existing CSV
missing_dates = df_new[~df_new['Date'].isin(df_all['Date'])].copy()
print(f"Found {len(missing_dates)} new/missing rows to add")

if len(missing_dates) > 0:
    # Combine existing + new data
    df_all = pd.concat([df_all, missing_dates], ignore_index=True)
    
    # Sort by date (newest first) and remove duplicates
    df_all = df_all.sort_values('Date', ascending=False).drop_duplicates(subset=['Date']).reset_index(drop=True)
    
    # Save updated CSV
    df_all.to_csv(csv_path, index=False)
    print(f"Added {len(missing_dates)} new rows. Total rows now: {len(df_all)}")
    print(f"New date range: {df_all['Date'].min()} to {df_all['Date'].max()}")
else:
    print("No new data to add")

print(f"Update complete! Latest date in CSV: {df_all['Date'].max()}")
