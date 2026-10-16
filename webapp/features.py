"""
features.py — the form schema and the row builder.

One declarative field spec drives BOTH the Streamlit widgets and the feature-row
assembly, so the form and the model schema cannot drift apart. No Streamlit import
here: everything is a plain function over dicts, so it can be exercised without a
browser.

Two families of field:

  DIRECT_FIELDS   one widget -> one feature column (possibly after a recode)
  NOMINAL_FIELDS  one widget -> a block of one-hot dummies

plus four DERIVED inputs (HbA1c, diagnosed diabetes, serum creatinine, brushings)
that feed engineered features rather than columns of their own.

The dietary block is deliberately absent -- see DIET_COLS.
"""

import numpy as np
import pandas as pd

# Grams/day from a 24-hour dietary recall. No user can self-report these meaningfully,
# so they are left NaN and the pipeline imputes the training median. The app says so.
DIET_COLS = ["N_CA", "N_NA", "N_PROT", "N_TDF", "LS_VEG1", "LS_FRUIT", "N_SUGAR"]

SECTIONS = ["demographics", "labs", "lifestyle", "oral"]


# ── Direct fields ────────────────────────────────────────────────────────────────
# `column` is the feature column the widget's value lands in, as recorded by KNHANES
# unless a note says otherwise. Values are passed through verbatim -- the recodes the
# notebook applies to raw survey codes (BD1, BP1, BS12_1) are folded into the OPTION
# CODES below rather than applied at runtime, so what the user picks is what the model
# sees and there is no second place for the mapping to go wrong.
DIRECT_FIELDS = [
    # ── Demographics & household ──
    dict(column="sex", section="demographics", kind="radio", label="Sex",
         options=[(1, "Male"), (2, "Female")], default=1),
    dict(column="ho_incm", section="demographics", kind="select", label="Income quartile",
         options=[(1, "1 — Lowest"), (2, "2"), (3, "3"), (4, "4 — Highest")], default=2),
    dict(column="edu", section="demographics", kind="select", label="Education",
         options=[(1, "Elementary or less"), (2, "Middle school"),
                  (3, "High school"), (4, "College or above")], default=2),
    dict(column="cfam", section="demographics", kind="select", label="People in household",
         options=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6 or more")],
         default=2),
    dict(column="town_t", section="demographics", kind="radio", label="Area type",
         options=[(1, "Urban (Dong)"), (2, "Rural (Eup/Myeon)")], default=1),

    # ── Clinical labs ──
    dict(column="HE_BMI", section="labs", kind="number", label="BMI (kg/m²)",
         min=12.0, max=50.0, default=24.0, step=0.1),
    dict(column="HE_Uacid", section="labs", kind="number", label="Uric acid (mg/dL)",
         min=1.0, max=15.0, default=5.0, step=0.1),
    dict(column="HE_sbp", section="labs", kind="number", label="Systolic BP (mmHg)",
         min=70.0, max=250.0, default=120.0, step=1.0),
    dict(column="HE_dbp", section="labs", kind="number", label="Diastolic BP (mmHg)",
         min=40.0, max=150.0, default=80.0, step=1.0),
    dict(column="HE_TG", section="labs", kind="number", label="Triglycerides (mg/dL)",
         min=20.0, max=1000.0, default=120.0, step=1.0),
    dict(column="HE_chol", section="labs", kind="number", label="Total cholesterol (mg/dL)",
         min=80.0, max=400.0, default=190.0, step=1.0),
    dict(column="HE_HDL_st2", section="labs", kind="number", label="HDL cholesterol (mg/dL)",
         min=15.0, max=150.0, default=50.0, step=1.0),
    dict(column="HE_Ucrea", section="labs", kind="number", label="Urine creatinine (mg/dL)",
         min=1.0, max=600.0, default=120.0, step=1.0),
    dict(column="HE_Upro", section="labs", kind="select", label="Urine protein (dipstick)",
         options=[(0, "Negative (−)"), (1, "Trace (±)"), (2, "Positive (+)"),
                  (3, "Positive (++)"), (4, "Positive (+++)"), (5, "Positive (++++)")],
         default=0),

    # ── Lifestyle ──
    dict(column="sm_presnt", section="lifestyle", kind="radio", label="Current smoker",
         options=[(0, "No"), (1, "Yes")], default=0),
    # BS12_1 is raw 1=Yes/2=No; the notebook recodes to {1:1, 2:0}, so the option codes
    # below are already the recoded 1/0 values.
    dict(column="BS12_1", section="lifestyle", kind="radio",
         label="Ever used an e-cigarette", options=[(0, "No"), (1, "Yes")], default=0),
    # BD1 is LIFETIME DRINKING EXPERIENCE, raw 1=Never/2=Yes. The notebook recodes to
    # {1:0, 2:1}, i.e. 1 = has ever drunk. The option codes below are the recoded values.
    # The previous webapp shipped the inverse of this and trained never-drinkers as drinkers.
    dict(column="BD1", section="lifestyle", kind="radio",
         label="Ever drunk alcohol (≥ 1 full drink)",
         options=[(0, "No — never"), (1, "Yes")], default=1),
    dict(column="pa_aerobic", section="lifestyle", kind="radio",
         label="Meets aerobic activity guideline", options=[(0, "No"), (1, "Yes")], default=0),
    # BP1 raw runs 1=Extremely high .. 4=Rarely/none; the notebook stores 5 - raw, so the
    # option codes below are already reversed: higher = more stressed.
    dict(column="BP1", section="lifestyle", kind="select", label="Perceived stress",
         options=[(1, "Rarely or none"), (2, "A little"), (3, "High"), (4, "Extremely high")],
         default=2),
    dict(column="L_BR_FQ", section="lifestyle", kind="select",
         label="Breakfast frequency (past year)",
         options=[(1, "5–7 × / week"), (2, "3–4 × / week"), (3, "1–2 × / week"),
                  (4, "Almost never")], default=1),

    # ── Oral health ──
    dict(column="OR1", section="oral", kind="select", label="Self-rated oral health",
         options=[(1, "Very good"), (2, "Good"), (3, "Fair"), (4, "Poor"), (5, "Very poor")],
         default=3, help="The strongest non-age predictor in both cohorts."),
    dict(column="O_pain", section="oral", kind="radio", label="Toothache in past year",
         options=[(0, "No"), (1, "Yes")], default=0),
    dict(column="MO4_00", section="oral", kind="radio", label="Dental visit in past year",
         options=[(0, "No"), (1, "Yes")], default=0),
]

