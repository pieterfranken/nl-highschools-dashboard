#!/usr/bin/env python3
"""
🎓 Dutch High Schools Interactive Dashboard
An interactive web application for exploring the comprehensive dataset of Dutch secondary schools.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium

# Examify modular utilities
from lib.data import load_schools as load_schools_lib, toggle_client
from lib.maps import build_map
from lib.config import ID_COL, NAME_COL, CITY_COL, PROVINCE_COL, IS_CLIENT_COL

# Page configuration
st.set_page_config(
    page_title="🎓 Dutch High Schools Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(clients_version: int = 0):
    """Load schools with coordinates and client flags via lib.data.
    The clients_version param breaks cache when client set changes.
    """
    try:
        _ = clients_version  # used for caching key
        return load_schools_lib(with_client_flag=True)
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        st.stop()

def main():

    # Header
    st.markdown('<h1 class="main-header">🎓 Dutch High Schools Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("**Comprehensive analysis of 1,620+ Dutch secondary schools with detailed metrics and insights**")

    # Add info about the data source and last update
    with st.expander("ℹ️ About this Dashboard"):
        st.markdown("""
        **Data Source:** DUO (Dienst Uitvoering Onderwijs) - Official Dutch Education Data

        **What's included:**
        - 1,620 Dutch high schools (VO - Voortgezet Onderwijs)
        - 34 detailed data columns including contact info, education levels, and enrollment
        - Geographic analysis across all 12 Dutch provinces
        - Education structure breakdown (PRO, VMBO, MAVO, HAVO, VWO, BRUGJAAR)

        **Features:**
        - Interactive filtering and real-time updates
        - School finder with search functionality
        - Contact information and digital presence analysis
        - Comprehensive education level statistics

        **GitHub Repository:** [nl-highschools](https://github.com/pieterfranken/nl-highschools)
        """)

    # Load data
    clients_version = st.session_state.get("clients_version", 0)
    df = load_data(clients_version)
    
    # Sidebar quick navigation
    st.sidebar.header("📂 Navigation")
    try:
        if st.sidebar.button("🗺️ Open Map"):
            st.switch_page("pages/1_🗺️_Map.py")
        if st.sidebar.button("🎯 Open Clients"):
            st.switch_page("pages/2_🎯_Clients.py")
    except Exception:
        pass

    # Sidebar filters
    st.sidebar.header("🔍 Filters & Options")

    # Show GitHub sync status (concise)
    try:
        from lib.data import has_github_token, github_clients_count
        if has_github_token():
            cnt = github_clients_count()
            last = st.session_state.get("github_save_time")
            note = f"GitHub sync ✓{'' if cnt is None else f' ({cnt})'}"
            if last:
                note += f" • {last[:19]}Z"
            st.sidebar.caption(note)
        else:
            st.sidebar.caption("Clients stored locally")
    except Exception:
        pass

    # Province filter
    provinces = ['All'] + sorted(df['province'].dropna().unique().tolist())
    selected_province = st.sidebar.selectbox("📍 Select Province", provinces)

    # Education level filter (only relevant levels)
    education_levels = st.sidebar.multiselect(
        "🎓 Education Levels",
        ['VMBO', 'HAVO', 'VWO'],
        default=['HAVO', 'VWO']
    )

    # School size filter
    size_categories = ['All'] + sorted(df['school_size_category'].dropna().unique().tolist())
    selected_size = st.sidebar.selectbox("📊 School Size", size_categories)

    # Denomination filter
    denominations = ['All'] + sorted(df['denomination'].dropna().unique().tolist())
    selected_denomination = st.sidebar.selectbox("⛪ Denomination", denominations)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_province != 'All':
        filtered_df = filtered_df[filtered_df['province'] == selected_province]
    
    if education_levels:
        mask = filtered_df[education_levels].any(axis=1)
        filtered_df = filtered_df[mask]
    
    if selected_size != 'All':
        filtered_df = filtered_df[filtered_df['school_size_category'] == selected_size]
    
    if selected_denomination != 'All':
        filtered_df = filtered_df[filtered_df['denomination'] == selected_denomination]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏫 Total Schools", f"{len(filtered_df):,}")
    
    with col2:
        total_students = filtered_df['enrollment_total'].sum()
        st.metric("👥 Total Students", f"{total_students:,.0f}" if pd.notna(total_students) else "N/A")
    
    with col3:
        avg_size = filtered_df['enrollment_total'].mean()
        st.metric("📊 Avg School Size", f"{avg_size:,.0f}" if pd.notna(avg_size) else "N/A")
    
    with col4:
        with_websites = filtered_df['has_website'].sum()
        website_pct = (with_websites / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        st.metric("🌐 With Websites", f"{website_pct:.1f}%")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🗺️ Geographic", "🎓 Education", "📞 Contact", "🔍 School Finder"])
    
    with tab1:
        st.header("📊 Overview Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Province distribution
            province_counts = filtered_df['province'].value_counts()
            fig_province = px.bar(
                x=province_counts.values.tolist(),
                y=province_counts.index.tolist(),
                orientation='h',
                title="Schools by Province",
                labels={'x': 'Number of Schools', 'y': 'Province'}
            )
            fig_province.update_layout(height=400)
            st.plotly_chart(fig_province, width='stretch')

        with col2:
            # School size distribution
            size_counts = filtered_df['school_size_category'].value_counts()
            fig_size = px.pie(
                values=size_counts.values,
                names=size_counts.index,
                title="School Size Distribution"
            )
            st.plotly_chart(fig_size, width='stretch')

        # Education structure breakdown
        st.subheader("🎓 Education Structure Analysis")
        structure_counts = filtered_df['education_structure'].value_counts().head(10)
        fig_structure = px.bar(
            x=structure_counts.index,
            y=structure_counts.values,
            title="Top 10 Education Structures",
            labels={'x': 'Education Structure', 'y': 'Number of Schools'}
        )
        fig_structure.update_xaxes(tickangle=45)
        st.plotly_chart(fig_structure, width='stretch')
    
    with tab2:
        st.header("🗺️ Geographic Analysis")

        # Lightweight map inline
        try:
            # Filters in this tab
            colf1, colf2, colf3 = st.columns(3)
            with colf1:
                only_clients = st.toggle("Show only clients", value=False, key="map_only_clients")
            with colf2:
                provinces = ['All'] + (sorted(filtered_df['province'].dropna().unique().tolist()) if 'province' in filtered_df.columns else [])
                province_map = st.selectbox("Province", options=provinces, index=0, key="map_province")
            with colf3:
                search_map = st.text_input("Search (name or city)", key="map_search")

            map_data = filtered_df.copy()
            if province_map != 'All' and 'province' in map_data.columns:
                map_data = map_data[map_data['province'] == province_map]
            if search_map:
                mask = (
                    map_data['school_name'].str.contains(search_map, case=False, na=False)
                    | map_data['city'].str.contains(search_map, case=False, na=False)
                )
                map_data = map_data[mask]
            if only_clients and IS_CLIENT_COL in map_data.columns:
                map_data = map_data[map_data[IS_CLIENT_COL] == True]

            # Build and render
            m = build_map(map_data, only_clients=only_clients)
            if m is None:
                st.info("No data to display on the map.")
            else:
                st_folium(m, height=600)
        except Exception as e:
            st.warning(f"Map unavailable: {e}")

        st.divider()

        # Municipality analysis
        st.subheader("🏛️ Top Cities by School Count")
        city_counts = filtered_df['city'].value_counts().head(10)
        fig_cities = px.bar(
            x=city_counts.values,
            y=city_counts.index,
            orientation='h',
            title="Schools by City (Top 10)"
        )
        fig_cities.update_layout(height=400)
        st.plotly_chart(fig_cities, width='stretch')
    
    with tab3:
        st.header("🎓 Education Level Analysis")
        
        # Education level breakdown (relevant levels only)
        education_data = []
        for level in ['VMBO', 'HAVO', 'VWO']:
            if level in filtered_df.columns:
                count = filtered_df[level].sum()
                percentage = (count / len(filtered_df)) * 100 if len(filtered_df) else 0
                education_data.append({'Level': level, 'Schools': count, 'Percentage': f"{percentage:.1f}%"})

        education_df = pd.DataFrame(education_data)
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📚 Education Levels Offered")
            st.dataframe(education_df, width='stretch')
        
        with col2:
            fig_education = px.bar(
                education_df,
                x='Level',
                y='Schools',
                title="Schools Offering Each Education Level",
                color='Schools',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_education, width='stretch')
        
        # Comprehensive schools analysis
        st.subheader("🎯 Comprehensive Schools Analysis")
        relevant_cols = [c for c in ['VMBO', 'HAVO', 'VWO'] if c in filtered_df.columns]
        filtered_df['level_count'] = filtered_df[relevant_cols].sum(axis=1) if relevant_cols else 0
        comprehensive_stats = filtered_df.groupby('level_count').agg({
            'school_name': 'count',
            'enrollment_total': 'mean'
        }).round(0)
        comprehensive_stats.columns = ['Number of Schools', 'Average Enrollment']
        comprehensive_stats.index.name = 'Education Levels Offered'
        st.dataframe(comprehensive_stats)
    
    with tab4:
        st.header("📞 Contact Information Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Digital presence by province
            st.subheader("🌐 Digital Presence by Province")
            digital_stats = filtered_df.groupby('province').agg({
                'has_website': 'mean',
                'phone_formatted': lambda x: x.notna().mean()
            }).round(3) * 100
            digital_stats.columns = ['Website %', 'Phone %']
            st.dataframe(digital_stats)
        
        with col2:
            # Contact availability
            contact_data = {
                'Contact Type': ['Phone Numbers', 'Websites'],
                'Available': [
                    filtered_df['phone_formatted'].notna().sum(),
                    filtered_df['has_website'].sum()
                ],
                'Percentage': [
                    (filtered_df['phone_formatted'].notna().sum() / len(filtered_df)) * 100,
                    (filtered_df['has_website'].sum() / len(filtered_df)) * 100
                ]
            }
            contact_df = pd.DataFrame(contact_data)
            
            fig_contact = px.bar(
                contact_df,
                x='Contact Type',
                y='Percentage',
                title="Contact Information Availability",
                color='Percentage',
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig_contact, width='stretch')
    
    with tab5:
        st.header("🔍 School Finder & Clients")

        # Search functionality
        search_term = st.text_input("🔍 Search schools by name or city:")

        if search_term:
            search_results = filtered_df[
                filtered_df['school_name'].str.contains(search_term, case=False, na=False) |
                filtered_df['city'].str.contains(search_term, case=False, na=False)
            ]
        else:
            search_results = filtered_df.head(50)  # Show first 50 schools by default

        st.subheader(f"📋 Search Results ({len(search_results)} schools)")

        # Display results
        display_columns = [
            'school_name', 'city', 'province', 'levels_offered',
            'enrollment_total', 'school_size_category', 'phone_formatted', 'website'
        ]
        available_cols = [c for c in display_columns if c in search_results.columns]

        for _, row in search_results.reset_index(drop=True).iterrows():
            school_id = str(row.get('vestigings_id', ''))
            is_client = bool(row.get(IS_CLIENT_COL, False))
            cols = st.columns([4, 2, 2, 2, 2])
            with cols[0]:
                st.write(f"{row.get('school_name', '')} — {row.get('city', '')}")
            with cols[1]:
                st.write(f"ID: {school_id}")
            with cols[2]:
                st.write("Client" if is_client else "Not client")
            with cols[3]:
                if not is_client and st.button("Mark as client", key=f"add-{school_id}"):
                    toggle_client(filtered_df, school_id, True)
                    st.session_state["clients_version"] = st.session_state.get("clients_version", 0) + 1
                    st.rerun()
            with cols[4]:
                if is_client and st.button("Remove client", type="secondary", key=f"rm-{school_id}"):
                    toggle_client(filtered_df, school_id, False)
                    st.session_state["clients_version"] = st.session_state.get("clients_version", 0) + 1
                    st.rerun()

        # Also show a compact table if desired
        with st.expander("Show compact table"):
            if len(search_results) > 0 and available_cols:
                st.dataframe(
                    search_results[available_cols].reset_index(drop=True),
                    width='stretch',
                )
            else:
                st.info("No schools found matching your search criteria.")
    
    # Footer
    st.markdown("---")
    st.markdown("**Data Source:** DUO (Dienst Uitvoering Onderwijs) | **Dashboard created with:** Streamlit & Plotly")

if __name__ == "__main__":
    main()
