"""
Map building utilities with Folium for Streamlit.
"""
from __future__ import annotations

import folium
from folium.plugins import MarkerCluster
from typing import Optional
import pandas as pd

from lib.config import (
    NL_CENTER,
    DEFAULT_ZOOM,
    LAT_COL,
    LON_COL,
    NAME_COL,
    CITY_COL,
    WEBSITE_COL,
    IS_CLIENT_COL,
)
from lib.data import normalize_url

CLIENT_COLOR = "#2ca02c"  # green
NONCLIENT_COLOR = "#1f77b4"  # blue


def add_school_marker(map_obj: folium.Map, row: pd.Series) -> None:
    lat, lon = row.get(LAT_COL), row.get(LON_COL)
    if pd.isna(lat) or pd.isna(lon):
        return
    is_client = bool(row.get(IS_CLIENT_COL, False))
    color = CLIENT_COLOR if is_client else NONCLIENT_COLOR

    site = normalize_url(row.get(WEBSITE_COL))
    link = f'<a href="{site}" target="_blank">Website</a>' if site else ''
    popup_html = f"""
        <b>{row.get(NAME_COL, 'School')}</b><br/>
        {row.get(CITY_COL, '')}<br/>
        {link}
    """
    folium.CircleMarker(
        location=(lat, lon),
        radius=6 if is_client else 5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=folium.Popup(popup_html, max_width=300),
    ).add_to(map_obj)


def build_map(df: pd.DataFrame, only_clients: bool = False) -> Optional[folium.Map]:
    if df.empty:
        return None
    m = folium.Map(location=NL_CENTER, zoom_start=DEFAULT_ZOOM, tiles="CartoDB positron")

    cluster = MarkerCluster().add_to(m)
    data = df.copy()
    if only_clients and IS_CLIENT_COL in data.columns:
        data = data[data[IS_CLIENT_COL] == True]

    for _, row in data.iterrows():
        lat, lon = row.get(LAT_COL), row.get(LON_COL)
        if pd.notna(lat) and pd.notna(lon):
            add_school_marker(cluster, row)

    return m

