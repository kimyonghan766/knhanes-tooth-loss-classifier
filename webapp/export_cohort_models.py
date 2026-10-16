"""
export_cohort_models.py — build the deployment artifacts for BOTH age cohorts.

Reproduces the preprocessing of Main/final.ipynb (>=50) and Main/final(65+).ipynb
(>=65) sections 2.1 -> 4 -> 6 verbatim, refits each cohort's WINNING model with the
Optuna parameters those notebooks printed, and writes the artifacts the Streamlit app
loads.

Optuna is NOT re-run. The searches are seeded (TPESampler(seed=42)) and their best
parameters are transcribed below from notebook cell 49's output; refitting the already
selected configuration takes seconds instead of an hour.

Run:
    python webapp/export_cohort_models.py

Outputs (webapp/artifacts/):
    model_50plus.pkl / meta_50plus.json     CatBoost
    model_65plus.pkl / meta_65plus.json     Logistic Regression

The build ASSERTS itself against Main/shap_importance_{50,65}plus.npz, which the
notebooks wrote. If the reproduction drifts from the notebook -- a changed recode, a
missing feature, a different winner -- the assertions fail and no artifact is written.
"""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
import shap

from catboost import CatBoostClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..")
CSV_DIR = os.path.join(REPO, "csv")
MAIN_DIR = os.path.join(REPO, "Main")
OUT_DIR = os.path.join(HERE, "artifacts")

sys.path.insert(0, MAIN_DIR)
import codebook_labels  # noqa: E402  (needs MAIN_DIR on the path first)

# ── Notebook constants (final.ipynb cells 6, 38, 47) ─────────────────────────────
RAW_COLUMNS = [
    "year", "age", "sex",
    "ho_incm", "edu", "occp", "marri_1", "marri_2", "genertn", "fam_rela",
    "house", "cfam", "live_t", "tins", "region", "town_t",
    "DE1_dg",
    "HE_HbA1c", "HE_BMI", "HE_crea",
    "HE_Uacid", "HE_TG", "HE_sbp", "HE_dbp", "HE_chol", "HE_HDL_st2",
    "HE_Upro", "HE_Ucrea",
    "sm_presnt", "BD1", "pa_aerobic", "BP1",
    "BS12_1",
    "N_CA", "N_NA", "N_PROT", "N_TDF", "LS_VEG1", "LS_FRUIT", "N_SUGAR", "L_BR_FQ",
    "OR1", "O_pain", "MO4_00",
    "BM1_0", "BM1_1", "BM1_2", "BM1_3", "BM1_4", "BM1_5", "BM1_6", "BM1_7", "BM1_8",
    "O_TC",
    "wt_itvex", "psu", "kstrata",
]

# One level per nominal parent is dropped so the dummy block is not collinear with the
# intercept. Values match the inferential model in section 11, so a coefficient means the
# same thing in both arms.
NOMINAL_REF = {"tins": 10, "region": 1, "occp": 1, "house": 1,
               "live_t": 1, "marri_2": 1, "genertn": 1, "fam_rela": 1}

MIN_DUMMY_COUNT = 20          # rare-dummy guard, counted on TRAIN rows only
TRAIN_YEARS = [2020.0, 2021.0, 2022.0, 2023.0]
TEST_YEARS = [2024.0]

ORDINAL_SCALED_COLS = ["ho_incm", "edu", "cfam", "BP1", "L_BR_FQ", "HE_Upro", "OR1"]
BASE_BINARY_COLS = ["sex", "town_t", "sm_presnt", "BD1", "pa_aerobic", "BS12_1",
                    "O_pain", "MO4_00", "BM1_0", "diabetes"]
CONTINUOUS_COLS = [
    "age", "HE_BMI", "eGFR",
    "HE_Uacid", "HE_TG", "HE_sbp", "HE_dbp", "HE_chol", "HE_HDL_st2",
    "HE_Ucrea",
    "N_CA", "N_NA", "N_PROT", "N_TDF", "LS_VEG1", "LS_FRUIT", "N_SUGAR",
    "brush_freq",
]

