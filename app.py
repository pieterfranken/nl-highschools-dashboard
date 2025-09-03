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

@st.cache_data
def load_data():
    """Load and cache the schools dataset"""
    try:
        df = pd.read_csv('nl_highschools_full.csv')
        # Optimize memory usage for cloud deployment
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype('string')
        return df
    except FileNotFoundError:
        st.error("❌ Dataset file 'nl_highschools_full.csv' not found.")
        st.info("💡 If you're running this locally, please run: `python build_nl_highschools_dataset.py`")
        st.stop()
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
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters & Options")
    
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
        
        # Map would go here (simplified for now due to coordinate requirements)
        st.info("🗺️ Interactive map feature would require geocoding coordinates for each school address.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Vacation region analysis
            vacation_stats = filtered_df.groupby('vacation_region').agg({
                'school_name': 'count',
                'enrollment_total': 'mean'
            }).round(0)
            vacation_stats.columns = ['Schools', 'Avg Enrollment']
            st.subheader("🏖️ By Vacation Region")
            st.dataframe(vacation_stats)
        
        with col2:
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
        st.header("🔍 School Finder")
        
        # Search functionality
        search_term = st.text_input("🔍 Search schools by name or city:")
        
        if search_term:
            search_results = filtered_df[
                filtered_df['school_name'].str.contains(search_term, case=False, na=False) |
                filtered_df['city'].str.contains(search_term, case=False, na=False)
            ]
        else:
            search_results = filtered_df.head(20)  # Show first 20 schools by default
        
        st.subheader(f"📋 Search Results ({len(search_results)} schools)")
        
        # Display results
        display_columns = [
            'school_name', 'city', 'province', 'levels_offered', 
            'enrollment_total', 'school_size_category', 'phone_formatted', 'website'
        ]
        
        if len(search_results) > 0:
            st.dataframe(
                search_results[display_columns].reset_index(drop=True),
                width='stretch',
                column_config={
                    'school_name': 'School Name',
                    'city': 'City',
                    'province': 'Province',
                    'levels_offered': 'Education Levels',
                    'enrollment_total': st.column_config.NumberColumn('Students', format="%.0f"),
                    'school_size_category': 'Size Category',
                    'phone_formatted': 'Phone',
                    'website': st.column_config.LinkColumn('Website')
                }
            )
        else:
            st.info("No schools found matching your search criteria.")
    
    # Footer
    st.markdown("---")
    st.markdown("**Data Source:** DUO (Dienst Uitvoering Onderwijs) | **Dashboard created with:** Streamlit & Plotly")

if __name__ == "__main__":
    main()
