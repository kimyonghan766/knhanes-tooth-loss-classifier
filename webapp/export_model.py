"""
export_model.py — reproduces the preprocessing + XGBoost fit from
Main/test(age).ipynb and serialises the artifacts the Streamlit app loads.

Run once (from the webapp/ folder or repo root):
    python export_model.py

Outputs (written next to this file):
    model.pkl   fitted sklearn Pipeline (imputer -> XGBClassifier)
    meta.json   feature schema (exact column order), decision threshold,
                and headline metrics for display

The XGBoost hyperparameters below are the Optuna-tuned values printed by the
notebook (seeded TPESampler, so they are reproducible). We do NOT re-run Optuna
here — we just refit the already-selected model, which takes seconds.
"""

import json
import os

import numpy as np
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve, matthews_corrcoef
from xgboost import XGBClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(HERE, "..", "csv")
AGE_THRESHOLD = 50

# Optuna-tuned XGBoost params (from notebook cell 41 output)
XGB_PARAMS = dict(
    n_estimators=700,
    max_depth=3,
    learning_rate=0.017666985651626402,
    subsample=0.7911740836717894,
    colsample_bytree=0.5139664876054895,
    min_child_weight=5,
    gamma=0.3075027506331827,
    reg_lambda=2.5525810718988002,
    scale_pos_weight=2.0,
    eval_metric="logloss",
    random_state=42,
    nthread=1,
)


def calculate_egfr(row):
    """CKD-EPI 2021 (race-free). KNHANES sex: 1 = male, 2 = female."""
    scr = row["HE_crea"]
    age = row["age"]
    sex = row["sex"]
    if pd.isna(scr) or pd.isna(sex):
        return np.nan
    if sex == 2:  # female
        kappa, alpha, sex_factor = 0.7, -0.241, 1.012
    else:  # male
        kappa, alpha, sex_factor = 0.9, -0.302, 1.0
    ratio = scr / kappa
    return (142
            * (min(ratio, 1) ** alpha)
            * (max(ratio, 1) ** -1.200)
            * (0.9938 ** age)
            * sex_factor)


def load_and_preprocess():
    """Faithful reproduction of notebook cells 3-33 up to the feature frame."""
    frames = [pd.read_csv(os.path.join(CSV_DIR, f"HN2{y}_all.csv"), low_memory=False)
              for y in range(0, 5)]
    df = pd.concat(frames, ignore_index=True)

    raw_columns = [
        "year", "age", "sex",
        "ho_incm", "edu", "occp", "marri_1", "house", "cfam", "live_t", "tins",
        "region", "town_t",
        "DE1_dg",
        "HE_HbA1c", "HE_BMI", "HE_crea",
        "HE_Uacid", "HE_TG", "HE_sbp", "HE_dbp",
        "HE_Upro", "HE_Ucrea",
        "sm_presnt", "BD1", "pa_aerobic", "BP1",
        "N_CA", "N_EN", "N_NA", "N_PROT", "N_TDF", "LS_VEG1", "LS_FRUIT", "N_SUGAR", "L_BR_FQ",
        "O_pain",
        "MO4_00",
        "BM1_0", "BM1_1", "BM1_2", "BM1_3", "BM1_4", "BM1_5", "BM1_6", "BM1_7", "BM1_8",
        "O_TC",
        "wt_itvex", "psu", "kstrata",
    ]
    d = df[raw_columns].copy()
    d = d[d["age"] >= AGE_THRESHOLD]

    # Target
    d["O_TC"] = pd.to_numeric(d["O_TC"], errors="coerce").replace([np.inf, -np.inf], np.nan)
    d = d.dropna(subset=["O_TC"])
    d["O_TC_"] = (d["O_TC"] < 20).astype(int)

    # Sentinel cleaning
    disease_cols = ["DE1_dg"]
    survey_cols = ["edu", "ho_incm", "occp", "marri_1", "house", "sm_presnt", "BD1",
                   "pa_aerobic", "BP1", "L_BR_FQ", "HE_Upro", "O_pain", "MO4_00",
                   "BM1_0", "BM1_1", "BM1_2", "BM1_3", "BM1_4", "BM1_5", "BM1_6", "BM1_7", "BM1_8"]
    lab_cols = ["HE_HbA1c", "HE_BMI", "HE_crea", "HE_Uacid", "HE_TG", "HE_sbp", "HE_dbp", "HE_Ucrea"]
    diet_cols = ["N_CA", "N_EN", "N_NA", "N_PROT", "N_TDF", "LS_VEG1", "LS_FRUIT", "N_SUGAR"]

    d[disease_cols] = d[disease_cols].replace({8: np.nan, 9: np.nan, 88: np.nan, 99: np.nan})
    d[survey_cols] = d[survey_cols].replace({8: np.nan, 9: np.nan, 88: np.nan, 99: np.nan})
    d[survey_cols] = d[survey_cols].replace([np.inf, -np.inf], np.nan)

    all_lab = lab_cols + diet_cols
    d[all_lab] = d[all_lab].apply(pd.to_numeric, errors="coerce")
    d[all_lab] = d[all_lab].where(d[all_lab].abs() < 1e10, np.nan)
    d.loc[d["HE_crea"] <= 0, "HE_crea"] = np.nan

    d[["cfam", "tins", "live_t"]] = d[["cfam", "tins", "live_t"]].replace([np.inf, -np.inf], np.nan)
    d["tins"] = d["tins"].replace({99: np.nan})
    d["live_t"] = d["live_t"].replace({9: np.nan})

    # Derived: eGFR
    d["eGFR"] = d.apply(calculate_egfr, axis=1)
    d = d.drop(columns=["HE_crea"])

    # Derived: combined diabetes
    diagnosed = (d["DE1_dg"] == 1)
    hba1c_pos = (d["HE_HbA1c"] >= 6.5)
    d["diabetes"] = (diagnosed | hba1c_pos).astype(float)
    both_missing = d["DE1_dg"].isna() & d["HE_HbA1c"].isna()
    d.loc[both_missing, "diabetes"] = np.nan
    d = d.drop(columns=["DE1_dg"])

    # Derived: brushing frequency
    bm1_cols = ["BM1_1", "BM1_2", "BM1_3", "BM1_4", "BM1_5", "BM1_6", "BM1_7", "BM1_8"]
    d["brush_freq"] = d[bm1_cols].sum(axis=1, min_count=1)
    d.loc[d["BM1_0"] == 0, "brush_freq"] = 0

    # Feature frame
    feat = d.copy()
    feat["BD1"] = feat["BD1"].map({1: 1, 2: 0})
    feat["BP1"] = 5 - feat["BP1"]
    feat = pd.get_dummies(feat, columns=["tins", "region", "occp", "house", "live_t"],
                          prefix=["tins", "region", "occp", "house", "live_t"],
                          dummy_na=False, dtype=float)

    nominal_dummies = sorted([c for c in feat.columns if c.startswith("tins_")]) \
        + sorted([c for c in feat.columns if c.startswith("region_")]) \
        + sorted([c for c in feat.columns if c.startswith("occp_")]) \
        + sorted([c for c in feat.columns if c.startswith("house_")]) \
        + sorted([c for c in feat.columns if c.startswith("live_t_")])

    ordinal_cols = [
        "sex", "ho_incm", "edu", "marri_1", "cfam", "town_t",
        "sm_presnt", "BD1", "pa_aerobic", "BP1", "L_BR_FQ",
        "HE_Upro", "O_pain", "MO4_00", "BM1_0", "diabetes",
    ] + nominal_dummies
    continuous_cols = [
        "age", "HE_BMI", "eGFR", "HE_Uacid", "HE_TG", "HE_sbp", "HE_dbp",
        "HE_Ucrea", "N_CA", "N_NA", "N_PROT", "N_TDF", "LS_VEG1", "LS_FRUIT",
        "N_SUGAR", "brush_freq",
    ]
    feature_cols = ordinal_cols + continuous_cols

    return d, feat, ordinal_cols, continuous_cols, feature_cols


