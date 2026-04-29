# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 09:40:39 2026

@author: Hana
"""

import streamlit as st
from hudbll_backend import run_model
from geocode_utils import get_coordinates, get_block_group
from census_data import get_demographic_data

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Home & Water Risk Tool",
    layout="centered"
)

st.title("🏠 Household Blood-Lead Level Risk Calculation Tool")
st.write(
    "Enter the information below to generate an example model assessment."
)

st.subheader("Child Information")

child_present = st.radio(
    "Did a child under age 6 live in the home between 2002–2019?",
    options=[False, True],
    format_func=lambda x: "Yes" if x else "No"
)

# Defaults
test_year = 2020
child_age_months = 14
specimen_type = 0  # C = capillary, V = venous

if child_present:

    blood_test = st.radio(
        "Did the child receive a blood lead test during those years?",
        options=[False, True],
        format_func=lambda x: "Yes" if x else "No"
    )

    # Year selection (always allow)
    test_year = st.selectbox(
        "Year of residence / test",
        list(range(2002, 2021)),
        index=len(list(range(2002, 2021))) - 1  # default 2020
    )

    child_age_months = st.selectbox(
        "Child age in months during that year",
        list(range(0, 73)),
        index=14
    )

    if blood_test:
        specimen_type = st.radio(
            "Blood specimen type",
            options=["Capillary", "Venous"],
            index=0
        )

        specimen_type = "C" if specimen_type == "Capillary" else "V"
        if specimen_type == "C":
            specimen_type = 0
        else:
            specimen_type = 1

st.divider()

# -------------------------------------------------
# User inputs
# -------------------------------------------------

street = st.text_input("Street Address")
city = st.text_input("City")
state = st.text_input("State")
zip_code = st.text_input("ZIP Code")

year_built = st.selectbox(
    "Year home was built",
    [
        "Before 1950",
        "1950–1969",
        "1970–1989",
        "1990–2009",
        "2010 or later"
    ]
)
if year_built == "Before 1950":
    year_built = 1940
if year_built == "1950–1969":
    year_built = 1960
if year_built == "1970–1989":
    year_built = 1980
if year_built == "1990–2009":
    year_built = 2000
if year_built == "2010 or later":
    year_built = 2015

home_value = st.selectbox(
    "Estimated home value",
    [
        "< $150k",
        "$150k–$299k",
        "$300k–$499k",
        "$500k–$749k",
        "$750k+"
    ]
)

if home_value == "< $150k":
    home_value = 100000.0
if home_value == "$150k–$299k":
    home_value = 225000.0
if home_value == "$300k–$499k":
    home_value = 350000.0
if home_value == "$500k–$749k":
    home_value = 625000.0
if home_value == "$750k+":
    home_value = 900000.0

income = st.selectbox(
    "Annual household income",
    [
        "< $35k",
        "$35k–$74k",
        "$75k–$124k",
        "$125k–$199k",
        "$200k+"
    ]
)

if income == "< $35k":
    income = 20000.0
if income == "$35k–$74k":
    income = 55000.0
if income == "$75k–$124k":
    income = 100000.0
if income == "$125k–$199k":
    income = 165000.0
if home_value == "$200k+":
    home_value = 300000.0

piped_water = st.radio(
    "Does the home have community (city/county) water?",
    options=[True, False],
    format_func=lambda x: "Yes" if x else "No"
)

st.divider()

# -------------------------------------------------
# Run model
# -------------------------------------------------
if st.button("Run Assessment", type="primary"):

    # 1. Validate address
    if not street or not city or not state:
        st.error("Please enter a complete address.")
        st.stop()

    # 2. Get coordinates
    lat, lon = get_coordinates(street, city, state, zip_code)
    #print(lat,lon)

    if lat is None:
        st.error("Address could not be located.")
        st.stop()

    # 3. Get census block group
    county,tract,block_group = get_block_group(lat, lon, test_year)

    if block_group is None:
        st.error("Could not determine census block group.")
        st.stop()

    # 4. Display location confirmation
    st.success("Location found")

    #st.write("Latitude:", lat)
    #st.write("Longitude:", lon)
    st.write("Block Group:", block_group)

    st.map({"lat": [lat], "lon": [lon]})

    # 5. Retrieve census variables (example placeholder)
    # also need to get CBG income, default home value, default year built
    county_median_income,county_median_home_value,cbg_family_poverty,cbg_prop_black = get_demographic_data(block_group, test_year)

    # 6. Build model input
    model_inputs = {
        "YEAR":test_year,
        "age_months_continuous":child_age_months,
        "SPECTYPEV":specimen_type,
        "TRI_SOURCES5k":2,
        "NEI_SOURCES5k":3,
        "med_income_pct_of_median":income/county_median_income,
        "PCT_FAMILYPOVERTY":cbg_family_poverty,
        "proportion_black":cbg_prop_black,
        "home_value_pct_of_median":home_value/county_median_home_value,
        "YEAR_BUILT_2":int(year_built),
        "PIPED_WATER1":piped_water
    }
    #print([type(model_inputs[k]) for k in model_inputs.keys()])
    #print(model_inputs)
    
    default_inputs = {
        "YEAR":test_year,
        "age_months_continuous":14,
        "SPECTYPEV":0,
        "TRI_SOURCES5k":2,
        "NEI_SOURCES5k":3,
        "med_income_pct_of_median":county_median_income,
        "PCT_FAMILYPOVERTY":cbg_family_poverty, #update with county
        "proportion_black":cbg_prop_black, #update with county
        "home_value_pct_of_median":county_median_home_value,
        "YEAR_BUILT_2":int(year_built), #update with county
        "PIPED_WATER1":piped_water
    }
    #print([type(default_inputs[k]) for k in default_inputs.keys()])

    # 7. Run model
    result = run_model(model_inputs, default_inputs)

    # 8. Display results
    st.subheader("Assessment Result")
    st.write(result["summary"])

