"""
Combined Cross-Cohort SHAP Summary (50+ vs 65+)
=================================================
Single figure, two panels side-by-side: the SHAP beeswarm summary for the
best model in the 50+ cohort and the 65+ cohort, each panel titled with its
model and age cohort.

Why a separate script (not a notebook cell): each notebook only plots its own
cohort's SHAP summary (cell 60). This rebuilds each cohort's data pipeline,
refits only its best model using the tuned params already recorded in the
notebook, recomputes SHAP values exactly as cell 59/60 do (same TreeExplainer
call, same binary/low-cardinality feature exclusion set), and places both
beeswarms in one figure via plt.sca() before each shap.summary_plot() call.

Faithfulness: each notebook uses a deterministic temporal split (train
2020-2023, test 2024) and fixed random_state=42, so the recomputed AUPRC/AUC
must equal the values the notebook reports. The script asserts this before
computing SHAP values.

Run with the same interpreter the notebooks used:
    ~/.pyenv/versions/3.11.9/bin/python build_cross_cohort_shap_summary_overlay.py
"""
import os, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "Main")   # repo-root Main/, two levels up from this script
os.chdir(MAIN)                      # notebooks read ../csv/ relative to Main/

# label, notebook file
# reported Test AUPRC/AUC are read live from each notebook (recover_best), never hardcoded
COHORTS = [
    ("Age 50+", "final.ipynb"),
    ("Age 65+", "final(65+).ipynb"),
]
DATA_CELL = 40                      # cell that defines X_train/X_test/y_train/y_test/feature_cols/*_dummies
OUT_BASENAME = os.path.join(HERE, "cross_cohort_shap_summary_overlay")


