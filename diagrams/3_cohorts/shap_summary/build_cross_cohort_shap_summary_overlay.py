"""
Combined Cross-Cohort SHAP Summary (50+ vs 50-64 vs 65+)
=================================================
Single figure, three panels: the SHAP beeswarm summary for the common pinned
CatBoost model in the 50+ cohort, the 50-64 cohort, and the 65+ cohort, each
panel titled with its model and age cohort.

Why a separate script (not a notebook cell): each notebook only plots its own
cohort's SHAP summary (cell 68/70). This rebuilds each cohort's data pipeline,
refits the common pinned CatBoost model using the tuned params recorded in the
notebook, recomputes SHAP values exactly as cell 68/70 do (same TreeExplainer/
LinearExplainer call, same top-20-by-mean|SHAP| display, same codebook labels),
and places both beeswarms in one figure via plt.sca() before each
shap.summary_plot() call.

Faithfulness: each notebook uses a deterministic temporal split (train
2020-2023, test 2024) and fixed random_state=42, so the recomputed AUPRC/AUC
must equal the values the notebook reports. The script asserts this before
computing SHAP values.

Run with the same interpreter the notebooks used:
    ~/.pyenv/versions/3.11.9/bin/python build_cross_cohort_shap_summary_overlay.py
"""
import os, re, ast, sys, json, contextlib, io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "..", "Main")   # repo-root Main/, three levels up from this script
sys.path.insert(0, MAIN)            # codebook_labels.py lives in Main/
os.chdir(MAIN)                      # notebooks read ../csv/ relative to Main/
from codebook_labels import label_list

# label, notebook file
# reported Test AUPRC/AUC are read live from each notebook (recover_best), never hardcoded
COHORTS = [
    ("Age 50+", "CB_50+.ipynb"),
    ("Age 50-64", "CB_50-64.ipynb"),
    ("Age 65+", "CB_65+.ipynb"),
]
# Execute only the cells needed to reconstruct the modeling frame. Resolve them
# by stable source markers so later notebook insertions cannot shift the builder
# onto the wrong cells or the expensive nested Optuna search.
PIPELINE_CELL_MARKERS = (
    "import numpy as np", "CSV_DIR = '../csv'", "raw_columns = [",
    "pd.to_numeric(df_subset['O_TC']", "# Disease diagnoses:",
    "REDUNDANCY_REPRESENTATIVE = {", "_missingness_excluded = [",
    "def calculate_egfr", "# Operational diabetes definition:",
    "from sklearn.impute import SimpleImputer", "from sklearn.pipeline import Pipeline",
    "import optuna",
)
# Panel-title cohort wording (≥ and en dash, matching the text and tables). The COHORTS
# labels above stay as dictionary keys; only the displayed title uses this map.
COHORT_TITLES = {"Age 50+": "Age ≥50", "Age 65+": "Age ≥65", "Age 50-64": "Age 50–64"}
SHAP_MAX_DISPLAY = 15               # top-15 (notebook cell 54 uses 20; this figure intentionally trims to 15)
OUT_BASENAME = os.path.join(HERE, "cross_cohort_shap_summary_overlay")

# Shortened axis labels for THIS figure only (codebook_labels.py / codebook.md stay
# untouched so the notebooks' own SHAP plots keep the full wording) -- frees up
# left-margin width so the beeswarm plots themselves can render larger.
LABEL_OVERRIDES = {
    "Daily brushing frequency (count)": "Daily brushing frequency",
    "Diabetes (diagnosed or HbA1c ≥ 6.5%)": "Diabetes",
    "Dong/Eup-Myeon classification": "Urban/rural classification",
    "Sex": "Female sex",
    "Housing type: Apartment": "Dwelling type: apartment",
    "Estimated kidney function (eGFR, CKD-EPI)": "eGFR",
    "Frequency of fruit intake, past year": "Fruit intake frequency",
    "Current smoking rate indicator": "Current smoking",
    "Final diastolic BP": "Diastolic blood pressure",
}


