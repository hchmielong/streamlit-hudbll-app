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
    "Does the home have piped (municipal) water?",
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

    if lat is None:
        st.error("Address could not be located.")
        st.stop()

    # 3. Get census block group
    county,tract,block_group = get_block_group(lat, lon)

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
    county_median_income,county_median_home_value,cbg_family_poverty,cbg_prop_black = get_demographic_data(block_group)

    # 6. Build model input
    model_inputs = {
        "YEAR":year_built,
        "age_months_continuous":14,
        "SPECTYPE":"C",
        "TRI_SOURCES5k":2,
        "NEI_SOURCES5k":3,
        "med_income_pct_of_median":income/county_median_income,
        "PCT_FAMILYPOVERTY":cbg_family_poverty,
        "proportion_black":cbg_prop_black,
        "home_value_pct_of_median":home_value/county_median_home_value,
        "YEAR_BUILT":year_built,
        "PIPED_WATER":piped_water
    }

    # 7. Run model
    result = run_model(model_inputs)

    # 8. Display results
    st.subheader("Assessment Result")
    st.write(result)

