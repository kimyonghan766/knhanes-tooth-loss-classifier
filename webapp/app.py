"""
Tooth Loss Risk Predictor — Streamlit app.

Serves the two cohort models built by export_cohort_models.py. Age selects the cohort:
at 65 and above the app switches to the >=65 artifacts, and the model, decision
threshold, headline metrics, dropdown option sets and SHAP chart all move together.

Run:  streamlit run webapp/app.py
"""

import json
import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

import explain
import features

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(HERE, "artifacts")

AGE_MIN, AGE_MAX = 50, 80          # KNHANES top-codes age at 80
COHORT_SWITCH_AGE = 65

RISK_UP = "#C44E52"
RISK_DOWN = "#4C72B0"


@st.cache_resource
def load_cohort(cohort_key):
    model = joblib.load(os.path.join(ARTIFACTS, f"model_{cohort_key}.pkl"))
    with open(os.path.join(ARTIFACTS, f"meta_{cohort_key}.json")) as f:
        meta = json.load(f)
    return model, meta


def cohort_for(age):
    return "65plus" if age >= COHORT_SWITCH_AGE else "50plus"


def platt(proba, meta):
    """Section 10.3 recalibration, fitted on training out-of-fold probabilities."""
    p = np.clip(proba, 1e-6, 1 - 1e-6)
    z = meta["platt_slope"] * np.log(p / (1 - p)) + meta["platt_intercept"]
    return float(1.0 / (1.0 + np.exp(-z)))


def render_field(container, field, key_prefix):
    """Render one DIRECT_FIELDS / DERIVED_FIELDS entry and return its value."""
    kind = field["kind"]
    key = f"{key_prefix}_{field.get('column') or field['key']}"
    label, help_text = field["label"], field.get("help")

    if kind in ("radio", "select"):
        values = [v for v, _ in field["options"]]
        labels = dict(field["options"])
        widget = container.radio if kind == "radio" else container.selectbox
        return widget(label, values, index=values.index(field["default"]),
                      format_func=lambda v: labels[v], key=key, help=help_text,
                      **({"horizontal": True} if kind == "radio" else {}))
    if kind == "number":
        return container.number_input(label, float(field["min"]), float(field["max"]),
                                      float(field["default"]), float(field["step"]),
                                      key=key, help=help_text)
    if kind == "slider":
        return container.slider(label, field["min"], field["max"], field["default"],
                                key=key, help=help_text)
    if kind == "checkbox":
        return container.checkbox(label, value=field["default"], key=key, help=help_text)
    raise ValueError(f"Unknown widget kind: {kind}")


def render_section(section, meta, values, n_cols=3):
    """Render every field in one section into an n-column grid."""
    st.subheader(features.SECTION_TITLES[section])
    cols = st.columns(n_cols)
    slot = 0

    for field in features.DIRECT_FIELDS + features.DERIVED_FIELDS:
        if field["section"] != section:
            continue
        key = field.get("column") or field["key"]
        values[key] = render_field(cols[slot % n_cols], field, meta["cohort"])
        slot += 1

    for field in features.NOMINAL_FIELDS:
        if field["section"] != section:
            continue
        levels = features.available_levels(field, meta)
        options = [v for v, _ in levels]
        labels = dict(levels)
        default = features.default_level(field, meta)
        values[field["parent"]] = cols[slot % n_cols].selectbox(
            field["label"], options, index=options.index(default),
            format_func=lambda v, labels=labels: labels[v],
            key=f"{meta['cohort']}_{field['parent']}")
        slot += 1


def plot_contributions(series):
    fig, ax = plt.subplots(figsize=(6, 0.34 * len(series) + 1.0))
    colors = [RISK_UP if v > 0 else RISK_DOWN for v in series.values]
    ax.barh(list(series.index), series.values, color=colors, edgecolor="black", linewidth=0.5)
    ax.axvline(0, color="black", lw=0.8)
    ax.invert_yaxis()
    ax.set_xlabel("SHAP value   (→ raises risk,  ← lowers risk)")
    ax.tick_params(labelsize=9)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tooth Loss Risk Predictor", page_icon="🦷", layout="wide")
st.title("🦷 Tooth Loss Risk Predictor")
st.caption("Predicts having fewer than 20 functional teeth. KNHANES 2020–2024, "
           "trained on 2020–2023 and tested on the held-out 2024 wave.")

# Age sits above the form because it SELECTS the cohort — everything below re-renders.
age = st.slider("Age", AGE_MIN, AGE_MAX, 60,
                help=f"At {COHORT_SWITCH_AGE} and above the app switches to the ≥65 cohort model.")
model, meta = load_cohort(cohort_for(age))

st.info(
    f"**≥{meta['age_threshold']} cohort** · {meta['model_name']} · "
    f"Test AUC {meta['test_auc']} · AUPRC {meta['test_auprc']} · "
    f"decision threshold {meta['mcc_threshold']:.3f} ({meta['threshold_kind']}) · "
    f"{meta['n_train']:,} training rows, {len(meta['feature_cols'])} features"
)

left, right = st.columns([1.35, 1])
values = {"age": age}

with left:
    for section in features.SECTIONS:
        render_section(section, meta, values)
    predict = st.button("Predict risk", type="primary", use_container_width=True)

with right:
    st.subheader("Result")
    if not predict:
        st.info("Fill in the form and press **Predict risk**.")
    else:
        row = features.build_row(values, meta)
        raw = float(model.predict_proba(row)[0, 1])
        calibrated = platt(raw, meta)

        # Platt scaling is monotone (slope > 0, asserted at build time), so comparing the
        # RAW score to the RAW threshold gives exactly the notebook's decision, while the
        # displayed number is the calibrated one. Mapping the threshold through the same
        # transform keeps the two consistent on screen.
        high = raw >= meta["mcc_threshold"]
        threshold_shown = platt(meta["mcc_threshold"], meta)

        st.metric("Predicted tooth-loss risk", f"{calibrated * 100:.0f}%")
        st.progress(min(calibrated, 1.0))
        if high:
            st.error("**HIGH RISK** — fewer than 20 functional teeth")
        else:
            st.success("**LOW RISK** — 20 or more functional teeth")

        derived = features.derive(values)
        st.caption(
            f"Calibrated at {calibrated * 100:.1f}% vs threshold {threshold_shown * 100:.1f}% "
            f"(raw score {raw:.3f} vs {meta['mcc_threshold']:.3f}). "
            f"eGFR {derived['eGFR']:.0f} mL/min/1.73m² · "
            f"diabetes flag {'yes' if derived['diabetes'] else 'no'}."
        )

        st.markdown("**What's driving this prediction**")
        st.pyplot(plot_contributions(explain.contributions(model, meta, row)))

        imputed = features.imputed_columns(meta)
        if imputed:
            st.caption(
                f"{len(imputed)} dietary variables were not collected by this form and "
                f"were set to the ≥{meta['age_threshold']} cohort's training median: "
                + ", ".join(explain.label_for(c, meta) for c in imputed) + "."
            )
        st.caption(
            f"Probabilities are Platt-recalibrated on training out-of-fold predictions "
            f"(Brier {meta['brier_raw']} → {meta['brier_recal']} on the 2024 test wave)."
        )
        st.warning("For research use only — not medical advice.")
