"""
Tooth Loss Risk Predictor — Streamlit app.

Loads the artifacts produced by export_model.py (model.pkl + meta.json) and
serves a single-page risk-screening form. Raw KNHANES encodings are hidden
behind friendly inputs; derived features (eGFR, diabetes, brushing) are
computed in-app to match the training pipeline exactly.

Run:  streamlit run app.py
"""

import json
import os

import numpy as np
import pandas as pd
import joblib
import shap
import streamlit as st
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

# Friendly labels for the SHAP contribution chart (raw column -> readable name)
DISPLAY_NAMES = {
    "age": "Age", "sex": "Sex", "ho_incm": "Income quartile", "edu": "Education",
    "marri_1": "Marital status", "town_t": "Urban/Rural", "eGFR": "eGFR (kidney)",
    "diabetes": "Diabetes", "HE_BMI": "BMI", "HE_Uacid": "Uric acid",
    "HE_TG": "Triglycerides", "HE_sbp": "Systolic BP", "HE_dbp": "Diastolic BP",
    "sm_presnt": "Current smoker", "BD1": "Current drinker", "pa_aerobic": "Physical activity",
    "BP1": "Perceived stress", "brush_freq": "Brushing frequency", "BM1_0": "Brushed yesterday",
    "O_pain": "Dental pain", "MO4_00": "Dental visit (past yr)", "HE_Ucrea": "Urine creatinine",
    "HE_Upro": "Proteinuria",
}


@st.cache_resource
def load_artifacts():
    model = joblib.load(os.path.join(HERE, "model.pkl"))
    with open(os.path.join(HERE, "meta.json")) as f:
        meta = json.load(f)
    return model, meta


def calculate_egfr(scr, age, sex):
    """CKD-EPI 2021. sex: 1 = male, 2 = female."""
    if scr is None or scr <= 0:
        return np.nan
    if sex == 2:
        kappa, alpha, sex_factor = 0.7, -0.241, 1.012
    else:
        kappa, alpha, sex_factor = 0.9, -0.302, 1.0
    ratio = scr / kappa
    return (142 * (min(ratio, 1) ** alpha) * (max(ratio, 1) ** -1.200)
            * (0.9938 ** age) * sex_factor)


def is_dummy(col):
    return col.startswith(("tins_", "region_", "occp_", "house_", "live_t_"))


def build_feature_row(inputs, meta):
    """Construct a one-row DataFrame in the exact training schema.

    Un-asked continuous/ordinal columns -> NaN (pipeline imputes median/mode).
    Un-asked one-hot dummies            -> 0  (reference / absent category).
    """
    feature_cols = meta["feature_cols"]
    row = {c: (0.0 if is_dummy(c) else np.nan) for c in feature_cols}

    egfr = calculate_egfr(inputs["creatinine"], inputs["age"], inputs["sex"])
    diabetes = 1.0 if (inputs["hba1c"] >= 6.5 or inputs["diagnosed_diabetes"]) else 0.0

    row.update({
        "age": inputs["age"],
        "sex": inputs["sex"],
        "ho_incm": inputs["ho_incm"],
        "edu": inputs["edu"],
        "marri_1": inputs["marri_1"],
        "town_t": inputs["town_t"],
        "HE_BMI": inputs["bmi"],
        "eGFR": egfr,
        "HE_Uacid": inputs["uacid"],
        "HE_TG": inputs["tg"],
        "HE_sbp": inputs["sbp"],
        "HE_dbp": inputs["dbp"],
        "diabetes": diabetes,
        "sm_presnt": inputs["smoker"],
        "BD1": inputs["drinker"],
        "pa_aerobic": inputs["physical"],
        "BP1": inputs["stress"],          # already on the reversed (high = stressed) scale
        "brush_freq": inputs["brush"],
        "BM1_0": 1.0 if inputs["brush"] > 0 else 0.0,
        "O_pain": inputs["pain"],
        "MO4_00": inputs["visit"],
    })
    df = pd.DataFrame([row])[feature_cols]
    return df, egfr, diabetes


def shap_contributions(model, df, meta, top_n=8):
    imputer = model.named_steps["imputer"]
    clf = model.named_steps["model"]
    X_imp = imputer.transform(df)
    transformed_cols = meta["ordinal_cols"] + meta["continuous_cols"]
    explainer = shap.TreeExplainer(clf)
    sv = explainer.shap_values(X_imp)
    if isinstance(sv, list):
        sv = sv[1]
    sv = np.asarray(sv).reshape(-1)
    s = pd.Series(sv, index=transformed_cols)
    # collapse one-hot groups so the chart shows clinical drivers, not region_7
    s = s[[c for c in s.index if not is_dummy(c)]]
    return s.reindex(s.abs().sort_values(ascending=False).index).head(top_n)


# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tooth Loss Risk Predictor", page_icon="🦷", layout="wide")
model, meta = load_artifacts()

