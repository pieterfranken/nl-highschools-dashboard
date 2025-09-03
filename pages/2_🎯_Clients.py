import streamlit as st
import pandas as pd

from lib.data import load_schools, toggle_client
from lib.config import ID_COL, NAME_COL, CITY_COL, IS_CLIENT_COL

st.set_page_config(page_title="Clients | Examify Schools", page_icon="🎯", layout="wide")

st.title("🎯 Manage Clients")

# Load data
df = load_schools(with_client_flag=True)

# Quick stats
col1, col2 = st.columns(2)
with col1:
    st.metric("Current clients", int(df[IS_CLIENT_COL].sum()) if IS_CLIENT_COL in df.columns else 0)
with col2:
    st.metric("Total schools", len(df))

st.divider()

# Search and filter
search = st.text_input("Search by name or city")
show_only_clients = st.toggle("Show only clients", value=False)

filtered = df.copy()
if search:
    mask = (
        filtered[NAME_COL].str.contains(search, case=False, na=False)
        | filtered[CITY_COL].str.contains(search, case=False, na=False)
    )
    filtered = filtered[mask]
if show_only_clients and IS_CLIENT_COL in filtered.columns:
    filtered = filtered[filtered[IS_CLIENT_COL] == True]

# Table with actions
st.subheader("Schools")

if filtered.empty:
    st.info("No matching schools.")
else:
    # Action buttons inside the table
    for idx, row in filtered.head(200).iterrows():
        school_id = str(row[ID_COL])
        is_client = bool(row.get(IS_CLIENT_COL, False))
        cols = st.columns([4, 2, 2, 2, 2])
        with cols[0]:
            st.write(f"{row[NAME_COL]} — {row[CITY_COL]}")
        with cols[1]:
            st.write(f"ID: {school_id}")
        with cols[2]:
            st.write("Client" if is_client else "Not client")
        with cols[3]:
            if not is_client and st.button("Mark as client", key=f"add-{school_id}"):
                toggle_client(df, school_id, True)
                st.rerun()
        with cols[4]:
            if is_client and st.button("Remove client", type="secondary", key=f"rm-{school_id}"):
                toggle_client(df, school_id, False)
                st.rerun()