# ── Per-cohort configuration ─────────────────────────────────────────────────────
# `params` are the Optuna best_params printed by cell 49; `expect` are the figures the
# notebook printed for the selected model, used as build-time assertions.
COHORTS = {
    "50plus": dict(
        age_threshold=50,
        model_name="CatBoost",
        params=dict(iterations=500, depth=4,
                    learning_rate=0.02251362873975811,
                    l2_leaf_reg=3.114641923909002),
        shap_npz="shap_importance_50plus.npz",
        expect=dict(n_features=79, test_auc=0.8339, test_auprc=0.6230,
                    mcc_threshold=0.5571, youden_threshold=0.5245),
    ),
    "65plus": dict(
        age_threshold=65,
        model_name="Logistic Regression",
        params=dict(C=0.22694567397762977, l1_ratio=0.8629273218532529),
        shap_npz="shap_importance_65plus.npz",
        expect=dict(n_features=77, test_auc=0.7524, test_auprc=0.6891,
                    mcc_threshold=0.5378, youden_threshold=0.4757),
    ),
}

# CatBoost is multithreaded and LogisticRegression(saga) stops on a tolerance, so exact
# bit-equality with the notebook run is not guaranteed across machines. These tolerances
# are far tighter than any real preprocessing drift: the inverted BD1 recode alone moves
# test AUC by ~0.01, two orders of magnitude above METRIC_TOL.
METRIC_TOL = 2e-3
THRESHOLD_TOL = 5e-3


# ── Preprocessing (final.ipynb cells 10, 16, 22, 25) ─────────────────────────────
def calculate_egfr(row):
    """CKD-EPI 2021 (race-free). KNHANES sex: 1 = male, 2 = female."""
    scr, age, sex = row["HE_crea"], row["age"], row["sex"]
    if pd.isna(scr) or pd.isna(sex):
        return np.nan
    if sex == 2:
        kappa, alpha, sex_factor = 0.7, -0.241, 1.012
    else:
        kappa, alpha, sex_factor = 0.9, -0.302, 1.0
    ratio = scr / kappa
    return (142 * (min(ratio, 1) ** alpha) * (max(ratio, 1) ** -1.200)
            * (0.9938 ** age) * sex_factor)


