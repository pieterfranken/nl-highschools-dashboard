#!/usr/bin/env python3
"""
🎯 Batch Accurate Geocoding for Dutch Schools
Geocodes schools in batches with proper rate limiting
"""

import pandas as pd
import requests
import time
import json
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
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
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

def create_full_address(row):
    """Create a full address string for geocoding"""
    parts = []
    
    # Street and house number
    if pd.notna(row['street']):
        street_part = str(row['street']).strip()
        if pd.notna(row['house_no']):
            house_no = str(row['house_no']).strip()
            if house_no != 'nan':
                street_part += f" {house_no}"
                if pd.notna(row['house_add']):
                    house_add = str(row['house_add']).strip()
                    if house_add != 'nan':
                        street_part += house_add
        parts.append(street_part)
    
    # Postcode and city
    if pd.notna(row['postcode']):
        parts.append(str(row['postcode']).strip())
    
    if pd.notna(row['city']):
        parts.append(str(row['city']).strip())
    
    parts.append("Netherlands")
    
    return ", ".join(parts)

def main():
    print("🎯 Batch Accurate Geocoding for Dutch Schools")
    print("=" * 50)
    
    # Load dataset
    df = pd.read_csv('nl_highschools_full.csv')
    print(f"📊 Loaded {len(df):,} schools")
    
    # Load existing cache
    cache_file = Path('accurate_geocoding_cache.json')
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        print(f"📋 Loaded {len(cache)} cached coordinates")
    else:
        cache = {}
    
    # Add coordinate columns if they don't exist
    if 'latitude' not in df.columns:
        df['latitude'] = None
    if 'longitude' not in df.columns:
        df['longitude'] = None
    
    # Create full addresses
    df['full_address'] = df.apply(create_full_address, axis=1)
    
    # Limit to first 100 schools for this batch
    batch_size = 100
    df_batch = df.head(batch_size).copy()
    
    print(f"\n🔍 Geocoding first {batch_size} schools...")
    print("⏳ This will take about 3-4 minutes due to rate limiting...")
    
    geocoded_count = 0
    
    for idx, row in df_batch.iterrows():
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            address = row['full_address']
            
            coords = geocode_with_nominatim(address, cache)
            
            if coords:
                df.at[idx, 'latitude'] = coords[0]
                df.at[idx, 'longitude'] = coords[1]
                geocoded_count += 1
                print(f"✅ {geocoded_count:3d}/100 - {row['school_name'][:50]:<50} | {coords[0]:.6f}, {coords[1]:.6f}")
            else:
                print(f"❌ {geocoded_count:3d}/100 - Failed: {row['school_name'][:50]}")
            
            # Save cache every 10 schools
            if geocoded_count % 10 == 0:
                with open(cache_file, 'w') as f:
                    json.dump(cache, f)
            
            # Rate limiting - be respectful to the API
            time.sleep(1.2)
    
    # Save final cache
    with open(cache_file, 'w') as f:
        json.dump(cache, f)
    
    # Save updated dataset
    df_output = df.drop('full_address', axis=1)
    df_output.to_csv('nl_highschools_accurate_coordinates.csv', index=False)
    
    # Statistics
    with_coords = df_output[(df_output['latitude'].notna()) & (df_output['longitude'].notna())]
    print(f"\n📊 BATCH GEOCODING RESULTS:")
    print(f"✅ Schools with coordinates: {len(with_coords):,}/{len(df):,} ({len(with_coords)/len(df)*100:.1f}%)")
    print(f"🆕 Newly geocoded in this batch: {geocoded_count:,}")
    print(f"💾 Saved to: nl_highschools_accurate_coordinates.csv")
    
    print(f"\n🎯 Van Maerlant schools with accurate coordinates:")
    van_maerlant = with_coords[with_coords['school_name'].str.contains('Van Maerlant', case=False, na=False)]
    for _, school in van_maerlant.iterrows():
        print(f"  📍 {school['school_name']} - {school['street']}, {school['city']}")
        print(f"     🗺️  {school['latitude']:.6f}, {school['longitude']:.6f}")

if __name__ == "__main__":
    main()