st.title("🦷 Tooth Loss Risk Predictor")
st.caption(
    f"Model: {meta['model_name']} · Test AUC {meta['test_auc']} · "
    f"Decision threshold {meta['threshold']:.3f} ({meta['threshold_kind']}) · "
    "KNHANES 2020–2024, adults aged ≥ 50"
)

left, right = st.columns([1.1, 1])

with left:
    st.subheader("1 · Demographics")
    c1, c2 = st.columns(2)
    age = c1.slider("Age", 50, 80, 65)
    sex = c2.radio("Sex", [1, 2], format_func=lambda x: "Male" if x == 1 else "Female", horizontal=True)
    ho_incm = c1.selectbox("Income quartile", [1, 2, 3, 4],
                           format_func=lambda x: {1: "1 — Lowest", 2: "2", 3: "3", 4: "4 — Highest"}[x])
    edu = c2.selectbox("Education", [1, 2, 3, 4],
                       format_func=lambda x: {1: "Elementary", 2: "Middle school",
                                              3: "High school", 4: "College+"}[x])
    marri_1 = c1.selectbox("Marital status", [1, 2],
                           format_func=lambda x: "Has spouse" if x == 1 else "No spouse")
    town_t = c2.selectbox("Region type", [1, 2],
                          format_func=lambda x: "Urban (Dong)" if x == 1 else "Rural (Eup/Myeon)")

    st.subheader("2 · Clinical labs")
    c1, c2, c3 = st.columns(3)
    hba1c = c1.number_input("HbA1c (%)", 3.0, 15.0, 5.6, 0.1,
                            help="Used to flag diabetes (≥ 6.5%)")
    bmi = c2.number_input("BMI (kg/m²)", 12.0, 50.0, 24.0, 0.1)
    creatinine = c3.number_input("Serum creatinine (mg/dL)", 0.2, 15.0, 0.9, 0.1,
                                 help="Converted to eGFR internally")
    uacid = c1.number_input("Uric acid (mg/dL)", 1.0, 15.0, 5.0, 0.1)
    sbp = c2.number_input("Systolic BP (mmHg)", 70, 250, 120, 1)
    dbp = c3.number_input("Diastolic BP (mmHg)", 40, 150, 80, 1)
    tg = c1.number_input("Triglycerides (mg/dL)", 20, 1000, 120, 1)
    diagnosed_diabetes = c2.checkbox("Diagnosed with diabetes", value=False)

    st.subheader("3 · Lifestyle")
    c1, c2, c3 = st.columns(3)
    smoker = c1.radio("Current smoker", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
    drinker = c2.radio("Current drinker", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
    physical = c3.radio("Aerobic activity", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
    stress = c1.select_slider("Perceived stress", options=[1, 2, 3, 4],
                              value=2, format_func=lambda x: {1: "Almost none", 2: "A little",
                                                              3: "A lot", 4: "Very high"}[x])
    brush = c2.slider("Brushing / day", 0, 8, 2)
    visit = c3.radio("Dental visit (past yr)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
    pain = c1.radio("Dental pain", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)

    predict = st.button("Predict risk", type="primary", use_container_width=True)

with right:
    st.subheader("Result")
    if not predict:
        st.info("Fill the form and press **Predict risk**.")
    else:
        inputs = dict(age=age, sex=sex, ho_incm=ho_incm, edu=edu, marri_1=marri_1,
                      town_t=town_t, hba1c=hba1c, bmi=bmi, creatinine=creatinine,
                      uacid=uacid, sbp=sbp, dbp=dbp, tg=tg,
                      diagnosed_diabetes=diagnosed_diabetes, smoker=smoker, drinker=drinker,
                      physical=physical, stress=stress, brush=brush, visit=visit, pain=pain)
        df, egfr, diabetes = build_feature_row(inputs, meta)
        proba = float(model.predict_proba(df)[0, 1])
        high = proba >= meta["threshold"]

        st.metric("Predicted tooth-loss risk", f"{proba * 100:.0f}%")
        st.progress(min(proba, 1.0))
        if high:
            st.error("**HIGH RISK** of tooth loss (< 20 functional teeth)")
        else:
            st.success("**LOW RISK** of tooth loss (< 20 functional teeth)")
        st.caption(f"Computed eGFR: {egfr:.0f} mL/min/1.73m²  ·  Diabetes flag: {'Yes' if diabetes else 'No'}")

        st.markdown("**What's driving this prediction**")
        contrib = shap_contributions(model, df, meta)
        fig, ax = plt.subplots(figsize=(5, 3.2))
        colors = ["#C44E52" if v > 0 else "#4C72B0" for v in contrib.values]
        labels = [DISPLAY_NAMES.get(c, c) for c in contrib.index]
        ax.barh(labels, contrib.values, color=colors, edgecolor="black")
        ax.axvline(0, color="k", lw=0.8)
        ax.invert_yaxis()
        ax.set_xlabel("SHAP value  (→ increases risk,  ← decreases)")
        fig.tight_layout()
        st.pyplot(fig)

        st.warning("For research use only — not medical advice.")