def load_and_clean(age_threshold):
    """final.ipynb cells 4 -> 25: load, age-filter, label, de-sentinel, derive."""
    frames = [pd.read_csv(os.path.join(CSV_DIR, f"HN2{y}_all.csv"), low_memory=False)
              for y in range(0, 5)]
    df = pd.concat(frames, ignore_index=True)

    d = df[RAW_COLUMNS].copy()
    d = d[d["age"] >= age_threshold]

    # Target: -1.80E+308 overflows float64 to -inf rather than NaN, so replace explicitly.
    d["O_TC"] = pd.to_numeric(d["O_TC"], errors="coerce").replace([np.inf, -np.inf], np.nan)
    d = d.dropna(subset=["O_TC"])
    d["O_TC_"] = (d["O_TC"] < 20).astype(int)

    disease_cols = ["DE1_dg"]
    survey_cols = ["edu", "ho_incm", "occp", "marri_1", "house", "sm_presnt", "BD1",
                   "pa_aerobic", "BP1", "BS12_1", "L_BR_FQ", "HE_Upro", "OR1", "O_pain",
                   "MO4_00", "BM1_0", "BM1_1", "BM1_2", "BM1_3", "BM1_4", "BM1_5",
                   "BM1_6", "BM1_7", "BM1_8"]
    lab_cols = ["HE_HbA1c", "HE_BMI", "HE_crea", "HE_Uacid", "HE_TG", "HE_sbp",
                "HE_dbp", "HE_chol", "HE_HDL_st2", "HE_Ucrea"]
    diet_cols = ["N_CA", "N_NA", "N_PROT", "N_TDF", "LS_VEG1", "LS_FRUIT", "N_SUGAR"]

    # HN24 loads these as strings (its overflow sentinel forces object dtype), so the
    # numeric-keyed .replace below would silently no-op on every 2024 row without this.
    d[disease_cols + survey_cols] = d[disease_cols + survey_cols].apply(
        pd.to_numeric, errors="coerce")
    d[disease_cols] = d[disease_cols].replace({8: np.nan, 9: np.nan, 88: np.nan, 99: np.nan})
    d[survey_cols] = d[survey_cols].replace({8: np.nan, 9: np.nan, 88: np.nan, 99: np.nan})
    d[survey_cols] = d[survey_cols].replace([np.inf, -np.inf], np.nan)

    all_lab = lab_cols + diet_cols
    d[all_lab] = d[all_lab].apply(pd.to_numeric, errors="coerce")
    d[all_lab] = d[all_lab].where(d[all_lab].abs() < 1e10, np.nan)
    d.loc[d["HE_crea"] <= 0, "HE_crea"] = np.nan

    d[["cfam", "tins", "live_t"]] = d[["cfam", "tins", "live_t"]].apply(
        pd.to_numeric, errors="coerce")
    d[["cfam", "tins", "live_t"]] = d[["cfam", "tins", "live_t"]].replace(
        [np.inf, -np.inf], np.nan)
    d["tins"] = d["tins"].replace({99: np.nan})     # valid 10/20/30
    d["live_t"] = d["live_t"].replace({9: np.nan})  # valid 1-4
    d["cfam"] = d["cfam"].replace({9: np.nan})      # valid 1-6

    # Column-specific sentinels: fam_rela's 9 is a VALID category (sibling), so these
    # cannot join the blanket {8,9,88,99} -> NaN replace above.
    d[["marri_2", "genertn", "fam_rela"]] = d[["marri_2", "genertn", "fam_rela"]].apply(
        pd.to_numeric, errors="coerce")
    d[["marri_2", "genertn", "fam_rela"]] = d[["marri_2", "genertn", "fam_rela"]].replace(
        [np.inf, -np.inf], np.nan)
    d["marri_2"] = d["marri_2"].replace({8: np.nan, 88: np.nan, 99: np.nan})
    d["genertn"] = d["genertn"].replace({9: np.nan})
    d["fam_rela"] = d["fam_rela"].replace({99: np.nan})

    # marri_2 carries marital status on its own: 0 = never married, 1-4 = KNHANES detail,
    # 5 = married but detail missing. marri_1 is then an exact function of it and is not
    # modelled separately.
    d.loc[d["marri_1"] == 2, "marri_2"] = 0
    d.loc[(d["marri_1"] == 1) & d["marri_2"].isna(), "marri_2"] = 5

    d["eGFR"] = d.apply(calculate_egfr, axis=1)
    d = d.drop(columns=["HE_crea"], errors="ignore")

    # Combined diabetes: NaN comparisons return False, so the OR is safe; only set NaN
    # when BOTH sources are missing.
    diabetes = ((d["DE1_dg"] == 1) | (d["HE_HbA1c"] >= 6.5)).astype(float)
    d["diabetes"] = diabetes.mask(d["DE1_dg"].isna() & d["HE_HbA1c"].isna(), np.nan)
    d = d.drop(columns=["DE1_dg"], errors="ignore")

    bm1_cols = [f"BM1_{i}" for i in range(1, 9)]
    d["brush_freq"] = d[bm1_cols].sum(axis=1, min_count=1)
    # Non-brushers have all 8 slots coded N/A -> NaN sum; their true frequency is 0.
    d.loc[d["BM1_0"] == 0, "brush_freq"] = 0

    return d


