"""
Combined Cross-Cohort SHAP Summary (50+ vs 65+)
=================================================
Single figure, two panels side-by-side: the SHAP beeswarm summary for the
best model in the 50+ cohort and the 65+ cohort, each panel titled with its
model and age cohort.

Why a separate script (not a notebook cell): each notebook only plots its own
cohort's SHAP summary (cell 68/70). This rebuilds each cohort's data pipeline,
refits only its best model using the tuned params already recorded in the
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
import os, re, ast, sys, json
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
MAIN = os.path.join(HERE, "..", "..", "Main")   # repo-root Main/, two levels up from this script
sys.path.insert(0, MAIN)            # codebook_labels.py lives in Main/
os.chdir(MAIN)                      # notebooks read ../csv/ relative to Main/
from codebook_labels import label_list

# label, notebook file
# reported Test AUPRC/AUC are read live from each notebook (recover_best), never hardcoded
COHORTS = [
    ("Age 50+", "final.ipynb"),
    ("Age 65+", "final(65+).ipynb"),
]
DATA_CELL = 47                      # cell that defines X_train/X_test/y_train/y_test/w_test_arr/
                                     # feature_cols, make_imputer, make_scaler and SCALE_POS_WEIGHT
SHAP_MAX_DISPLAY = 20                # matches notebook cell 70's SHAP_MAX_DISPLAY
OUT_BASENAME = os.path.join(HERE, "cross_cohort_shap_summary_overlay")


def cell_output_text(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif "data" in o and "text/plain" in o["data"]:
            out.append("".join(o["data"]["text/plain"]))
    return "\n".join(out)


def recover_best(nb):
    """Best model name, its reported (survey-weighted) Test AUPRC/AUC, and its
    Optuna-tuned params — all read live from the notebook's saved outputs, so this
    tracks the notebook. Selection itself is by OOF AUPRC (leakage-free); Test
    AUPRC/AUC are reported, never used to choose — see cell 54's comment."""
    best_name = reported_ap = reported_auc = None
    for c in nb["cells"]:
        m = re.search(r"Best model by OOF AUPRC:\s*([A-Za-z ]+?)\s*\(OOF AUPRC\s*=\s*[\d.]+\)"
                      r"\s*\|\s*Test AUPRC:\s*([\d.]+)\s*\|\s*Test AUC:\s*([\d.]+)",
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
                                                      solver="saga", max_iter=1000, random_state=42, **params))])
    raise ValueError(name)


def run_cohort(label, nbfile):
    nb = json.load(open(nbfile))
    best_name, reported_ap, reported_auc, best_params = recover_best(nb)
    ns = {"__name__": "__nb__"}
    _real_show = plt.show
    plt.show = lambda *a, **k: None                       # notebook cells call plt.show()
    try:
        for c in nb["cells"][:DATA_CELL + 1]:
            if c["cell_type"] == "code":
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

    # ── No exclusion set: every feature competes on equal footing (cell 70) —
    # summary_plot's own max_display truncates to the top SHAP_MAX_DISPLAY, and
    # codebook_labels supplies the same plain-English axis labels as the notebook.
    feature_cols = ns["feature_cols"]
    names = label_list(feature_cols)

    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f})  "
          f"shap_values {shap_values.shape}  features {len(feature_cols)}")
    return dict(label=label, model=best_name,
                shap_values=shap_values, X=X_test_imp, names=names)


def plot(results):
    plt.rcParams.update({"font.size": 10})
    fig, axes = plt.subplots(1, 2, figsize=(24, 8))
    for ax, r in zip(axes, results):
        plt.sca(ax)
        shap.summary_plot(r["shap_values"], r["X"], feature_names=r["names"], show=False,
                          max_display=SHAP_MAX_DISPLAY,
                          plot_size=None)          # None = don't let shap override our figsize
        ax.set_title(f'SHAP Summary — {r["model"]} ({r["label"]})', fontsize=12)
    fig.suptitle("Cross-cohort SHAP feature attribution — best model per age cohort", fontsize=13, y=1.02)
    plt.tight_layout()
    fig.savefig(OUT_BASENAME + ".png", dpi=600, bbox_inches="tight")
    fig.savefig(OUT_BASENAME + ".pdf", bbox_inches="tight")
    print(f"\nWrote {OUT_BASENAME}.png (600 dpi) and {OUT_BASENAME}.pdf")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)