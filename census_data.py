# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:33:18 2026

@author: Hana
"""
import requests
import streamlit as st

CENSUS_API_KEY = st.secrets["CENSUS_API_KEY"]

def get_closest_acs_year(year):
    # ACS 5-year datasets availability
    if year <= 2014:
        return 2014
    elif year <= 2019:
        return 2019
    else:
        return 2022

# -------------------------------------------------
# ACS DATA (income, home value, poverty, race)
# -------------------------------------------------
def get_census_data(block_group, year):

    state = block_group[:2]
    county = block_group[2:5]
    tract = block_group[5:11]
    bg = block_group[11]

    acs_year = get_closest_acs_year(year)
    base_url = f"https://api.census.gov/data/{acs_year}/acs/acs5"

    # ------------------------
    # COUNTY DATA
    # ------------------------
    county_vars = ",".join([
    "B19013_001E",  # median household income
    "B25077_001E",  # median home value
    "B17010_001E",  # total families
    "B17010_002E",  # families below poverty
    "B02001_001E",  # total population
    "B02001_003E",  # black population alone
    "B25035_001E"   # median year structure built
    ])

    county_url = (
        f"{base_url}?get={county_vars}"
        f"&for=county:{county}&in=state:{state}"
        f"&key={CENSUS_API_KEY}"
    )

    #county_data = requests.get(county_url).json()

    #county_median_income = float(county_data[1][0])
    #county_home_value = float(county_data[1][1])
    
    response = requests.get(county_url)
    county_data = response.json()
    row = county_data[1]

    county_median_income = float(row[0])
    county_home_value = float(row[1])
    
    county_total_families = float(row[2])
    county_families_poverty = float(row[3])
    
    county_total_population = float(row[4])
    county_black_population = float(row[5])
    
    county_median_year_built = float(row[6])
    
    county_family_poverty_rate = (
        county_families_poverty / county_total_families
        if county_total_families > 0 else None
    )
    
    county_prop_black = (
        county_black_population / county_total_population
        if county_total_population > 0 else None
    )

    # ------------------------
    # BLOCK GROUP DATA
    # ------------------------
    # also need to get CBG income, default home value, default year built
    bg_vars = "B02001_001E,B02001_003E,B17010_001E,B17010_002E"

    bg_url = (
        f"{base_url}?get={bg_vars}"
        f"&for=block%20group:{bg}"
        f"&in=state:{state}%20county:{county}%20tract:{tract}"
        f"&key={CENSUS_API_KEY}"
    )   

    bg_data = requests.get(bg_url).json()

    cbg_total_pop = float(bg_data[1][0])
    cbg_black_pop = float(bg_data[1][1])
    cbg_total_fam = float(bg_data[1][2])
    cbg_poverty_fam = float(bg_data[1][3])

    # ------------------------
    # Derived variables
    # ------------------------
    cbg_prop_black = cbg_black_pop / cbg_total_pop if cbg_total_pop > 0 else 0
    cbg_fam_poverty_rate = cbg_poverty_fam / cbg_total_fam if cbg_total_fam > 0 else 0

    # also need to get CBG income, default home value, default year built
    return {
        "county_median_income": county_median_income,
        "county_median_home_value": county_home_value,
        "county_median_year_built": county_median_year_built,
        "county_family_poverty_rate": county_family_poverty_rate*100,
        "county_prop_black": county_prop_black,
        "bg_family_poverty": cbg_fam_poverty_rate*100,
        "bg_prop_black": cbg_prop_black
    }


# -------------------------------------------------
# Main interface used by app.py
# -------------------------------------------------
def get_demographic_data(block_group, year):
    """
    Returns tuple matching existing app expectations:
    (county_income, county_home_value, county_year_built, county_poverty, county_prop_black, bg_poverty_rate, bg_prop_black)
    """

    data = get_census_data(block_group, year)

    return (
        data["county_median_income"],
        data["county_median_home_value"],
        data["county_median_year_built"],
        data["county_family_poverty_rate"],
        data["county_prop_black"],
        data["bg_family_poverty"],
        data["bg_prop_black"]
    )