def build_feature_frame(d):
    """final.ipynb cell 38: recodes, one-hot with reference levels + explicit unknowns."""
    feat = d.copy()

    # BD1 is LIFETIME DRINKING EXPERIENCE with 1 = NEVER, so the drinker indicator is
    # map({1: 0, 2: 1}). The old webapp used {1: 1, 2: 0}, which inverted the variable.
    feat["BD1"] = feat["BD1"].map({1: 0, 2: 1})
    feat["BP1"] = 5 - feat["BP1"]              # higher = more stressed
    feat["BS12_1"] = feat["BS12_1"].map({1: 1, 2: 0})

    feat = pd.get_dummies(feat, columns=list(NOMINAL_REF), prefix=list(NOMINAL_REF),
                          dummy_na=True, dtype=float)

    # dummy_na=True gives a MISSING parent value its own explicit "unknown" column rather
    # than an all-zero row that is byte-identical to the dropped reference level. pandas
    # emits a *_nan column even for parents with no missing values, so drop the all-zero
    # ones to keep feature_cols honest.
    nan_cols = [c for c in feat.columns if c.endswith("_nan")]
    feat = feat.drop(columns=[c for c in nan_cols if feat[c].sum() == 0])

    ref_cols = [f"{p}_{float(l)}" for p, l in NOMINAL_REF.items()]
    missing_ref = [c for c in ref_cols if c not in feat.columns]
    assert not missing_ref, f"Reference dummy column(s) not found: {missing_ref}"
    feat = feat.drop(columns=ref_cols)

    nominal_dummies = []
    for parent in NOMINAL_REF:
        nominal_dummies += sorted(c for c in feat.columns if c.startswith(f"{parent}_"))

    return feat, nominal_dummies


def make_imputer(ordinal_cols, continuous_cols):
    # keep_empty_features=True stops SimpleImputer silently dropping an all-NaN column,
    # which would shrink the transformed matrix with no error.
    return ColumnTransformer([
        ("mode", SimpleImputer(strategy="most_frequent", keep_empty_features=True), ordinal_cols),
        ("median", SimpleImputer(strategy="median", keep_empty_features=True), continuous_cols),
    ])


def make_scaler(n_ordinal_scaled, n_binary, n_continuous):
    """Standardise the ordinal and continuous blocks; pass binary indicators through.

    Three contiguous index ranges of the imputer's output, which emits
    [ordinal_scaled | binary | continuous] in that order. Standardising a binary
    manufactures an extreme value out of nothing: a column with proportion p sends its
    minority rows to sqrt((1-p)/p). All three blocks are listed explicitly because a
    remainder='passthrough' would emit the transformed block first and silently permute
    the columns relative to feature_cols.
    """
    b0, b1 = n_ordinal_scaled, n_ordinal_scaled + n_binary
    return ColumnTransformer([
        ("scale_ordinal", StandardScaler(), list(range(0, b0))),
        ("passthrough", "passthrough", list(range(b0, b1))),
        ("scale_cont", StandardScaler(), list(range(b1, b1 + n_continuous))),
    ])


def build_estimator(model_name, params, ordinal_cols, continuous_cols,
                    n_ordinal_scaled, n_binary):
    if model_name == "CatBoost":
        return Pipeline([
            ("imputer", make_imputer(ordinal_cols, continuous_cols)),
            ("model", CatBoostClassifier(auto_class_weights="Balanced",
                                         random_seed=42, verbose=0, **params)),
        ])
    if model_name == "Logistic Regression":
        return Pipeline([
            ("imputer", make_imputer(ordinal_cols, continuous_cols)),
            ("scaler", make_scaler(n_ordinal_scaled, n_binary, len(continuous_cols))),
            # penalty is inferred from l1_ratio: the explicit penalty= argument was
            # deprecated in scikit-learn 1.8 and is removed in 1.10.
            ("model", LogisticRegression(solver="saga", class_weight="balanced",
                                         max_iter=1000, random_state=42, **params)),
        ])
    raise ValueError(f"No builder for {model_name}")


