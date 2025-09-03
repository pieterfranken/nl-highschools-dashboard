#!/usr/bin/env python3
"""
🎯 Client Management Utility
Command-line tool to manage client schools data
"""

import json
import pandas as pd
from pathlib import Path

def load_client_data():
    """Load client data from file"""
    client_file = Path('client_schools.json')
    if client_file.exists():
        with open(client_file, 'r') as f:
            return set(json.load(f))
    return set()

def save_client_data(client_schools):
    """Save client data to file"""
    client_file = Path('client_schools.json')
    with open(client_file, 'w') as f:
        json.dump(list(client_schools), f, indent=2)

def load_schools_data():
    """Load schools dataset"""
    try:
        return pd.read_csv('nl_highschools_accurate_coordinates.csv')
    except FileNotFoundError:
        try:
            return pd.read_csv('nl_highschools_with_coordinates.csv')
        except FileNotFoundError:
            return pd.read_csv('nl_highschools_full.csv')

def main():
    print("🎯 Client Management Utility")
    print("=" * 40)
    
    # Load data
    client_schools = load_client_data()
    df = load_schools_data()
    
    print(f"📊 Total schools: {len(df):,}")
    print(f"🎯 Current clients: {len(client_schools)}")
    
    if client_schools:
        print("\n📋 Current Client Schools:")
        client_list = df[df['vestigings_id'].isin(client_schools)]
        for _, client in client_list.iterrows():
            print(f"  🎯 {client['school_name']} ({client['city']})")
            print(f"     ID: {client['vestigings_id']}")
        
        # Show client statistics
        total_students = client_list['enrollment_total'].sum()
        print(f"\n📊 Client Statistics:")
        print(f"  👥 Total students: {total_students:,.0f}" if pd.notna(total_students) else "  👥 Total students: N/A")
        print(f"  🏫 Number of clients: {len(client_schools)}")
        
        # Show by province
        if 'province' in client_list.columns:
            print(f"\n🌍 Clients by Province:")
            province_counts = client_list['province'].value_counts()
            for province, count in province_counts.items():
                print(f"  {province}: {count} schools")
    else:
        print("\n💡 No clients currently registered")
        print("   Use the interactive dashboard to add clients")
    
    print(f"\n💾 Client data file: client_schools.json")
    print(f"📱 Interactive dashboard: streamlit run app.py")

if __name__ == "__main__":
    main()
