# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 09:41:01 2026

@author: Hana
"""

def run_model(
    zip_code: str,
    year_built: str,
    home_value: str,
    income: str,
    piped_water: bool
):
    """
    Placeholder backend model.
    Replace this logic with your actual model.
    """

    # Example derived logic
    risk_score = 0

    if piped_water is False:
        risk_score += 2

    if year_built in ["Before 1950", "1950–1969"]:
        risk_score += 1

    if home_value == "< $150k":
        risk_score += 1

    return {
        "zip_code": zip_code,
        "risk_score": risk_score,
        "summary": (
            f"Based on the provided information, the estimated risk score "
            f"for the home is {risk_score} (higher = more potential concern)."
        )
    }