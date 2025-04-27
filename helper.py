import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import re
import os

def geocode_address(geolocator, address, attempt=1, max_attempts=3):
    
    try:
        location = geolocator.geocode(address, timeout=10, country_codes=DEFAULT_COUNTRY_CODE)
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"  -> Geocoder returned None for: {address}")
            return (None, None)
     
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            print(f"Timeout geocoding '{address}', retrying ({attempt}/{max_attempts})...")
            time.sleep(2**attempt)
            return geocode_address(geolocator, address, attempt + 1) # Pass cleaned address in retry
        else:
            print(f"Failed to geocode '{address}' after {max_attempts} attempts (Timeout).")
            return (None, None)
    
    except GeocoderServiceError as e:
        print(f"Geocoding service error for '{address}': {e}")
        return (None, None)
    
    except Exception as e:
        print(f"An unexpected error occurred geocoding '{address}': {e}")
        return (None, None)

def lat_lon_finder(user_address_str):

    # Geocode the user's input address Ensure you have a unique user_agent string
    geolocator = Nominatim(user_agent="my_address_locator_app_v1_runtime_distinct") 
    print(f"Geocoding user address: {user_address_str}")

    # Assuming clean_and_format_address is defined elsewhere
    #user_address_cleaned = clean_and_format_address( user_address_str, DEFAULT_CITY, DEFAULT_STATE, DEFAULT_COUNTRY )
    #print(f"  -> Cleaned user address: {user_address_cleaned}")

    user_lat, user_lon = geocode_address(geolocator, user_address_str) 

    if user_lat is None or user_lon is None:
        print(f"Could not geocode the user address: '{user_address_str}'")
        return (None, None)

    return (user_lat, user_lon)

def dist_cal(lat, lon, df):

    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    all_distances = []

    for index, row in df.iterrows():

        if pd.isna(row['Processed_For_Geocoding']):
            continue

        distance_km = geodesic((lat, lon), 
                                (row['Latitude'], row['Longitude'])
                                ).km

        all_distances.append((
                            distance_km, 
                            str(row['Processed_For_Geocoding'])
                            ))

    return  all_distances.sort(key=lambda x: x[0])