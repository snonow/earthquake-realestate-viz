import streamlit as st
import altair as alt
import pandas as pd
import us
from vega_datasets import data

# --- Load data ---
df = pd.read_excel("data/Data_aggregated_v2.xlsx")
df['fips'] = df['State'].apply(lambda x: int(us.states.lookup(x).fips))

# Fill NaNs with a neutral value (e.g., 0 or a small number)
# We'll also create a new column to distinguish NaNs for tooltip or color
df['Total_Earthquake_filled'] = df['Total Earthquake'].fillna(0)
df['is_nan'] = df['Total Earthquake'].isna()  # True if original value was NaN

# --- US map TopoJSON ---
us_states = alt.topo_feature(data.us_10m.url, 'states')

# --- Year slider ---
year = st.slider("Select Year", int(df['Year'].min()), int(df['Year'].max()), 2013)
df_year = df[df['Year'] == year]

# --- Let user pick theme manually ---
theme_choice = st.radio("Choose color theme", ["light", "dark"])
if theme_choice == "dark":
    low_color = "#222222"   # dark background friendly
    high_color = "#ff6666"  # red
    missing_color = "#444444" # neutral for NaN
else:
    low_color = "#ffffff"   # very light
    high_color = "#d73027"  # red
    missing_color = "#cccccc" # neutral gray for NaN

# --- Map with conditional color ---
heatmap_fill = alt.Chart(us_states).mark_geoshape().encode(
    color=alt.condition(
        'datum.Total_Earthquake_filled == 0',
        alt.value(missing_color),  # NaN/0 values get neutral color
        alt.Color('Total_Earthquake_filled:Q', scale=alt.Scale(range=[low_color, high_color], domainMin=0))
    ),
    tooltip=['State:N', 'Total_Earthquake_filled:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df_year, 'fips', ['Total_Earthquake_filled', 'State'])
).project('albersUsa')

# --- Outline layer ---
heatmap_outline = alt.Chart(us_states).mark_geoshape(
    fill='none',
    stroke='black',
    strokeWidth=0.5
).project('albersUsa')

# --- Combine layers ---
heatmap = alt.layer(heatmap_fill, heatmap_outline).properties(
    title=f"Earthquake Intensity by State ({year})"
)

# --- Display in Streamlit ---
st.altair_chart(heatmap, use_container_width=True)