def cell_output_text(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif "data" in o and "text/plain" in o["data"]:
            out.append("".join(o["data"]["text/plain"]))
    return "\n".join(out)


def pipeline_cells(nb):
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    resolved = []
    for marker in PIPELINE_CELL_MARKERS:
        matches = [c for c in code_cells if marker in "".join(c.get("source", []))]
        assert matches, f"required pipeline cell marker not found: {marker!r}"
        resolved.append(matches[0])
    return resolved


def recover_best(nb):
    """Pinned model name, its reported (survey-weighted) Test AUPRC/AUC, and its
    Optuna-tuned params — all read live from the notebook's saved outputs, so this
    tracks the notebook. The _catboost notebooks HARD-PIN CatBoost for cross-cohort
    SHAP comparability (cell 44), which need not be the OOF-AUPRC leaderboard winner —
    that pin is what this figure explains."""
    best_name = reported_ap = reported_auc = None
    for c in nb["cells"]:
        m = re.search(r"Model pinned for cross-cohort SHAP comparability:\s*([A-Za-z ]+?)\s*"
                      r"\(OOF AUPRC\s*=\s*[\d.]+\s*\|\s*Test AUPRC:\s*([\d.]+)\s*\|\s*Test AUC:\s*([\d.]+)",
                      cell_output_text(c))
        if m:
            best_name = m.group(1).strip()
            reported_ap, reported_auc = float(m.group(2)), float(m.group(3))
    # Optuna best_params, one line per model: "Name: Best AUPRC = 0.xxxx | Params: {...}"
    params_txt = next(cell_output_text(c) for c in nb["cells"]
                      if c["cell_type"] == "code" and "study.best_params" in "".join(c["source"]))
    params_by_model = {}
    for line in params_txt.split("\n"):
        m = re.match(r"([A-Za-z ]+?):\s*Best AUPRC\s*=\s*[\d.]+\s*\|\s*Params:\s*(\{.*\})", line)
        if m:
            params_by_model[m.group(1).strip()] = ast.literal_eval(m.group(2))
    return best_name, reported_ap, reported_auc, params_by_model[best_name]


def build_estimator(name, params, make_imputer, make_scaler, scale_pos_weight):
    """Identical to the notebooks' build_estimator (cell 54)."""
    if name == "Random Forest":
        return Pipeline([("imputer", make_imputer()),
                         ("model", RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1, **params))])
    if name == "XGBoost":
        # scale_pos_weight is PINNED (§8), not tuned, so it never appears in best_params.
        params = {k: v for k, v in params.items() if k != "scale_pos_weight"}
        return Pipeline([("imputer", make_imputer()),
                         ("model", XGBClassifier(scale_pos_weight=scale_pos_weight,
                                                  eval_metric="logloss", random_state=42, nthread=1, **params))])
    if name == "LightGBM":
        return Pipeline([("imputer", make_imputer()),
                         ("model", LGBMClassifier(class_weight="balanced", verbose=-1, random_state=42, n_jobs=1, **params))])
    if name == "CatBoost":
        return Pipeline([("imputer", make_imputer()),
                         ("model", CatBoostClassifier(auto_class_weights="Balanced", random_seed=42, verbose=0, **params))])
    if name == "Logistic Regression":
        # No explicit penalty= (deprecated in sklearn 1.8, removed in 1.10) -- inferred from
        # l1_ratio, which is already in params. make_scaler(), not a blanket StandardScaler:
        # it standardises ordinal/continuous columns only and passes binary/dummy columns
        # through unscaled (cell 38).
        return Pipeline([("imputer", make_imputer()), ("scaler", make_scaler()),
                         ("model", LogisticRegression(class_weight="balanced",
                                                      solver="saga", max_iter=5000, random_state=42, **params))])
    raise ValueError(name)


