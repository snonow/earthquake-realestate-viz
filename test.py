import altair as alt
from vega_datasets import data

# Load a sample dataset
cars = data.cars()

# Create a simple chart
chart = alt.Chart(cars).mark_point().encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin'
)

# Save to PNG (requires vl-convert)
chart.save('data/chart.png')
