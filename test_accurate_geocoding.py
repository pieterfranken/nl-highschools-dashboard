#!/usr/bin/env python3
"""
🧪 Test Accurate Geocoding for a Few Schools
Test the geocoding with Van Maerlant Lyceum and a few other schools
"""

import pandas as pd
import requests
import time
import json

def geocode_with_nominatim(address):
    """Geocode using Nominatim (OpenStreetMap) API"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'nl',
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'nl-highschools-dashboard/1.0 (educational research)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                result = (float(data[0]['lat']), float(data[0]['lon']))
                return result, data[0].get('display_name', '')
        
        return None, None
        
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None, None

def create_full_address(row):
    """Create a full address string for geocoding"""
    parts = []
    
    # Street and house number
    if pd.notna(row['street']):
        street_part = str(row['street']).strip()
        if pd.notna(row['house_no']):
            street_part += f" {str(row['house_no']).strip()}"
            if pd.notna(row['house_add']):
                street_part += str(row['house_add']).strip()
        parts.append(street_part)
    
    # Postcode and city
    if pd.notna(row['postcode']):
        parts.append(str(row['postcode']).strip())
    
    if pd.notna(row['city']):
        parts.append(str(row['city']).strip())
    
    parts.append("Netherlands")
    
    return ", ".join(parts)

def main():
    print("🧪 Testing Accurate Geocoding")
    print("=" * 40)
    
    # Load dataset
    df = pd.read_csv('nl_highschools_full.csv')
    
    # Find Van Maerlant Lyceum
    van_maerlant = df[df['school_name'].str.contains('Van Maerlant', case=False, na=False)]
    
    if len(van_maerlant) > 0:
        print("🎯 Found Van Maerlant schools:")
        for _, school in van_maerlant.iterrows():
            print(f"  - {school['school_name']} in {school['city']}")
            print(f"    Address: {school['street']} {school['house_no']}, {school['postcode']} {school['city']}")
            
            # Create full address
            full_address = create_full_address(school)
            print(f"    Full address for geocoding: {full_address}")
            
            # Geocode
            coords, display_name = geocode_with_nominatim(full_address)
            
            if coords:
                print(f"    ✅ Coordinates: {coords[0]:.6f}, {coords[1]:.6f}")
                print(f"    📍 Found location: {display_name}")
            else:
                print(f"    ❌ Could not geocode this address")
            
            print()
            time.sleep(2)  # Rate limiting
    
    # Test a few more schools from different cities
    print("\n🧪 Testing other schools:")
    test_schools = df.head(3)
    
    for _, school in test_schools.iterrows():
        print(f"\n🏫 {school['school_name']}")
        print(f"   📍 {school['city']}")
        
        full_address = create_full_address(school)
        print(f"   🔍 Geocoding: {full_address}")
        
        coords, display_name = geocode_with_nominatim(full_address)
        
        if coords:
            print(f"   ✅ Coordinates: {coords[0]:.6f}, {coords[1]:.6f}")
            print(f"   📍 Found: {display_name}")
        else:
            print(f"   ❌ Could not geocode")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