# ── Thresholds and calibration (final.ipynb cells 76, 86) ────────────────────────
def mcc_curve(y_true, proba, thresholds):
    """MCC at every threshold, vectorised.

    Equivalent to [matthews_corrcoef(y_true, proba >= t) for t in thresholds] but
    O(n log n): sort the scores once and read the confusion matrix off a running total,
    the same trick sklearn's roc_curve uses.
    """
    y = np.asarray(y_true, dtype=np.int64)
    p = np.asarray(proba, dtype=float)
    order = np.argsort(-p, kind="mergesort")
    y_sorted, p_sorted = y[order], p[order]
    P, N = int(y.sum()), y.size - int(y.sum())
    k = np.searchsorted(-p_sorted, -np.asarray(thresholds, dtype=float), side="right")
    cum_tp = np.concatenate(([0], np.cumsum(y_sorted)))
    TP = cum_tp[k].astype(float)
    FP, FN = k - TP, P - TP
    TN = N - FP
    denom = np.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))
    with np.errstate(invalid="ignore", divide="ignore"):
        mcc = (TP * TN - FP * FN) / denom
    return np.where(denom == 0, 0.0, mcc)


def _logit(p, eps=1e-6):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def fit_platt(oof_proba, y_train):
    """Section 10.3 recalibration. Fitted on TRAIN out-of-fold probabilities, never on
    the test set, so it carries no hold-out leakage into deployment.

    C=np.inf keeps Platt scaling UNPENALISED -- the default C=1 L2 would shrink the
    slope toward 0, and the slope is itself the reported calibration diagnostic.
    """
    recalibrator = LogisticRegression(C=np.inf).fit(
        _logit(oof_proba).reshape(-1, 1), y_train)
    return float(recalibrator.coef_[0, 0]), float(recalibrator.intercept_[0])


def apply_platt(proba, slope, intercept):
    z = slope * _logit(proba) + intercept
    return 1.0 / (1.0 + np.exp(-z))


# ── SHAP background for the linear cohort (final.ipynb cell 68) ──────────────────
def linear_contributions(coef, x_scaled, background_mean):
    """shap.LinearExplainer with a background dataset reduces to this exactly."""
    return coef * (x_scaled - background_mean)


def check_linear_equivalence(clf, X_train_scaled, X_sample_scaled, background_mean):
    """Assert the closed form above IS shap.LinearExplainer, so the app can ship a mean
    vector instead of a ~6000 x 77 background matrix.

    The masker is passed explicitly. shap.LinearExplainer(clf, ndarray) wraps a bare array
    in Independent(data, max_samples=100), which SUBSAMPLES the background to 100 rows --
    the notebook's own section 9.9 hits that default, so its SHAP values are measured
    against a 100-row background mean rather than the full 2020-2023 mean. Verified: the
    closed form matches the 100-row default to only 4.3e-2, and the full background to
    0.0e0 exactly. The app uses the full training mean, which is the baseline the notebook
    comment describes and is strictly less noisy than the 100-row draw.
    """
    masker = shap.maskers.Independent(X_train_scaled, max_samples=len(X_train_scaled))
    reference = shap.LinearExplainer(clf, masker).shap_values(X_sample_scaled)
    ours = linear_contributions(clf.coef_[0], X_sample_scaled, background_mean)
    max_diff = float(np.abs(reference - ours).max())
    assert max_diff < 1e-9, (
        f"closed-form linear SHAP differs from shap.LinearExplainer by {max_diff:.3e}")
    return max_diff


