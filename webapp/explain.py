"""
explain.py — per-prediction feature contributions, one function, two model families.

The two cohorts won with different model types, so a single hardcoded explainer cannot
serve both:

    >=50  CatBoost            imputer -> model            shap.TreeExplainer
    >=65  Logistic Regression imputer -> scaler -> model   closed-form linear SHAP

The linear branch is the exact closed form of shap.LinearExplainer with a training-set
background (verified to 0.0 in export_cohort_models.check_linear_equivalence), so the app
ships a mean vector instead of a ~6000 x 77 background matrix and does not need `shap`
loaded to explain the >=65 cohort at all.

No Streamlit import here.
"""

import numpy as np
import pandas as pd

# Codebook descriptions are written for a variable table, not a chart axis. Only the
# handful that read badly at chart width are overridden; everything else uses the label
# baked into meta.json at build time.
SHORT_LABELS = {
    "sm_presnt": "Current smoker",
    "town_t": "Urban / rural",
    "pa_aerobic": "Aerobic activity",
    "L_BR_FQ": "Breakfast frequency",
    "BD1": "Ever drunk alcohol",
    "BS12_1": "Ever used e-cigarette",
    "BP1": "Perceived stress",
    "BM1_0": "Brushed yesterday",
    "MO4_00": "Dental visit (past yr)",
    "O_pain": "Toothache (past yr)",
    "OR1": "Self-rated oral health",
    "HE_Upro": "Proteinuria",
    "HE_Ucrea": "Urine creatinine",
    "HE_HDL_st2": "HDL cholesterol",
    "eGFR": "eGFR (kidney function)",
    "diabetes": "Diabetes",
    "brush_freq": "Brushings / day",
    "cfam": "Household size",
    "ho_incm": "Income quartile",
    "edu": "Education",
}

_GENERATION_PREFIX = "Household generation-composition code"


def label_for(column, meta):
    if column in SHORT_LABELS:
        return SHORT_LABELS[column]
    label = meta["labels"].get(column, column)
    # The codebook calls genertn a "composition code"; the levels read fine without it.
    return label.replace(_GENERATION_PREFIX, "Household composition")


def _tree_contributions(model, row_df):
    import shap  # imported lazily: only the CatBoost cohort needs it

    imputed = model.named_steps["imputer"].transform(row_df)
    raw = shap.TreeExplainer(model.named_steps["model"]).shap_values(imputed)
    # shap has changed this return shape across releases; the notebook carries the same shim.
    if getattr(raw, "ndim", 0) == 3:
        values = raw[..., 1]
    elif isinstance(raw, list):
        values = raw[1]
    else:
        values = raw
    return np.asarray(values).reshape(-1)


def _linear_contributions(model, meta, row_df):
    background_mean = np.asarray(meta["linear_background_mean"], dtype=float)
    if background_mean.size != len(meta["feature_cols"]):
        raise ValueError("linear_background_mean does not match feature_cols")

    imputed = model.named_steps["imputer"].transform(row_df)
    scaled = model.named_steps["scaler"].transform(imputed)
    coef = model.named_steps["model"].coef_[0]
    return (coef * (scaled - background_mean)).reshape(-1)


def contributions(model, meta, row_df, top_n=12):
    """Signed contributions for one row, largest |value| first, with display labels.

    Returns a Series indexed by label. Positive pushes risk up, negative pushes it down.
    One-hot dummies are KEPT: live_t_2.0, region_15.0/16.0, occp_nan, marri_2_3.0 and
    fam_rela_2.0 all rank inside the top 20 in one cohort or the other, and their baked
    labels read as clinical facts ("Housing type: Apartment"), not as raw codes.
    """
    if meta["model_name"] == "Logistic Regression":
        values = _linear_contributions(model, meta, row_df)
    else:
        values = _tree_contributions(model, row_df)

    series = pd.Series(values, index=meta["feature_cols"])
    series = series.reindex(series.abs().sort_values(ascending=False).index).head(top_n)
    series.index = [label_for(c, meta) for c in series.index]
    return series
