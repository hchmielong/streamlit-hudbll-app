# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 09:40:39 2026

@author: Hana
"""

import streamlit as st
from hudbll_backend import run_model

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Home & Water Risk Tool",
    layout="centered"
)

st.title("🏠 Household Blood-Lead Level Calculation Tool")
st.write(
    "Enter the information below to generate an example model assessment."
)

st.divider()

# -------------------------------------------------
# User inputs
# -------------------------------------------------

zip_code = st.text_input(
    "ZIP Code",
    max_chars=10,
    placeholder="e.g., 27606"
)

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
    if not zip_code:
        st.error("Please enter a ZIP code.")
    else:
        with st.spinner("Running model..."):
            results = run_model(
                zip_code=zip_code,
                year_built=year_built,
                home_value=home_value,
                income=income,
                piped_water=piped_water
            )

        st.success("Assessment complete")

        st.subheader("Results")
        st.write(results["summary"])

        st.caption(f"ZIP Code evaluated: {results['zip_code']}")