# ── Nominal fields (one widget -> a one-hot block) ───────────────────────────────
# `codes` lists EVERY KNHANES level including the reference. Which ones are actually
# offered is decided per cohort by available_levels(), because the rare-dummy guard drops
# different levels in each cohort.
NOMINAL_FIELDS = [
    dict(parent="marri_2", section="demographics", label="Marital status", default=1.0,
         codes={0.0: "Never married", 1.0: "Married, living together",
                2.0: "Married, living apart", 3.0: "Widowed", 4.0: "Divorced",
                5.0: "Married (detail not recorded)"}),
    dict(parent="genertn", section="demographics", label="Household composition", default=2.0,
         codes={1.0: "One generation — living alone", 2.0: "One generation — couple",
                3.0: "One generation — other",
                4.0: "Two generations — couple + unmarried children",
                5.0: "Two generations — single parent + unmarried children",
                6.0: "Two generations — other", 7.0: "Three or more generations"}),
    dict(parent="fam_rela", section="demographics", label="Relationship to householder",
         default=1.0,
         codes={1.0: "Self", 2.0: "Spouse", 3.0: "Child", 4.0: "Child's spouse",
                5.0: "Grandchild", 6.0: "Parent", 7.0: "Grandparent", 8.0: "Sibling",
                9.0: "Other relative", 10.0: "Non-relative"}),
    dict(parent="live_t", section="demographics", label="Housing type", default=2.0,
         codes={1.0: "Single-family house", 2.0: "Apartment",
                3.0: "Row house / multi-family", 4.0: "Other"}),
    dict(parent="house", section="demographics", label="Home ownership", default=2.0,
         codes={1.0: "Owns none", 2.0: "Owns 1", 3.0: "Owns 2 or more"}),
    dict(parent="occp", section="demographics", label="Occupation", default=7.0,
         codes={1.0: "Manager / professional", 2.0: "Office worker",
                3.0: "Service & sales", 4.0: "Skilled agriculture / forestry / fishery",
                5.0: "Craft / machine operation / assembly", 6.0: "Elementary occupation",
                7.0: "Not employed (homemaker, retired, student)"}),
    dict(parent="tins", section="demographics", label="Health insurance", default=10.0,
         codes={10.0: "National Health Insurance (regional)",
                20.0: "National Health Insurance (employer)", 30.0: "Medical Aid"}),
    dict(parent="region", section="demographics", label="Region", default=1.0,
         codes={1.0: "Seoul", 2.0: "Busan", 3.0: "Daegu", 4.0: "Incheon", 5.0: "Gwangju",
                6.0: "Daejeon", 7.0: "Ulsan", 8.0: "Sejong", 9.0: "Gyeonggi",
                10.0: "Gangwon", 11.0: "Chungbuk", 12.0: "Chungnam", 13.0: "Jeonbuk",
                14.0: "Jeonnam", 15.0: "Gyeongbuk", 16.0: "Gyeongnam", 17.0: "Jeju"}),
]

UNKNOWN_LEVEL = "__unknown__"   # sentinel for the explicit *_nan category

