"""
Combined Cross-Cohort ROC + PR + Calibration Overlay (50+ vs 65+)
=====================================================================
Single figure, three panels: PR curve overlay (left), ROC curve overlay
(middle), and calibration overlay (right), each showing the best model for
the 50+ cohort and the 65+ cohort on the same axes.

Why a separate script (not a notebook cell): each notebook only plots its
own cohort's curves. This rebuilds each cohort's data pipeline, refits only
its best model using the tuned params already recorded in the notebook, and
draws all three curves for both cohorts overlaid -- each cohort's best model
is fit once and its predicted probabilities are reused for all three panels.

Faithfulness: each notebook uses a deterministic temporal split (train
2020-2023, test 2024) and fixed random_state=42, so the recomputed
AUPRC/AUC must equal the values the notebook reports. The script asserts
this before drawing.

Run with the same interpreter the notebooks used:
    ~/.pyenv/versions/3.11.9/bin/python build_cross_cohort_overlay.py
"""
import os, re, ast, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (precision_recall_curve, average_precision_score,
                              roc_curve, roc_auc_score, brier_score_loss)
from sklearn.calibration import calibration_curve
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "Main")   # repo-root Main/, two levels up from this script
os.chdir(MAIN)                      # notebooks read ../csv/ relative to Main/

# label, notebook file, plot colour (Okabe-Ito, CVD-safe)
# reported Test AUPRC/AUC are read live from each notebook (recover_best), never hardcoded
COHORTS = [
    ("50+",  "final.ipynb",       "#0072B2"),
    ("65+",  "final(65+).ipynb",  "#009E73"),
]
DATA_CELL = 47                      # cell that defines X_train/X_test/y_train/y_test/w_test_arr,
                                     # make_imputer, make_scaler and SCALE_POS_WEIGHT
N_BINS = 10                         # matches the notebooks' calibration_curve(..., n_bins=10, strategy='uniform')
OUT_PNG = os.path.join(HERE, "cross_cohort_overlay.png")
OUT_PDF = os.path.join(HERE, "cross_cohort_overlay.pdf")


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


def run_cohort(label, nbfile, color):
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
    y_test = ns["y_test"]
    w = ns["w_test_arr"]                # survey weights — Test AUC/AUPRC/Brier are population estimates

    prec, rec, _ = precision_recall_curve(y_test, proba, sample_weight=w)
    ap = average_precision_score(y_test, proba, sample_weight=w)
    baseline = float(np.average(y_test, weights=w))
    assert abs(ap - reported_ap) < 0.01, \
        f"{label}: AUPRC {ap:.4f} != reported {reported_ap:.4f} — pipeline drifted, not drawing."

    fpr, tpr, _ = roc_curve(y_test, proba, sample_weight=w)
    auc = roc_auc_score(y_test, proba, sample_weight=w)
    assert abs(auc - reported_auc) < 0.01, \
        f"{label}: AUC {auc:.4f} != reported {reported_auc:.4f} — pipeline drifted, not drawing."

    brier = brier_score_loss(y_test, proba, sample_weight=w)
    # calibration_curve accepts no sample_weight, so the plotted CURVE stays unweighted
    # (sample-level) while the Brier score above is survey-weighted — matches cell 82/84.
    prob_true, prob_pred = calibration_curve(y_test, proba, n_bins=N_BINS, strategy="uniform")

    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f})  Brier {brier:.4f}  n_test {len(y_test)}")
    return dict(label=label, model=best_name, prec=prec, rec=rec, ap=ap, baseline=baseline,
                fpr=fpr, tpr=tpr, auc=auc, brier=brier, prob_true=prob_true, prob_pred=prob_pred,
                color=color)


def plot(results):
    plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#888888"})
    fig, (ax_pr, ax_roc, ax_cal) = plt.subplots(1, 3, figsize=(21.5, 6.2))

    # ── Left panel: PR overlay ──────────────────────────────────────────
    ax_pr.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_pr.set_axisbelow(True)
    for r in results:
        ax_pr.plot(r["rec"], r["prec"], color=r["color"], linewidth=2.0, zorder=3,
                   label=f'{r["label"]} · {r["model"]}  (AUPRC {r["ap"]:.3f})')
        ax_pr.axhline(r["baseline"], color=r["color"], linewidth=1.3,
                      linestyle=(0, (5, 4)), alpha=0.7, zorder=2)
        ax_pr.text(0.985, r["baseline"], f'chance {r["baseline"]:.3f}',
                   color=r["color"], fontsize=9, ha="right", va="bottom", zorder=4,
                   bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))
    ax_pr.set_xlim(0, 1.0)
    ax_pr.set_ylim(0, 1.02)
    ax_pr.set_xlabel("Recall  (of tooth-loss cases, <20 teeth)")
    ax_pr.set_ylabel("Precision")
    ax_pr.set_title("Precision–Recall", fontsize=12, loc="left")
    ax_pr.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9.5)
    for s in ("top", "right"):
        ax_pr.spines[s].set_visible(False)

    # ── Middle panel: ROC overlay ────────────────────────────────────────
    ax_roc.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_roc.set_axisbelow(True)
    ax_roc.plot([0, 1], [0, 1], color="#888888", linewidth=1.3,
               linestyle=(0, (5, 4)), alpha=0.7, zorder=2, label="Chance (AUC 0.500)")
    for r in results:
        ax_roc.plot(r["fpr"], r["tpr"], color=r["color"], linewidth=2.0, zorder=3,
                    label=f'{r["label"]} · {r["model"]}  (AUC {r["auc"]:.3f})')
    ax_roc.set_xlim(0, 1.0)
    ax_roc.set_ylim(0, 1.02)
    ax_roc.set_xlabel("False Positive Rate")
    ax_roc.set_ylabel("True Positive Rate")
    ax_roc.set_title("ROC", fontsize=12, loc="left")
    ax_roc.legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=9.5)
    for s in ("top", "right"):
        ax_roc.spines[s].set_visible(False)

    # ── Right panel: Calibration overlay ─────────────────────────────────
    ax_cal.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_cal.set_axisbelow(True)
    ax_cal.plot([0, 1], [0, 1], color="#888888", linewidth=1.3,
               linestyle=(0, (5, 4)), alpha=0.7, zorder=2, label="Perfectly calibrated")
    for r in results:
        ax_cal.plot(r["prob_pred"], r["prob_true"], color=r["color"], linewidth=2.0,
                   marker="o", markersize=5, markeredgecolor="white", markeredgewidth=0.6,
                   zorder=3, label=f'{r["label"]} · {r["model"]}  (Brier {r["brier"]:.3f})')
    ax_cal.set_xlim(0, 1.0)
    ax_cal.set_ylim(0, 1.02)
    ax_cal.set_xlabel("Mean predicted probability")
    ax_cal.set_ylabel("Observed frequency")
    ax_cal.set_title("Calibration", fontsize=12, loc="left")
    ax_cal.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=9.5)
    for s in ("top", "right"):
        ax_cal.spines[s].set_visible(False)

    fig.suptitle("Cross-cohort AUPRC, AUROC & Calibration — best model per age cohort (2024 test set)",
                 fontsize=13, x=0.01, ha="left")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    print(f"\nWrote {OUT_PNG} (300 dpi) and {OUT_PDF}")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)
