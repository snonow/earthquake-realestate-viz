import os
import pandas as pd

# --- Load CSVs ---
df_prices = pd.read_csv("data/realtor-data.csv")
df_eq = pd.read_csv("data/Eartquakes-1990-2023.csv")

# --- Extract year from realtor data ---
df_prices['Year'] = pd.to_datetime(df_prices['prev_sold_date'], errors='coerce').dt.year
df_prices = df_prices.dropna(subset=['Year'])
df_prices['Year'] = df_prices['Year'].astype(int)

# --- Extract year from earthquake data ---
df_eq['Year'] = pd.to_datetime(df_eq['time'], errors='coerce').dt.year
df_eq = df_eq.dropna(subset=['Year'])
df_eq['Year'] = df_eq['Year'].astype(int)

# --- Keep relevant columns and rename to match ---
df_prices = df_prices.rename(columns={'state':'State', 'price':'Median Price'})
df_eq = df_eq.rename(columns={'state':'State', 'magnitudo':'Total Earthquake'})

# --- Aggregate earthquake data by state and year ---
df_eq_agg = df_eq.groupby(['State','Year'])['Total Earthquake'].sum().reset_index()

# --- Merge on State and Year ---
df = pd.merge(df_prices, df_eq_agg, on=['State','Year'], how='inner')

# --- Create folder for processed data ---
os.makedirs("data/processed", exist_ok=True)

# --- Save as Parquet (compressed) ---
df.to_parquet(
    "data/processed/realtor_earthquake.parquet",
    engine='pyarrow',
    index=False,
    compression='snappy'
)

# --- Optionally save as Feather for fast access ---
# df.to_feather("data/processed/realtor_earthquake.feather")

print(f"Merged DataFrame saved successfully! Shape: {df.shape}")