def run_cohort(label, nbfile):
    nb = json.load(open(nbfile))
    best_name, reported_ap, reported_auc, best_params = recover_best(nb)
    ns = {"__name__": "__nb__"}
    _real_show = plt.show
    plt.show = lambda *a, **k: None                       # notebook cells call plt.show()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            for c in pipeline_cells(nb):
                exec("".join(c["source"]), ns)
    finally:
        plt.show = _real_show
        plt.close("all")

    est = build_estimator(best_name, best_params, ns["make_imputer"], ns["make_scaler"],
                          ns["SCALE_POS_WEIGHT"])
    est.fit(ns["X_train"], ns["y_train"])
    proba = est.predict_proba(ns["X_test"])[:, 1]
    w = ns["w_test_arr"]                # survey weights — Test AUC/AUPRC are population estimates

    ap = average_precision_score(ns["y_test"], proba, sample_weight=w)
    assert abs(ap - reported_ap) < 0.01, \
        f"{label}: AUPRC {ap:.4f} != reported {reported_ap:.4f} — pipeline drifted, not drawing."
    auc = roc_auc_score(ns["y_test"], proba, sample_weight=w)
    assert abs(auc - reported_auc) < 0.01, \
        f"{label}: AUC {auc:.4f} != reported {reported_auc:.4f} — pipeline drifted, not drawing."

    # ── Same SHAP computation as notebook cell 68 ────────────────────────
    X_test_imp = est.named_steps["imputer"].transform(ns["X_test"])
    best_clf = est.named_steps["model"]
    if best_name == "Logistic Regression":
        # BACKGROUND = TRAINING DATA (2020-2023 mean), not the 2024 test mean — see cell 68's
        # comment: LinearExplainer reduces to coef_j * (x_j - E[x_j]), and E[x] must come from
        # the distribution the coefficients were fitted on.
        X_train_imp = est.named_steps["imputer"].transform(ns["X_train"])
        X_train_scaled = est.named_steps["scaler"].transform(X_train_imp)
        X_test_scaled = est.named_steps["scaler"].transform(X_test_imp)
        explainer = shap.LinearExplainer(best_clf, X_train_scaled)
        shap_values = explainer.shap_values(X_test_scaled)
    else:
        explainer = shap.TreeExplainer(best_clf)
        sv_raw = explainer.shap_values(X_test_imp)
        # notebook cell 68: newer SHAP returns a 3-D (n, features, classes) array
        # for tree classifiers — take the positive class; fall back to list/2-D
        shap_values = (sv_raw[..., 1] if getattr(sv_raw, "ndim", 0) == 3
                       else (sv_raw[1] if isinstance(sv_raw, list) else sv_raw))

    # ── Every feature competes on equal footing. Select and order the displayed
    # rows by the conventional unweighted mean |SHAP| across test observations, matching
    # the notebooks' unweighted model-fitting and selection pipeline. Disable
    # summary_plot's internal sorting so this explicit ordering is preserved.
    feature_cols = ns["feature_cols"]
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_idx = np.argsort(mean_abs_shap)[::-1][:SHAP_MAX_DISPLAY]
    top_features = [feature_cols[i] for i in top_idx]
    names = [LABEL_OVERRIDES.get(n, n) for n in label_list(top_features)]

    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f})  "
          f"shap_values {shap_values.shape}  features {len(feature_cols)}")
    return dict(label=label, model=best_name,
                shap_values=shap_values[:, top_idx],
                X=X_test_imp[:, top_idx], names=names)


def plot(results):
    plt.rcParams.update({"font.size": 9, "font.weight": "normal", "axes.labelweight": "normal"})
    fig, axes = plt.subplots(2, 2, figsize=(11.69, 8.25))   # A4 landscape width, same 34:24 aspect ratio as before
    by_label = {r["label"]: r for r in results}
    # 50+ and 65+ on top, 50-64 bottom-left; bottom-right left empty (2x2 grid, 3 panels)
    positions = {
        "Age 50+": axes[0, 0],
        "Age 65+": axes[0, 1],
        "Age 50-64": axes[1, 0],
    }
    axes[1, 1].axis("off")
    LABEL_FONTSIZE = 10   # feature-name labels; also applied to x-axis, its numbers, and the colorbar
    for label, ax in positions.items():
        r = by_label[label]
        plt.sca(ax)
        n_axes_before = len(fig.axes)
        shap.summary_plot(r["shap_values"], r["X"], feature_names=r["names"], show=False,
                          max_display=SHAP_MAX_DISPLAY,
                          sort=False,       # preserve unweighted mean-|SHAP| ordering
                          plot_size=None)          # None = don't let shap override our figsize
        ax.tick_params(axis="y", labelsize=LABEL_FONTSIZE)
        ax.tick_params(axis="x", labelsize=LABEL_FONTSIZE)
        ax.xaxis.label.set_size(LABEL_FONTSIZE)    # "SHAP value (impact on model output)"
        for cax in fig.axes[n_axes_before:]:        # the colorbar axis shap just added
            cax.tick_params(labelsize=LABEL_FONTSIZE)   # "High" / "Low"
            cax.yaxis.label.set_size(LABEL_FONTSIZE)    # "Feature value"
        ax.set_title(f'{r["model"]} ({COHORT_TITLES[r["label"]]})', fontsize=11, fontweight="normal")
    plt.tight_layout()
    fig.savefig(OUT_BASENAME + ".png", dpi=900, bbox_inches="tight")
    print(f"\nWrote {OUT_BASENAME}.png (900 dpi)")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)