# ── Build one cohort ─────────────────────────────────────────────────────────────
def build(cohort_key, cfg):
    print(f"\n{'=' * 78}\n{cohort_key}  (age >= {cfg['age_threshold']})\n{'=' * 78}")

    d = load_and_clean(cfg["age_threshold"])
    feat, nominal_dummies = build_feature_frame(d)

    binary_cols = BASE_BINARY_COLS + nominal_dummies
    ordinal_cols = ORDINAL_SCALED_COLS + binary_cols
    feature_cols = ordinal_cols + CONTINUOUS_COLS

    train_mask = d["year"].isin(TRAIN_YEARS)
    test_mask = d["year"].isin(TEST_YEARS)

    # Rare-dummy guard, counted on TRAIN rows only so the 2024 hold-out never informs the
    # feature set. A dummy with a handful of positives carries no estimable coefficient.
    counts = feat.loc[train_mask, nominal_dummies].sum()
    rare = sorted(counts[counts < MIN_DUMMY_COUNT].index)
    if rare:
        print(f"Dropped {len(rare)} rare dummies (< {MIN_DUMMY_COUNT} train positives): "
              f"{', '.join(rare)}")
        binary_cols = [c for c in binary_cols if c not in rare]
        ordinal_cols = [c for c in ordinal_cols if c not in rare]
        feature_cols = [c for c in feature_cols if c not in rare]
    assert ordinal_cols == ORDINAL_SCALED_COLS + binary_cols, (
        "ordinal_cols must stay ordered as [ordinal_scaled | binary] for make_scaler()")

    X_train = feat.loc[train_mask, feature_cols].replace([np.inf, -np.inf], np.nan)
    X_test = feat.loc[test_mask, feature_cols].replace([np.inf, -np.inf], np.nan)
    y_train = d.loc[train_mask, "O_TC_"]
    y_test = d.loc[test_mask, "O_TC_"]

    # Survey weights are used ONLY where a metric is reported, never where a model is
    # fitted or selected. psu/kstrata drive design-based variance estimation, which the
    # sklearn metrics do not perform, so they are deliberately unused.
    w_test = d.loc[test_mask, "wt_itvex"].astype(float).to_numpy()

    print(f"Train {len(X_train):,} rows | Test {len(X_test):,} rows | "
          f"{len(feature_cols)} features | positive rate {y_train.mean():.4f}")

    # ── Assertion 1/2: feature schema and winner match the notebook's own output ──
    npz = np.load(os.path.join(MAIN_DIR, cfg["shap_npz"]), allow_pickle=True)
    nb_features = [str(c) for c in npz["feature_names"]]
    nb_model = str(npz["model_name"])
    if feature_cols != nb_features:
        missing = [c for c in nb_features if c not in feature_cols]
        extra = [c for c in feature_cols if c not in nb_features]
        raise AssertionError(
            f"feature_cols != {cfg['shap_npz']}\n  missing: {missing}\n  extra: {extra}\n"
            f"  order-only mismatch: {sorted(feature_cols) == sorted(nb_features)}")
    assert nb_model == cfg["model_name"], (
        f"notebook selected {nb_model}, config says {cfg['model_name']}")
    assert len(feature_cols) == cfg["expect"]["n_features"]
    print(f"[ok] feature schema matches {cfg['shap_npz']} "
          f"({len(feature_cols)} features, winner {nb_model})")

    # ── Fit ──
    estimator = build_estimator(cfg["model_name"], cfg["params"], ordinal_cols,
                                CONTINUOUS_COLS, len(ORDINAL_SCALED_COLS), len(binary_cols))
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof_proba = cross_val_predict(estimator, X_train, y_train, cv=cv,
                                  method="predict_proba")[:, 1]
    estimator.fit(X_train, y_train)
    proba_test = estimator.predict_proba(X_test)[:, 1]

    # ── Assertion 3: survey-weighted test metrics reproduce ──
    test_auc = roc_auc_score(y_test, proba_test, sample_weight=w_test)
    test_auprc = average_precision_score(y_test, proba_test, sample_weight=w_test)
    for label, got, want in [("Test AUC", test_auc, cfg["expect"]["test_auc"]),
                             ("Test AUPRC", test_auprc, cfg["expect"]["test_auprc"])]:
        assert abs(got - want) < METRIC_TOL, (
            f"{label} {got:.4f} != notebook {want:.4f} (tol {METRIC_TOL})")
        print(f"[ok] {label:11s} {got:.4f}  (notebook {want:.4f})")

    # ── Assertion 4: OOF thresholds reproduce ──
    fpr, tpr, thresholds = roc_curve(y_train, oof_proba)
    youden_threshold = float(thresholds[(tpr + (1 - fpr) - 1).argmax()])
    scores = mcc_curve(y_train, oof_proba, thresholds)
    mcc_threshold = float(thresholds[int(np.argmax(scores))])
    for label, got, want in [("MCC thresh", mcc_threshold, cfg["expect"]["mcc_threshold"]),
                             ("Youden thresh", youden_threshold, cfg["expect"]["youden_threshold"])]:
        assert abs(got - want) < THRESHOLD_TOL, (
            f"{label} {got:.4f} != notebook {want:.4f} (tol {THRESHOLD_TOL})")
        print(f"[ok] {label:11s} {got:.4f}  (notebook {want:.4f})")

    # ── Platt recalibration ──
    slope, intercept = fit_platt(oof_proba, y_train)
    assert slope > 0, "Platt slope must be positive for the threshold map to stay monotone"
    proba_recal = apply_platt(proba_test, slope, intercept)
    brier_raw = brier_score_loss(y_test, proba_test, sample_weight=w_test)
    brier_recal = brier_score_loss(y_test, proba_recal, sample_weight=w_test)
    print(f"[ok] Platt slope {slope:.4f} intercept {intercept:.4f} | "
          f"Brier {brier_raw:.4f} -> {brier_recal:.4f}")

    # ── Assertion 5: closed-form linear SHAP == shap.LinearExplainer ──
    background_mean = None
    if cfg["model_name"] == "Logistic Regression":
        X_train_imp = estimator.named_steps["imputer"].transform(X_train)
        X_train_scaled = estimator.named_steps["scaler"].transform(X_train_imp)
        background_mean = X_train_scaled.mean(axis=0)
        X_test_imp = estimator.named_steps["imputer"].transform(X_test)
        X_test_scaled = estimator.named_steps["scaler"].transform(X_test_imp)
        diff = check_linear_equivalence(estimator.named_steps["model"], X_train_scaled,
                                        X_test_scaled[:200], background_mean)
        print(f"[ok] linear SHAP equivalence, max |diff| {diff:.2e}")

    # ── Write artifacts ──
    os.makedirs(OUT_DIR, exist_ok=True)
    joblib.dump(estimator, os.path.join(OUT_DIR, f"model_{cohort_key}.pkl"))

    meta = {
        "cohort": cohort_key,
        "age_threshold": cfg["age_threshold"],
        "model_name": cfg["model_name"],
        "feature_cols": feature_cols,
        "ordinal_scaled_cols": ORDINAL_SCALED_COLS,
        "binary_cols": binary_cols,
        "continuous_cols": CONTINUOUS_COLS,
        "nominal_ref": {k: float(v) for k, v in NOMINAL_REF.items()},
        "mcc_threshold": mcc_threshold,
        "youden_threshold": youden_threshold,
        "threshold_kind": "MCC-optimised (OOF)",
        "platt_slope": slope,
        "platt_intercept": intercept,
        "test_auc": round(float(test_auc), 4),
        "test_auprc": round(float(test_auprc), 4),
        "brier_raw": round(float(brier_raw), 4),
        "brier_recal": round(float(brier_recal), 4),
        "train_positive_rate": round(float(y_train.mean()), 4),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        # Baked at build time so the app never needs codebook.md at runtime.
        "labels": {c: codebook_labels.label_for(c) for c in feature_cols},
        "linear_background_mean": (None if background_mean is None
                                   else [float(v) for v in background_mean]),
    }
    with open(os.path.join(OUT_DIR, f"meta_{cohort_key}.json"), "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"Wrote artifacts/model_{cohort_key}.pkl and artifacts/meta_{cohort_key}.json")


def main():
    for cohort_key, cfg in COHORTS.items():
        build(cohort_key, cfg)
    print("\nAll cohorts built and verified against the notebooks.")


if __name__ == "__main__":
    main()
