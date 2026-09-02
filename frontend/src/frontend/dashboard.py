"""eClipseBord - Streamlit dashboard for solar eclipses.

Cleaned data from the FastAPI backend and shows key metrics,
charts, a map, and a table. Backend address is read from the
BACKEND_URL environment variable so that the same code
works both locally with docker compose and in Azure.
"""

import os

import httpx
import pandas as pd
import streamlit as st

# Locally via docker compose - reach the backend on the service name
# "backend". In Azure, BACKEND_URL - set to the deployed backend's URL.
BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="eClipseBord", page_icon="🌑", layout="wide")


@st.cache_data(ttl=300)
def fetch(path: str):
    """Fetch JSON from a backend endpoint."""
    response = httpx.get(f"{BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


st.title("🌑 eClipseBord")
st.caption("Solar eclipses through history with data from NASA's eclipse catalog")
st.write(f"Backend: {BASE_URL}")

# Key metrics at the top
stats = fetch("/eclipses/stats")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total eclipses", f"{stats['total_eclipses']:,}")
col2.metric("Time span", f"{stats['year_min']} - {stats['year_max']}")
col3.metric("Most common type", stats["most_common_type"])
col4.metric("Avg. magnitude", stats["avg_magnitude"])

st.divider()

# Charts: types and trend over time
left, right = st.columns(2)

with left:
    st.subheader("Eclipses by type")
    types_df = pd.DataFrame(fetch("/eclipses/types")).set_index("type")
    st.bar_chart(types_df)

with right:
    st.subheader("Eclipses by century")
    century_df = pd.DataFrame(fetch("/eclipses/by-century")).set_index("century")
    st.line_chart(century_df)

st.divider()

# Map of where the eclipses occur
st.subheader("Where do the eclipses occur?")
records = pd.DataFrame(fetch("/eclipses"))
map_df = records[["Lat", "Lon"]].dropna()
map_df = map_df.rename(columns={"Lat": "latitude", "Lon": "longitude"})
st.map(map_df)

st.divider()

# Raw data table
st.subheader("Raw data")
st.dataframe(records, use_container_width=True)