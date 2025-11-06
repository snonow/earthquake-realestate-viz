import pandas as pd
import altair as alt
import numpy as np
import os

# --- Load data ---
df = pd.read_excel("data/Data_aggregated_v2.xlsx")
df = df.dropna(subset=['Total Earthquake', 'Median Price', 'Year'])

# --- Keep real values ---
df['price'] = df['Median Price']
df['earthquake'] = df['Total Earthquake']

# --- Option: log-scale for color/size for better visuals ---
df['log_quake'] = np.log10(df['earthquake'] + 1)

# --- Compute total earthquakes per state ---
state_totals = df.groupby('State')['earthquake'].sum().sort_values()

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

# --- Filter for California ---
df_ca = df[df['State'] == 'California'].copy()

# --- Center earthquakes for visual encoding ---
quake_scaled = df_ca['earthquake'].copy()
quake_scaled = np.sqrt(quake_scaled)  # square root compression
quake_scaled = (quake_scaled - quake_scaled.min()) / (quake_scaled.max() - quake_scaled.min())  # normalize 0–1
quake_scaled = quake_scaled * 200 + 20  # map to Altair size range
df_ca['quake_size'] = quake_scaled

# --- Aggregate median price per year for California ---
median_prices_ca = (
    df_ca.groupby(['Year', 'quake_group'])
    .agg({'price':'median'})
    .reset_index()
)

# --- Scatter plot for California ---
scatter_ca = alt.Chart(df_ca).mark_circle(opacity=0.6).encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('price:Q', title='Median House Price'),
    color=alt.Color('quake_group:N', scale=alt.Scale(scheme='dark2'), legend=alt.Legend(title='Earthquake Group')),
    size=alt.Size('quake_size:Q', legend=None),
    tooltip=['State:N', 'Year:O', 'Total Earthquake:Q', 'price:Q']
).properties(
    width=900,
    height=600,
    title='Median House Price over Time in California by Earthquake Intensity Group'
)

# --- Trend lines for California ---
lines_ca = alt.Chart(median_prices_ca).mark_line(size=3).encode(
    x='Year:O',
    y='price:Q',
    color='quake_group:N'
)

# --- Combine ---
chart_ca = scatter_ca + lines_ca

# --- Save outputs ---
chart_ca.save('outputs/price_vs_earthquake_california.png', scale_factor=4.0)