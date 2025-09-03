#!/usr/bin/env python3
"""
🎯 Enhanced Geocoding with Fallback for Failed Schools
Uses exact addresses first, then falls back to city/postcode for failed schools
"""

import pandas as pd
import requests
import time
import json
import numpy as np
from pathlib import Path

def geocode_with_nominatim(address, cache):
    """Geocode using Nominatim (OpenStreetMap) API"""
    if address in cache:
        return cache[address]
    
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
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                result = (float(data[0]['lat']), float(data[0]['lon']))
                cache[address] = result
                return result
        
        cache[address] = None
        return None
        
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        cache[address] = None
        return None

def geocode_fallback(postcode, city, cache):
    """Fallback geocoding using just postcode and city"""
    fallback_address = f"{postcode}, {city}, Netherlands"
    
    if fallback_address in cache:
        return cache[fallback_address]
    
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': fallback_address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'nl'
        }
        
        headers = {
            'User-Agent': 'nl-highschools-dashboard/1.0 (educational research)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                # Add small random offset so schools don't overlap exactly
                lat = float(data[0]['lat']) + np.random.uniform(-0.002, 0.002)
                lon = float(data[0]['lon']) + np.random.uniform(-0.002, 0.002)
                result = (lat, lon)
                cache[fallback_address] = result
                return result
        
        cache[fallback_address] = None
        return None
        
    except Exception as e:
        print(f"Error in fallback geocoding {fallback_address}: {e}")
        cache[fallback_address] = None
        return None

def create_full_address(row):
    """Create a full address string for geocoding"""
    parts = []
    
    # Street and house number
    if pd.notna(row['street']):
        street_part = str(row['street']).strip()
        if pd.notna(row['house_no']):
            house_no = str(row['house_no']).strip()
            if house_no != 'nan' and house_no != '':
                street_part += f" {house_no}"
                if pd.notna(row['house_add']):
                    house_add = str(row['house_add']).strip()
                    if house_add != 'nan' and house_add != '':
                        street_part += house_add
        parts.append(street_part)
    
    # Postcode and city
    if pd.notna(row['postcode']):
        parts.append(str(row['postcode']).strip())
    
    if pd.notna(row['city']):
        parts.append(str(row['city']).strip())
    
    parts.append("Netherlands")
    
    return ", ".join(parts)

def process_failed_schools():
    """Process schools that failed in the main geocoding run"""
    print("🔄 Processing Failed Schools with Fallback Geocoding")
    print("=" * 60)
    
    # Load the current dataset
    df = pd.read_csv('nl_highschools_accurate_coordinates.csv')
    
    # Load cache
    cache_file = Path('accurate_geocoding_cache.json')
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            cache = json.load(f)
    else:
        cache = {}
    
    # Find schools without coordinates
    failed_schools = df[(df['latitude'].isna()) | (df['longitude'].isna())].copy()
    
    print(f"📊 Found {len(failed_schools)} schools without coordinates")
    print("🎯 Attempting fallback geocoding using postcode + city...")
    
    fallback_success = 0
    
    for idx, row in failed_schools.iterrows():
        postcode = str(row['postcode']).strip() if pd.notna(row['postcode']) else ''
        city = str(row['city']).strip() if pd.notna(row['city']) else ''
        
        if postcode and city:
            coords = geocode_fallback(postcode, city, cache)
            
            if coords:
                df.at[idx, 'latitude'] = coords[0]
                df.at[idx, 'longitude'] = coords[1]
                fallback_success += 1
                print(f"✅ Fallback: {row['school_name'][:50]:<50} | {coords[0]:.6f}, {coords[1]:.6f}")
            else:
                print(f"❌ Failed fallback: {row['school_name'][:50]}")
        else:
            print(f"❌ No postcode/city: {row['school_name'][:50]}")
        
        time.sleep(1.0)  # Rate limiting
    
    # Save updated dataset
    df.to_csv('nl_highschools_accurate_coordinates.csv', index=False)
    
    # Save cache
    with open(cache_file, 'w') as f:
        json.dump(cache, f)
    
    # Final statistics
    with_coords = df[(df['latitude'].notna()) & (df['longitude'].notna())]
    
    print(f"\n📊 FALLBACK GEOCODING RESULTS:")
    print(f"✅ Fallback successes: {fallback_success}/{len(failed_schools)}")
    print(f"✅ Total schools with coordinates: {len(with_coords):,}/{len(df):,} ({len(with_coords)/len(df)*100:.1f}%)")
    print(f"💾 Updated dataset saved")
    
    return len(with_coords), len(df)

if __name__ == "__main__":
    process_failed_schools()
