import pandas as pd
import altair as alt
import numpy as np
import os

# --- Load preprocessed Parquet ---
df = pd.read_parquet("data/processed/realtor_earthquake.parquet")

# --- Keep proper columns ---
df = df.dropna(subset=['Median Price', 'Total Earthquake', 'Year', 'State'])

# --- Option: log-scale for color/size for better visuals ---
df['log_quake'] = np.log10(df['Total Earthquake'] + 1)

# --- Compute total earthquakes per state ---
state_totals = df.groupby('State')['Total Earthquake'].sum().sort_values()

# --- Classify states as High or Low earthquake ---
threshold_high = state_totals.quantile(0.8)
threshold_low = state_totals.quantile(0.2)

def classify_state(state):
    total = state_totals[state]
    if total >= threshold_high:
        return 'High Earthquake'
    elif total <= threshold_low:
        return 'Low Earthquake'
    else:
        return 'Medium'

df['quake_group'] = df['State'].apply(classify_state)

# Keep only High and Low for clarity
df_selected = df[df['quake_group'].isin(['High Earthquake', 'Low Earthquake'])]

# --- Fix Year type ---
df_selected['Year'] = df_selected['Year'].astype(int)

# --- Center earthquakes for visual encoding ---
quake_scaled = df_selected['Total Earthquake'].copy()
quake_scaled = np.sqrt(quake_scaled)  # square root compression
quake_scaled = (quake_scaled - quake_scaled.min()) / (quake_scaled.max() - quake_scaled.min())  # normalize 0–1
quake_scaled = quake_scaled * 200 + 20  # map to Altair size range
df_selected['quake_size'] = quake_scaled

# --- Aggregate median price per year and group ---
median_prices = (
    df_selected.groupby(['Year', 'quake_group'])
    .agg({'Median Price':'median'})
    .reset_index()
)

# --- Scatter plot: Year vs Price, colored by earthquake group ---
scatter_group = alt.Chart(df_selected).mark_circle(opacity=0.6).encode(
    x=alt.X('Year:O', title='Year'),  # utiliser Year int directement
    y=alt.Y('Median Price:Q', title='Median House Price'),
    color=alt.Color('quake_group:N', scale=alt.Scale(scheme='dark2'), legend=alt.Legend(title='Earthquake Group')),
    size=alt.Size('quake_size:Q', legend=None),  # use centered size
    tooltip=['State:N', 'Year:O', 'Total Earthquake:Q', 'Median Price:Q']
).properties(
    width=900,
    height=600,
    title='Median House Price over Time by Earthquake Intensity Group (centered visualization)'
)

# --- Add trend lines for High vs Low ---
lines_group = alt.Chart(median_prices).mark_line(size=3).encode(
    x='Year:O',
    y='Median Price:Q',
    color='quake_group:N'
)

# --- Combine ---
chart_group = scatter_group + lines_group

# --- Save outputs ---
os.makedirs("outputs", exist_ok=True)
chart_group.save('outputs/price_vs_earthquake_parquet.png', scale_factor=4.0)
