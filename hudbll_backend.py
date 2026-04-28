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


import json
import os
import numpy as np
from collections import Counter

# Load metadata
with open("C:/Users/Hana/OneDrive - North Carolina State University/BLL_data/BLL_HUD_Guilford_Wake/Models/feature_order.json") as f:
    feature_order = json.load(f)

with open("C:/Users/Hana/OneDrive - North Carolina State University/BLL_data/BLL_HUD_Guilford_Wake/Models/factor_levels.json") as f:
    factor_levels = json.load(f)
    
feature_index = {f: i for i, f in enumerate(feature_order)}

# Load trees
trees = []
tree_dir = "C:/Users/Hana/OneDrive - North Carolina State University/BLL_data/BLL_HUD_Guilford_Wake/Models/rf_trees"


# Step 1: find all classes from leaf predictions
classes = set()
for fname in sorted(os.listdir(tree_dir)):
    if fname.endswith(".json"):
        with open(os.path.join(tree_dir, fname)) as f:
            nodes = json.load(f)
        for node in nodes:
            if node['status'] == -1:
                classes.add(node.get("prediction"))

class_list = sorted(classes)
class_index = {c: i for i, c in enumerate(class_list)}
class_reverse_index = {i: c for c, i in class_index.items()}

# Step 2: load all trees
trees = []

for fname in sorted(os.listdir(tree_dir)):
    if not fname.endswith(".json"):
        continue
    with open(os.path.join(tree_dir, fname)) as f:
        nodes = json.load(f)

    left, right, split_var, split_point, status, prediction = [], [], [], [], [], []

    for node in nodes:
        left.append(node["left daughter"] - 1)
        right.append(node["right daughter"] - 1)
        status.append(node["status"])

        if node["status"] != -1:  # internal node
            feat_name = node["split var"]
            # if leaf value got put here by mistake, ignore it
            if feat_name not in feature_index:
                feat_name = None
            split_var.append(feature_index[feat_name] if feat_name else -1)
            split_point.append(node["split point"])
            prediction.append(-1)
        else:  # leaf node
            split_var.append(-1)
            split_point.append(0)
            prediction.append(class_index[node.get("prediction")])

    trees.append({
        "left": np.array(left, dtype=np.int32),
        "right": np.array(right, dtype=np.int32),
        "split_var": np.array(split_var, dtype=np.int32),
        "split_point": np.array(split_point, dtype=np.float32),
        "status": np.array(status, dtype=np.int8),
        "prediction": np.array(prediction, dtype=np.int32)
    })

print(f"Loaded {len(trees)} trees")


def encode_row(input_dict):
    """Convert input dict to numeric row for prediction."""
    row = []
    for f in feature_order:
        val = input_dict[f]
        if f in factor_levels:
            val = factor_levels[f].index(val) + 1  # R-style 1-based
        row.append(val)
    return row

def predict_tree(tree, row):
    node = 0
    while True:
        if tree["status"][node] == -1:  # leaf node
            return tree["prediction"][node]  # class index

        feature_idx = tree["split_var"][node]
        val = row[feature_idx]

        if val <= tree["split_point"][node]:
            node = tree["left"][node]
        else:
            node = tree["right"][node]
            


def predict(row):
    votes = [predict_tree(tree, row) for tree in trees]
    # majority vote
    class_idx = Counter(votes).most_common(1)[0][0]
    return class_reverse_index[class_idx]  # convert back to original label

def predict_proba(row):
    """Return probability for each class as a dict."""
    votes = [predict_tree(tree, row) for tree in trees]  # list of class indices
    counts = np.zeros(len(class_list), dtype=np.float32)

    for v in votes:
        counts[v] += 1

    probs = counts / len(trees)  # normalize to get probabilities
    return {class_reverse_index[i]: probs[i] for i in range(len(class_list))}

#sample = {"YEAR":2019,"age_months_continuous":12.24,"SPECTYPE":"C","TRI_SOURCES5k":1,"NEI_SOURCES5k":0,"med_income_pct_of_median":1.827838,
#          "PCT_FAMILYPOVERTY":3.252033,"proportion_black":0.127191,"home_value_pct_of_median":1.739434,"YEAR_BUILT":2003.858,"PIPED_WATER":1,"LEAD_3.5":"X0"}

sample = {"YEAR":2014,"age_months_continuous":12.12,"SPECTYPE":"C","TRI_SOURCES5k":1,"NEI_SOURCES5k":1,"med_income_pct_of_median":1.423952,
          "PCT_FAMILYPOVERTY":14.33566,"proportion_black":0.07192118,"home_value_pct_of_median":1.205479,"YEAR_BUILT":1963.0008,"PIPED_WATER":0,"LEAD_3.5":"X0"}

sample = {"YEAR":2014,"age_months_continuous":12.24,"SPECTYPE":"C","TRI_SOURCES5k":1,"NEI_SOURCES5k":1,"med_income_pct_of_median":1.423952,
          "PCT_FAMILYPOVERTY":14.33566,"proportion_black":0.07192118,"home_value_pct_of_median":1.205479,"YEAR_BUILT":1963.0008,"PIPED_WATER":0,"LEAD_3.5":"X0"}

sample = {"YEAR":2014,"age_months_continuous":26.16,"SPECTYPE":"C","TRI_SOURCES5k":1,"NEI_SOURCES5k":1,"med_income_pct_of_median":1.423952,
          "PCT_FAMILYPOVERTY":14.33566,"proportion_black":0.07192118,"home_value_pct_of_median":1.402153,"YEAR_BUILT":1971.000,"PIPED_WATER":0,"LEAD_3.5":"X0"}

sample = {"YEAR":2014,"age_months_continuous":12.12,"SPECTYPE":"C","TRI_SOURCES5k":1,"NEI_SOURCES5k":1,"med_income_pct_of_median":1.423952,
          "PCT_FAMILYPOVERTY":14.33566,"proportion_black":0.07192118,"home_value_pct_of_median":1.171531,"YEAR_BUILT":1974.061,"PIPED_WATER":0,"LEAD_3.5":"X0"}

sample = {"YEAR":2014,"age_months_continuous":12.12,"SPECTYPE":"C","TRI_SOURCES5k":1,"NEI_SOURCES5k":1,"med_income_pct_of_median":1.423952,
          "PCT_FAMILYPOVERTY":14.33566,"proportion_black":0.07192118,"home_value_pct_of_median":1.064686,"YEAR_BUILT":1975.744,"PIPED_WATER":0,"LEAD_3.5":"X0"}

sample = {"YEAR":2014,"age_months_continuous":12.12,"SPECTYPE":"C","TRI_SOURCES5k":1,"NEI_SOURCES5k":1,"med_income_pct_of_median":1.423952,
          "PCT_FAMILYPOVERTY":14.33566,"proportion_black":0.07192118,"home_value_pct_of_median":1.078701,"YEAR_BUILT":1975.887,"PIPED_WATER":0,"LEAD_3.5":"X0"}



row = encode_row(sample)
result = predict(row)
print("Predicted class:", result)
probs = predict_proba(row)
print("Predicted probabilities:", probs)