#!/usr/bin/env python3
"""
🎯 Accurate Geocoding for Dutch Schools
Uses full addresses (street + house number + postcode + city) for precise locations
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
        # Use Nominatim API directly
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'nl',  # Limit to Netherlands
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
            street_part += f" {str(row['house_no']).strip()}"
            if pd.notna(row['house_add']):
                street_part += str(row['house_add']).strip()
        parts.append(street_part)
    
    # Postcode and city
    if pd.notna(row['postcode']):
        parts.append(str(row['postcode']).strip())
    
    if pd.notna(row['city']):
        parts.append(str(row['city']).strip())
    
    # Always add Netherlands
    parts.append("Netherlands")
    
    return ", ".join(parts)

def main():
    print("🎯 Accurate Geocoding for Dutch Schools")
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
    
    # Show sample addresses
    print("\n📍 Sample addresses to geocode:")
    for i, addr in enumerate(df['full_address'].head(5)):
        print(f"  {i+1}. {addr}")
    
    # Geocode schools that don't have coordinates
    geocoded_count = 0
    total_to_geocode = df[(df['latitude'].isna()) | (df['longitude'].isna())].shape[0]
    
    print(f"\n🔍 Need to geocode {total_to_geocode} schools")
    print("⏳ This may take a while due to rate limiting...")
    
    for idx, row in df.iterrows():
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            address = row['full_address']
            
            coords = geocode_with_nominatim(address, cache)
            
            if coords:
                df.at[idx, 'latitude'] = coords[0]
                df.at[idx, 'longitude'] = coords[1]
                geocoded_count += 1
                
                if geocoded_count % 5 == 0:
                    print(f"✅ Geocoded {geocoded_count}/{total_to_geocode} schools")
                    # Save cache periodically
                    with open(cache_file, 'w') as f:
                        json.dump(cache, f)
            else:
                print(f"❌ Failed to geocode: {row['school_name']} - {address}")
            
            # Rate limiting - be respectful to the API
            time.sleep(1.5)  # 1.5 seconds between requests
    
    # Save final cache
    with open(cache_file, 'w') as f:
        json.dump(cache, f)
    
    # Save updated dataset
    df_output = df.drop('full_address', axis=1)  # Remove the temporary address column
    df_output.to_csv('nl_highschools_accurate_coordinates.csv', index=False)
    
    # Statistics
    with_coords = df_output[(df_output['latitude'].notna()) & (df_output['longitude'].notna())]
    print(f"\n📊 ACCURATE GEOCODING RESULTS:")
    print(f"✅ Schools with coordinates: {len(with_coords):,}/{len(df):,} ({len(with_coords)/len(df)*100:.1f}%)")
    print(f"🆕 Newly geocoded: {geocoded_count:,}")
    print(f"💾 Saved to: nl_highschools_accurate_coordinates.csv")
    
    # Show sample coordinates with addresses
    print(f"\n📍 SAMPLE ACCURATE COORDINATES:")
    sample = with_coords[['school_name', 'street', 'city', 'latitude', 'longitude']].head(5)
    for _, row in sample.iterrows():
        print(f"  {row['school_name'][:40]:<40}")
        print(f"    📍 {row['street']}, {row['city']}")
        print(f"    🗺️  {row['latitude']:.6f}, {row['longitude']:.6f}")
        print()

if __name__ == "__main__":
    main()
