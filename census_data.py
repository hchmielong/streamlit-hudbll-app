# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:33:18 2026

@author: Hana
"""
import requests

# uses 2020 decennial data
def get_race_data(block_group):

    state = block_group[:2]
    county = block_group[2:5]
    tract = block_group[5:11]
    bg = block_group[11]

    url = (
        "https://api.census.gov/data/2020/dec/pl?"
        "get=P2_001N,P2_006N"
        f"&for=block%20group:{bg}"
        f"&in=state:{state}%20county:{county}%20tract:{tract}"
    )

    r = requests.get(url)
    data = r.json()

    total_pop = float(data[1][0])
    black_pop = float(data[1][1])

    prop_black = black_pop / total_pop if total_pop > 0 else 0

    return prop_black

# uses 2022 acs data - change to 2020
def get_census_data(block_group):

    state = block_group[:2]
    county = block_group[2:5]
    tract = block_group[5:11]
    bg = block_group[11]

    # ------------------------
    # COUNTY DATA
    # ------------------------

    county_vars = "B19013_001E,B25077_001E"
    
    county_url = (
    f"https://api.census.gov/data/2022/acs/acs5?"
    f"get={county_vars}&for=county:{county}&in=state:{state}"
    )
    
    county_data = requests.get(county_url).json()
    
    county_median_income = float(county_data[1][0])
    county_home_value = float(county_data[1][1])
    
    # ------------------------
    # BLOCK GROUP DATA
    # ------------------------
    
    bg_vars = "B02001_001E,B02001_003E,B17010_001E,B17010_002E"

    bg_url = (
        f"https://api.census.gov/data/2022/acs/acs5?"
        f"get={bg_vars}"
        f"&for=block%20group:{bg}"
        f"&in=state:{state}%20county:{county}%20tract:{tract}"
    )
    
    bg_data = requests.get(bg_url).json()
    
    total_pop = float(bg_data[1][0])
    #black_pop = float(bg_data[1][1])
    total_fam = float(bg_data[1][2])
    poverty_fam = float(bg_data[1][3])
    
    # ------------------------
    # Derived variables
    # ------------------------
    
    #prop_black = black_pop / total_pop if total_pop > 0 else 0
    fam_poverty_rate = poverty_fam / total_fam if total_fam > 0 else 0
    
    return {
        "county_median_income": county_median_income,
        "county_median_home_value": county_home_value,
        #"bg_prop_black": prop_black,
        "bg_family_poverty": fam_poverty_rate
    }


def get_demographic_data(block_group):
    acs_data = get_census_data(block_group)
    prop_black = get_race_data(block_group)
    return acs_data['county_median_income'],acs_data['county_median_home_value'],acs_data['bg_family_poverty'],prop_black