def make_imputer(ordinal_cols, continuous_cols):
    return ColumnTransformer([
        ("mode", SimpleImputer(strategy="most_frequent"), ordinal_cols),
        ("median", SimpleImputer(strategy="median"), continuous_cols),
    ])


def main():
    d, feat, ordinal_cols, continuous_cols, feature_cols = load_and_preprocess()

    train_mask = d["year"].isin([2020.0, 2021.0, 2022.0, 2023.0])
    test_mask = d["year"].isin([2024.0])

    X_train = feat.loc[train_mask, feature_cols].replace([np.inf, -np.inf], np.nan)
    X_test = feat.loc[test_mask, feature_cols].replace([np.inf, -np.inf], np.nan)
    y_train = d.loc[train_mask, "O_TC_"]
    y_test = d.loc[test_mask, "O_TC_"]

    print(f"Train: {len(X_train)} | Test: {len(X_test)} | positive rate (train): {y_train.mean():.3f}")

    model = Pipeline([
        ("imputer", make_imputer(ordinal_cols, continuous_cols)),
        ("model", XGBClassifier(**XGB_PARAMS)),
    ])
    model.fit(X_train, y_train)

    # Headline metrics on the held-out 2024 test set
    proba_test = model.predict_proba(X_test)[:, 1]
    test_auc = roc_auc_score(y_test, proba_test)
    test_auprc = average_precision_score(y_test, proba_test)
    print(f"Test AUC: {test_auc:.4f} | Test AUPRC: {test_auprc:.4f}")

    # MCC-optimised threshold from OOF probabilities (notebook cell 51 logic)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof = cross_val_predict(model, X_train, y_train, cv=cv, method="predict_proba")[:, 1]
    _, _, thresh = roc_curve(y_train, oof)
    mcc_scores = [matthews_corrcoef(y_train, (oof >= t).astype(int)) for t in thresh]
    best_idx = int(np.argmax(mcc_scores))
    mcc_threshold = float(thresh[best_idx])
    print(f"MCC threshold (OOF): {mcc_threshold:.4f} | OOF MCC: {mcc_scores[best_idx]:.4f}")

    joblib.dump(model, os.path.join(HERE, "model.pkl"))

    meta = {
        "model_name": "XGBoost",
        "feature_cols": feature_cols,
        "ordinal_cols": ordinal_cols,
        "continuous_cols": continuous_cols,
        "threshold": mcc_threshold,
        "threshold_kind": "MCC-optimised (OOF)",
        "test_auc": round(test_auc, 4),
        "test_auprc": round(test_auprc, 4),
        "train_positive_rate": round(float(y_train.mean()), 4),
    }
    with open(os.path.join(HERE, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print("Wrote model.pkl and meta.json")


if __name__ == "__main__":
    main()
