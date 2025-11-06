import streamlit as st
import altair as alt
import pandas as pd
import us
from vega_datasets import data

# --- Load data ---
df = pd.read_excel("data/Data_aggregated_v2.xlsx")
df['fips'] = df['State'].apply(lambda x: int(us.states.lookup(x).fips))

# Fill NaNs with 0 for mapping
df['Total Earthquake_filled'] = df['Total Earthquake'].fillna(0)
df['Median_Price_filled'] = df['Median Price'].fillna(0)

# --- US map TopoJSON ---
us_states = alt.topo_feature(data.us_10m.url, 'states')

# --- Year slider ---
year = st.slider("Select Year", int(df['Year'].min()), int(df['Year'].max()), 2013)
df_year = df[df['Year'] == year]

# --- Earthquake map (red/maroon) ---
heatmap_eq = alt.Chart(us_states).mark_geoshape().encode(
    color=alt.Color(
        'Total Earthquake_filled:Q',
        scale=alt.Scale(range=['#ffe6e6', '#800000']),  # light pink -> maroon
        title="Earthquake Count"
    ),
    tooltip=['State:N', 'Total Earthquake_filled:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df_year, 'fips', ['Total Earthquake_filled', 'State'])
).project('albersUsa')

heatmap_eq_outline = alt.Chart(us_states).mark_geoshape(
    fill='none', stroke='black', strokeWidth=0.5
).project('albersUsa')

heatmap_eq_layered = alt.layer(heatmap_eq, heatmap_eq_outline).properties(
    title=f"Earthquake Intensity ({year})",
    width=400, height=300
)

# --- House price map (green/blue) ---
heatmap_price = alt.Chart(us_states).mark_geoshape().encode(
    color=alt.Color(
        'Median_Price_filled:Q',
        scale=alt.Scale(range=['#e6f2ff', '#0055aa']),  # light blue -> dark blue
        title="Median House Price"
    ),
    tooltip=['State:N', 'Median_Price_filled:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df_year, 'fips', ['Median_Price_filled', 'State'])
).project('albersUsa')

heatmap_price_outline = alt.Chart(us_states).mark_geoshape(
    fill='none', stroke='black', strokeWidth=0.5
).project('albersUsa')

heatmap_price_layered = alt.layer(heatmap_price, heatmap_price_outline).properties(
    title=f"Median House Price ({year})",
    width=400, height=300
)

# --- Display maps side by side ---
st.subheader("US Maps by State")
st.altair_chart(alt.hconcat(heatmap_eq_layered, heatmap_price_layered).resolve_scale(color='independent'), width='stretch')

# --- Prepare data for correlation ---
df_corr = df_year[['State', 'Total Earthquake', 'Median Price']].dropna()

# --- Scatter plot: Earthquake vs House Price ---
scatter = alt.Chart(df_corr).mark_circle(size=100).encode(
    x=alt.X('Total Earthquake:Q', title='Total Earthquake'),
    y=alt.Y('Median Price:Q', title='Median House Price'),
    tooltip=['State:N', 'Total Earthquake:Q', 'Median Price:Q'],
    color=alt.value('#1f77b4')  # blue points
).properties(
    width=800, height=400,
    title=f'Correlation between Earthquake and House Prices ({year})'
)

# --- Regression line ---
regression = scatter.transform_regression('Total Earthquake', 'Median Price').mark_line(color='red')
scatter_combined = scatter + regression

# --- Display in Streamlit ---
st.subheader("Correlation between Earthquake and House Prices")
st.altair_chart(scatter_combined, width='stretch')
