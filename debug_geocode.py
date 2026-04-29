# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 15:57:46 2026

@author: htchmiel
"""

from geocode_utils import get_coordinates, get_block_group

# ---- TEST INPUT ----
street = "123 Main St"
city = "Raleigh"
state = "NC"
zip_code = "27601"
year = 2014

# ---- STEP 1: Get coordinates ----
lat, lon = get_coordinates(street, city, state, zip_code)

print("LAT/LON:", lat, lon)

if lat is None:
    print("❌ Failed at geocoding step")
    exit()

# ---- STEP 2: Get block group ----
county, tract, block_group = get_block_group(lat, lon, year)

print("COUNTY:", county)
print("TRACT:", tract)
print("BLOCK GROUP:", block_group)

if block_group is None:
    print("❌ Failed at block group step")
else:
    print("✅ Success")