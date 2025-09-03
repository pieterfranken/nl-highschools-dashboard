import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

from lib.data import load_schools, resolve_data_file
from lib.maps import build_map
from lib.config import IS_CLIENT_COL, NAME_COL, CITY_COL, PROVINCE_COL

st.set_page_config(page_title="Map | Examify Schools", page_icon="🗺️", layout="wide")

st.title("🗺️ Client & Schools Map")

# Load data
df = load_schools(with_client_flag=True)
loaded_file = resolve_data_file()

# Data status banner
with_coords = df[df['latitude'].notna() & df['longitude'].notna()] if 'latitude' in df.columns and 'longitude' in df.columns else df.iloc[0:0]
st.caption(f"Data: {loaded_file.name} | Schools with coordinates: {len(with_coords):,}")

# Filters
colf1, colf2, colf3 = st.columns(3)
with colf1:
    only_clients = st.toggle("Show only clients", value=False)
with colf2:
    provinces = ["All"] + (sorted(df[PROVINCE_COL].dropna().unique().tolist()) if PROVINCE_COL in df.columns else [])
    province = st.selectbox("Province", options=provinces, index=0)
with colf3:
    search = st.text_input("Search (name or city)")

# Filter
data = df.copy()
if province != "All" and PROVINCE_COL in data.columns:
    data = data[data[PROVINCE_COL] == province]
if search:
    mask = (
        data[NAME_COL].str.contains(search, case=False, na=False)
        | data[CITY_COL].str.contains(search, case=False, na=False)
    )
    data = data[mask]
if only_clients and IS_CLIENT_COL in data.columns:
    data = data[data[IS_CLIENT_COL] == True]

# Map
m = build_map(data, only_clients=only_clients)
if m is None:
    st.info("No data to display on the map.")
else:
    st_folium(m, height=650)

# Summary
st.markdown("---")
st.caption(f"Showing {len(data):,} schools")

