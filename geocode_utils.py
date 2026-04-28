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
    

def get_block_group(lat, lon):

    url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"

    params = {
        "x": lon,
        "y": lat,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }

    r = requests.get(url, params=params)
    data = r.json()

    try:
        geo = data["result"]["geographies"]["2020 Census Blocks"][0]

        block_group = geo["GEOID"][:12]
        county = geo["COUNTY"]
        tract = geo["TRACT"]

        return county,tract,block_group

    except:
        return None,None,None