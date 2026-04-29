# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 14:48:12 2026

@author: Hana
"""
import requests

def get_coordinates(street, city, state, zip_code):

    address = f"{street}, {city}, {state} {zip_code}"

    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }

    r = requests.get(url, params=params)
    data = r.json()

    try:
        match = data["result"]["addressMatches"][0]

        lat = match["coordinates"]["y"]
        lon = match["coordinates"]["x"]

        return lat, lon

    except:
        return None, None
    

# -------------------------------------------------
# Helper: Determine correct Census vintage
# -------------------------------------------------
def get_census_vintage(year):
    """
    Select appropriate Census geography vintage

    - Pre-2020 → 2010 Census geography
    - 2020+ → Current (2020 Census)
    """

    if year < 2020:
        return "Census2010_Current"
    else:
        return "Current_Current"


# -------------------------------------------------
# Coordinates → Block Group
# -------------------------------------------------
def get_block_group(lat, lon, year):
    """
    Returns (county, tract, block_group GEOID)

    Uses year-aware census geography
    """

    vintage = get_census_vintage(year)

    url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"

    params = {
        "x": lon,
        "y": lat,
        "benchmark": "Public_AR_Current",
        "vintage": vintage,
        "format": "json"
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()

        # Handle both 2010 and 2020 structures safely
        geographies = data["result"]["geographies"]

        # Try common keys in order of likelihood
        geo_key_options = [
            "Census Blocks",
            "2020 Census Blocks",
            list(geographies.keys())[0]  # fallback
        ]

        geo = None
        for key in geo_key_options:
            if key in geographies:
                geo = geographies[key][0]
                break

        if geo is None:
            return None, None, None

        block_group = geo["GEOID"][:12]
        county = geo["COUNTY"]
        tract = geo["TRACT"]

        return county, tract, block_group

    except (KeyError, IndexError, requests.RequestException):
        return None, None, None