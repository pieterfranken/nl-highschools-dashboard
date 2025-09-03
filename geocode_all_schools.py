#!/usr/bin/env python3
"""
🌍 Complete Accurate Geocoding for All Dutch Schools
Geocodes all 1,620 schools with street-level precision
"""

import pandas as pd
import requests
import time
import json
from pathlib import Path
from datetime import datetime

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

def main():
    print("🌍 Complete Accurate Geocoding for All Dutch Schools")
    print("=" * 60)
    
    start_time = datetime.now()
    
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
    
    # Load existing progress if available
    progress_file = Path('nl_highschools_accurate_coordinates.csv')
    if progress_file.exists():
        df_existing = pd.read_csv(progress_file)
        # Merge existing coordinates
        for idx, row in df_existing.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                df.at[idx, 'latitude'] = row['latitude']
                df.at[idx, 'longitude'] = row['longitude']
        print(f"📋 Loaded existing progress with coordinates")
    else:
        # Add coordinate columns if they don't exist
        if 'latitude' not in df.columns:
            df['latitude'] = None
        if 'longitude' not in df.columns:
            df['longitude'] = None
    
    # Create full addresses
    df['full_address'] = df.apply(create_full_address, axis=1)
    
    # Count schools that need geocoding
    needs_geocoding = df[(df['latitude'].isna()) | (df['longitude'].isna())]
    total_to_geocode = len(needs_geocoding)
    already_geocoded = len(df) - total_to_geocode
    
    print(f"✅ Already geocoded: {already_geocoded:,} schools")
    print(f"🔍 Need to geocode: {total_to_geocode:,} schools")
    
    if total_to_geocode == 0:
        print("🎉 All schools already have coordinates!")
        return
    
    # Estimate time
    estimated_minutes = (total_to_geocode * 1.2) / 60  # 1.2 seconds per request
    print(f"⏱️  Estimated time: {estimated_minutes:.1f} minutes")
    print(f"🚀 Starting geocoding at {start_time.strftime('%H:%M:%S')}")
    print("=" * 60)
    
    geocoded_count = 0
    failed_count = 0
    
    for idx, row in df.iterrows():
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            address = row['full_address']
            
            coords = geocode_with_nominatim(address, cache)
            
            if coords:
                df.at[idx, 'latitude'] = coords[0]
                df.at[idx, 'longitude'] = coords[1]
                geocoded_count += 1
                
                # Progress indicator
                if geocoded_count % 25 == 0:
                    elapsed = datetime.now() - start_time
                    remaining = total_to_geocode - geocoded_count
                    eta_seconds = (elapsed.total_seconds() / geocoded_count) * remaining
                    eta_minutes = eta_seconds / 60
                    
                    print(f"✅ {geocoded_count:4d}/{total_to_geocode} ({geocoded_count/total_to_geocode*100:5.1f}%) | "
                          f"ETA: {eta_minutes:4.1f}m | "
                          f"Latest: {row['school_name'][:40]:<40}")
                
                # Save progress every 50 schools
                if geocoded_count % 50 == 0:
                    df_output = df.drop('full_address', axis=1)
                    df_output.to_csv('nl_highschools_accurate_coordinates.csv', index=False)
                    with open(cache_file, 'w') as f:
                        json.dump(cache, f)
                    print(f"💾 Progress saved at {geocoded_count} schools")
            else:
                failed_count += 1
                if failed_count <= 10:  # Only show first 10 failures
                    print(f"❌ Failed: {row['school_name'][:50]} - {address}")
            
            # Rate limiting - be respectful to the API
            time.sleep(1.2)
    
    # Save final results
    with open(cache_file, 'w') as f:
        json.dump(cache, f)
    
    df_output = df.drop('full_address', axis=1)
    df_output.to_csv('nl_highschools_accurate_coordinates.csv', index=False)
    
    # Final statistics
    end_time = datetime.now()
    duration = end_time - start_time
    
    with_coords = df_output[(df_output['latitude'].notna()) & (df_output['longitude'].notna())]
    
    print("\n" + "=" * 60)
    print("🎉 COMPLETE GEOCODING RESULTS")
    print("=" * 60)
    print(f"✅ Total schools with coordinates: {len(with_coords):,}/{len(df):,} ({len(with_coords)/len(df)*100:.1f}%)")
    print(f"🆕 Newly geocoded in this session: {geocoded_count:,}")
    print(f"❌ Failed to geocode: {failed_count:,}")
    print(f"⏱️  Total time: {duration}")
    print(f"💾 Saved to: nl_highschools_accurate_coordinates.csv")
    print(f"📋 Cache size: {len(cache):,} addresses")
    
    # Show some examples of accurately geocoded schools
    print(f"\n📍 SAMPLE ACCURATE COORDINATES:")
    sample = with_coords[['school_name', 'street', 'city', 'latitude', 'longitude']].head(10)
    for _, row in sample.iterrows():
        print(f"  🏫 {row['school_name'][:50]:<50}")
        print(f"     📍 {row['street']}, {row['city']}")
        print(f"     🗺️  {row['latitude']:.6f}, {row['longitude']:.6f}")
        print()
    
    print("🎯 Ready for interactive mapping with accurate school locations!")

if __name__ == "__main__":
    main()
