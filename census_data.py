# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:33:18 2026

@author: Hana
"""
import requests

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
    county_vars = "B19013_001E,B25077_001E"

    county_url = (
        f"{base_url}?get={county_vars}"
        f"&for=county:{county}&in=state:{state}"
    )

    county_data = requests.get(county_url).json()

    county_median_income = float(county_data[1][0])
    county_home_value = float(county_data[1][1])

    # ------------------------
    # BLOCK GROUP DATA
    # ------------------------
    # also need to get CBG income, default home value, default year built
    bg_vars = "B02001_001E,B02001_003E,B17010_001E,B17010_002E"

    bg_url = (
        f"{base_url}?get={bg_vars}"
        f"&for=block%20group:{bg}"
        f"&in=state:{state}%20county:{county}%20tract:{tract}"
    )
    print(bg_url)
    bg_data = requests.get(bg_url).json()

    total_pop = float(bg_data[1][0])
    black_pop = float(bg_data[1][1])
    total_fam = float(bg_data[1][2])
    poverty_fam = float(bg_data[1][3])

    # ------------------------
    # Derived variables
    # ------------------------
    prop_black = black_pop / total_pop if total_pop > 0 else 0
    fam_poverty_rate = poverty_fam / total_fam if total_fam > 0 else 0

    # also need to get CBG income, default home value, default year built
    return {
        "county_median_income": county_median_income,
        "county_median_home_value": county_home_value,
        "bg_family_poverty": fam_poverty_rate,
        "bg_prop_black": prop_black
    }


# -------------------------------------------------
# Main interface used by app.py
# -------------------------------------------------
def get_demographic_data(block_group, year):
    """
    Returns tuple matching existing app expectations:
    (county_income, county_home_value, poverty_rate, prop_black)
    """

    data = get_census_data(block_group, year)

    return (
        data["county_median_income"],
        data["county_median_home_value"],
        data["bg_family_poverty"],
        data["bg_prop_black"]
    )