# ── Derived inputs (feed engineered features, not columns of their own) ──────────
DERIVED_FIELDS = [
    dict(key="hba1c", section="labs", kind="number", label="HbA1c (%)",
         min=3.0, max=15.0, default=5.6, step=0.1, help="Flags diabetes at ≥ 6.5%."),
    dict(key="diagnosed_diabetes", section="labs", kind="checkbox",
         label="Diagnosed with diabetes", default=False),
    dict(key="creatinine", section="labs", kind="number", label="Serum creatinine (mg/dL)",
         min=0.2, max=15.0, default=0.9, step=0.1, help="Converted to eGFR internally."),
    dict(key="brush_count", section="oral", kind="slider", label="Brushings yesterday",
         min=0, max=8, default=2,
         help="Also sets 'brushed yesterday', exactly as KNHANES records it."),
]

SECTION_TITLES = {
    "demographics": "1 · Demographics & household",
    "labs": "2 · Clinical labs",
    "lifestyle": "3 · Lifestyle",
    "oral": "4 · Oral health",
}


# ── Cohort-aware option filtering ────────────────────────────────────────────────
def available_levels(field, meta):
    """Levels this cohort can actually represent, as [(value, label), ...].

    A level is offerable when it is either the dropped REFERENCE level (encoded by
    all-zeros, so it needs no column) or has a surviving dummy column. The rare-dummy
    guard drops different levels per cohort -- fam_rela 'Child' and 'Sibling' survive at
    >=50 but not at >=65 -- so offering a hardcoded list would let a user pick a level
    that silently collapses into the reference category.
    """
    parent = field["parent"]
    reference = meta["nominal_ref"][parent]
    cols = set(meta["feature_cols"])

    levels = []
    for value, label in field["codes"].items():
        if value == reference or f"{parent}_{value}" in cols:
            levels.append((value, label))
    if f"{parent}_nan" in cols:
        levels.append((UNKNOWN_LEVEL, "Unknown / prefer not to say"))
    return levels


def default_level(field, meta):
    levels = [v for v, _ in available_levels(field, meta)]
    return field["default"] if field["default"] in levels else levels[0]


# ── Derived features (must match the notebook exactly) ───────────────────────────
def calculate_egfr(scr, age, sex):
    """CKD-EPI 2021 (race-free). KNHANES sex: 1 = male, 2 = female."""
    if scr is None or scr <= 0:
        return np.nan
    if sex == 2:
        kappa, alpha, sex_factor = 0.7, -0.241, 1.012
    else:
        kappa, alpha, sex_factor = 0.9, -0.302, 1.0
    ratio = scr / kappa
    return (142 * (min(ratio, 1) ** alpha) * (max(ratio, 1) ** -1.200)
            * (0.9938 ** age) * sex_factor)


def derive(values):
    """Engineered features from the four derived inputs. Returns a plain dict."""
    egfr = calculate_egfr(values["creatinine"], values["age"], values["sex"])
    diabetes = 1.0 if (values["hba1c"] >= 6.5 or values["diagnosed_diabetes"]) else 0.0
    brush = float(values["brush_count"])
    return {
        "eGFR": egfr,
        "diabetes": diabetes,
        "brush_freq": brush,
        "BM1_0": 1.0 if brush > 0 else 0.0,
    }


# ── Row assembly ─────────────────────────────────────────────────────────────────
def dummy_columns(meta):
    parents = tuple(f"{p}_" for p in meta["nominal_ref"])
    return [c for c in meta["feature_cols"] if c.startswith(parents)]


def build_row(values, meta):
    """Assemble one row in this cohort's exact training schema.

    Un-asked ORDINAL/CONTINUOUS columns (the dietary block) stay NaN, so the fitted
    pipeline imputes the training median. Un-asked DUMMIES start at 0.0, which is only
    correct because every nominal parent is asked -- an all-zero block is the encoding
    of the dropped reference level, not of 'missing'.
    """
    feature_cols = meta["feature_cols"]
    row = {c: np.nan for c in feature_cols}
    for c in dummy_columns(meta):
        row[c] = 0.0

    row["age"] = float(values["age"])
    for field in DIRECT_FIELDS:
        col = field["column"]
        if col in row:
            row[col] = float(values[col])

    for col, value in derive(values).items():
        if col in row:
            row[col] = value

    for field in NOMINAL_FIELDS:
        parent = field["parent"]
        level = values[parent]
        column = (f"{parent}_nan" if level == UNKNOWN_LEVEL else f"{parent}_{level}")
        if column in row:
            row[column] = 1.0
        # No column means the reference level: all-zeros is already its encoding.

    return pd.DataFrame([row])[feature_cols]


def imputed_columns(meta):
    """Feature columns no widget supplies, i.e. what the pipeline fills with the
    training median. Used for the disclosure line under the result."""
    supplied = {"age", "eGFR", "diabetes", "brush_freq", "BM1_0"}
    supplied |= {f["column"] for f in DIRECT_FIELDS}
    supplied |= set(dummy_columns(meta))
    return [c for c in meta["feature_cols"] if c not in supplied]