def cell_output_text(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif "data" in o and "text/plain" in o["data"]:
            out.append("".join(o["data"]["text/plain"]))
    return "\n".join(out)


def parse_val(v):
    v = v.strip()
    if v == "None":  return None
    if v == "True":  return True
    if v == "False": return False
    if re.fullmatch(r"-?\d+", v): return int(v)
    try:    return float(v)
    except ValueError: return v


def recover_best(nb):
    """Best model name, its reported Test AUPRC/AUC, and its tuned params — all
    read live from the notebook's saved outputs, so this tracks the notebook."""
    best_name = reported_ap = reported_auc = None
    for c in nb["cells"]:
        m = re.search(r"Best model by Test AUPRC:\s*([A-Za-z ]+?)\s*\(Test AUPRC\s*=\s*"
                      r"([\d.]+)\)\s*\|\s*Test AUC:\s*([\d.]+)", cell_output_text(c))
        if m:
            best_name = m.group(1).strip()
            reported_ap, reported_auc = float(m.group(2)), float(m.group(3))
    params_txt = next(cell_output_text(c) for c in nb["cells"]
                      if c["cell_type"] == "code" and "info['best_params']" in "".join(c["source"]))
    blocks, cur = {}, None
    for line in params_txt.split("\n"):
        h = re.match(r"──\s*(.+?)\s*──", line)
        if h:
            cur = h.group(1).strip(); blocks[cur] = {}
        elif cur and line.strip():
            parts = line.split()
            blocks[cur][parts[0]] = parse_val(" ".join(parts[1:]))
    return best_name, reported_ap, reported_auc, blocks[best_name]


def build_estimator(name, params, make_imputer):
    """Identical to the notebooks' build_estimator (cell 53)."""
    if name == "Random Forest":
        return Pipeline([("imputer", make_imputer()),
                         ("model", RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1, **params))])
    if name == "XGBoost":
        return Pipeline([("imputer", make_imputer()),
                         ("model", XGBClassifier(eval_metric="logloss", random_state=42, nthread=1, **params))])
    if name == "LightGBM":
        return Pipeline([("imputer", make_imputer()),
                         ("model", LGBMClassifier(class_weight="balanced", verbose=-1, random_state=42, n_jobs=1, **params))])
    if name == "CatBoost":
        return Pipeline([("imputer", make_imputer()),
                         ("model", CatBoostClassifier(auto_class_weights="Balanced", random_seed=42, verbose=0, **params))])
    if name == "Logistic Regression":
        return Pipeline([("imputer", make_imputer()), ("scaler", StandardScaler()),
                         ("model", LogisticRegression(penalty="elasticnet", class_weight="balanced",
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

    est = build_estimator(best_name, best_params, ns["make_imputer"])
    est.fit(ns["X_train"], ns["y_train"])
    proba = est.predict_proba(ns["X_test"])[:, 1]

    ap = average_precision_score(ns["y_test"], proba)
    assert abs(ap - reported_ap) < 0.01, \
        f"{label}: AUPRC {ap:.4f} != reported {reported_ap:.4f} — pipeline drifted, not drawing."
    auc = roc_auc_score(ns["y_test"], proba)
    assert abs(auc - reported_auc) < 0.01, \
        f"{label}: AUC {auc:.4f} != reported {reported_auc:.4f} — pipeline drifted, not drawing."

    # ── Same SHAP computation as notebook cell 59 ────────────────────────
    X_test_imp = est.named_steps["imputer"].transform(ns["X_test"])
    best_clf = est.named_steps["model"]
    if best_name == "Logistic Regression":
        X_test_scaled = est.named_steps["scaler"].transform(X_test_imp)
        explainer = shap.LinearExplainer(best_clf, X_test_scaled)
        shap_values = explainer.shap_values(X_test_scaled)
    else:
        explainer = shap.TreeExplainer(best_clf)
        sv_raw = explainer.shap_values(X_test_imp)
        # notebook cell 66: newer SHAP returns a 3-D (n, features, classes) array
        # for tree classifiers — take the positive class; fall back to list/2-D
        shap_values = (sv_raw[..., 1] if getattr(sv_raw, "ndim", 0) == 3
                       else (sv_raw[1] if isinstance(sv_raw, list) else sv_raw))

    # ── Same exclusion set as notebook cell 67 ───────────────────────────
    feature_cols = ns["feature_cols"]
    _excl = ({"sm_presnt", "diabetes", "O_pain", "brush_status_2", "town_t"}
             | set(ns["tins_dummies"]) | set(ns["region_dummies"])
             | set(ns["occp_dummies"]) | set(ns["house_dummies"]) | set(ns["live_t_dummies"])
             | set(ns["marri_2_dummies"]) | set(ns["genertn_dummies"]) | set(ns["fam_rela_dummies"]))
    keep_idx = [i for i, fc in enumerate(feature_cols) if fc not in _excl]
    keep_names = [fc for fc in feature_cols if fc not in _excl]

    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f})  "
          f"shap_values {shap_values.shape}  kept features {len(keep_names)}/{len(feature_cols)}")
    return dict(label=label, model=best_name,
                shap_values=shap_values[:, keep_idx], X=X_test_imp[:, keep_idx], names=keep_names)


def plot(results):
    plt.rcParams.update({"font.size": 10})
    fig, axes = plt.subplots(1, 2, figsize=(24, 8))
    for ax, r in zip(axes, results):
        plt.sca(ax)
        shap.summary_plot(r["shap_values"], r["X"], feature_names=r["names"], show=False,
                          plot_size=None)          # None = don't let shap override our figsize
        ax.set_title(f'SHAP Summary — {r["model"]} ({r["label"]})', fontsize=12)
    fig.suptitle("Cross-cohort SHAP feature attribution — best model per age cohort", fontsize=13, y=1.02)
    plt.tight_layout()
    fig.savefig(OUT_BASENAME + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT_BASENAME + ".pdf", bbox_inches="tight")
    print(f"\nWrote {OUT_BASENAME}.png (300 dpi) and {OUT_BASENAME}.pdf")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)