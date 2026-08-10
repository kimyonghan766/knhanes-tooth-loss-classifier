"""
Cross-Cohort Calibration + DCA Overlay (50+ vs 65+)
=====================================================================
Single figure, two panels: Platt-recalibrated calibration curve (left),
Decision Curve Analysis / net benefit (right), each showing BOTH age
cohorts on the same axes -- 50+ in blue, 65+ in red (best model only,
per cohort). Both panels reuse the notebooks' own algorithms verbatim
(cells 54, 80, 84-85 of Main/final.ipynb / final(65+).ipynb):

  - Calibration: out-of-fold (OOF) train-set probabilities for ALL 5 tuned
    models -> unpenalised Platt scaling (logistic regression on the logit of
    the OOF probabilities, C=inf) -> apply to the TEST set -> 10-bin
    calibration_curve on the best model's recalibrated probabilities.
  - DCA: net benefit of the best model's recalibrated probabilities across
    thresholds 0.01-0.50 (dcurves), alongside "Treat all" (differs by
    cohort prevalence) and "Treat none" (0 for both) reference lines.

Why a separate script (not a notebook cell): each notebook only computes
its own cohort's OOF probabilities / Platt scaling / DCA. Re-running the
notebooks' Optuna hyperparameter search (cell 49, 50 trials x 5 models)
would be needlessly expensive, so this script recovers each model's
ALREADY-TUNED best_params from the notebook's saved Optuna print lines
(cell 49's output text) and reproduces cell 54's OOF loop, cell 80's Platt
scaling, and cells 84-85's DCA exactly, without re-searching.

Faithfulness: each notebook uses a deterministic temporal split (train
2020-2023, test 2024), fixed random_state=42, and a fixed 5-fold
StratifiedKFold(shuffle=True, random_state=42) for OOF (cell 47's `cv`),
so the recomputed best-model Test AUPRC/AUC must equal the values the
notebook reports, and the recomputed best model name must match. The
script asserts both before drawing.

Run with the same interpreter the notebooks used:
    ~/.pyenv/versions/3.11.9/bin/python build_calibration_dca_overlay.py
"""
import os, re, ast, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.calibration import calibration_curve
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from dcurves import dca

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "Main")   # repo-root Main/, two levels up from this script
os.chdir(MAIN)                      # notebooks read ../csv/ relative to Main/

# label, notebook file, plot colour (Okabe-Ito blue / true red -- validated CVD-safe pair)
COHORTS = [
    ("50+",  "final.ipynb",       "#0072B2"),
    ("65+",  "final(65+).ipynb",  "#D62728"),
]
DATA_CELL = 47                      # cell that defines X_train/X_test/y_train/y_test/w_test_arr,
                                     # make_imputer, make_scaler, SCALE_POS_WEIGHT and `cv`
N_BINS = 10                         # matches the notebooks' calibration_curve(..., n_bins=10, strategy='uniform')
DCA_THRESHOLDS = np.arange(0.01, 0.51, 0.01)   # matches notebook cell 84's dca_thresholds
OUT_PNG = os.path.join(HERE, "calibration_dca_overlay.png")
OUT_PDF = os.path.join(HERE, "calibration_dca_overlay.pdf")
PNG_DPI = 600                       # Elsevier-grade combination art


def cell_output_text(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif "data" in o and "text/plain" in o["data"]:
            out.append("".join(o["data"]["text/plain"]))
    return "\n".join(out)


def recover_best_and_all_params(nb):
    """Best model name + reported Test AUPRC/AUC (from cell 54's printed summary line),
    and every tuned model's best_params + CV AUPRC (from cell 49's printed lines) --
    all read live from the notebook's saved outputs, never re-searched."""
    best_name = reported_ap = reported_auc = None
    for c in nb["cells"]:
        m = re.search(r"Best model by OOF AUPRC:\s*([A-Za-z ]+?)\s*\(OOF AUPRC\s*=\s*[\d.]+\)"
                      r"\s*\|\s*Test AUPRC:\s*([\d.]+)\s*\|\s*Test AUC:\s*([\d.]+)",
                      cell_output_text(c))
        if m:
            best_name = m.group(1).strip()
            reported_ap, reported_auc = float(m.group(2)), float(m.group(3))
    params_txt = next(cell_output_text(c) for c in nb["cells"]
                      if c["cell_type"] == "code" and "study.best_params" in "".join(c["source"]))
    params_by_model = {}
    for line in params_txt.split("\n"):
        m = re.match(r"([A-Za-z ]+?):\s*Best AUPRC\s*=\s*[\d.]+\s*\|\s*Params:\s*(\{.*\})", line)
        if m:
            params_by_model[m.group(1).strip()] = ast.literal_eval(m.group(2))
    assert best_name in params_by_model, f"best model {best_name!r} missing from parsed params"
    return best_name, reported_ap, reported_auc, params_by_model


def build_estimator(name, params, make_imputer, make_scaler, scale_pos_weight):
    """Identical to the notebooks' build_estimator (cell 54)."""
    if name == "Random Forest":
        return Pipeline([("imputer", make_imputer()),
                         ("model", RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1, **params))])
    if name == "XGBoost":
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
        return Pipeline([("imputer", make_imputer()), ("scaler", make_scaler()),
                         ("model", LogisticRegression(class_weight="balanced",
                                                      solver="saga", max_iter=1000, random_state=42, **params))])
    raise ValueError(name)


def xgb_oof_proba(params, X_train, y_train, cv, make_imputer, scale_pos_weight_unused):
    """Mirrors cell 54's _xgb_oof_proba: fold-local scale_pos_weight (XGBoost has no
    'balanced' string option, so cross_val_predict alone would freeze it at the
    full-training-set ratio instead of recomputing per fold like the other 4 models)."""
    _params = {k: v for k, v in params.items() if k != "scale_pos_weight"}
    oof = np.zeros(len(X_train))
    for train_idx, val_idx in cv.split(X_train, y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr = y_train.iloc[train_idx]
        fold_spw = float((y_tr == 0).sum() / (y_tr == 1).sum())
        fold_model = Pipeline([("imputer", make_imputer()),
                               ("model", XGBClassifier(scale_pos_weight=fold_spw,
                                                        eval_metric="logloss", random_state=42, nthread=1, **_params))])
        fold_model.fit(X_tr, y_tr)
        oof[val_idx] = fold_model.predict_proba(X_val)[:, 1]
    return oof


def _logit(p, eps=1e-6):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def run_cohort(label, nbfile, color):
    nb = json.load(open(nbfile))
    reported_best_name, reported_ap, reported_auc, params_by_model = recover_best_and_all_params(nb)
    ns = {"__name__": "__nb__"}
    _real_show = plt.show
    plt.show = lambda *a, **k: None
    try:
        for c in nb["cells"][:DATA_CELL + 1]:
            if c["cell_type"] == "code":
                exec("".join(c["source"]), ns)
    finally:
        plt.show = _real_show
        plt.close("all")
    X_train, y_train = ns["X_train"], ns["y_train"]
    X_test, y_test = ns["X_test"], ns["y_test"]
    w_test = ns["w_test_arr"]
    make_imputer, make_scaler = ns["make_imputer"], ns["make_scaler"]
    scale_pos_weight = ns["SCALE_POS_WEIGHT"]
    cv = ns["cv"]                       # StratifiedKFold(n_splits=5, shuffle=True, random_state=42), from cell 47

    # ── Reproduce cell 54: OOF probabilities + fitted model for all 5 tuned models ──
    fitted_models, oof_proba_by_model, oof_auprc = {}, {}, {}
    for name, params in params_by_model.items():
        est = build_estimator(name, params, make_imputer, make_scaler, scale_pos_weight)
        if name == "XGBoost":
            oof = xgb_oof_proba(params, X_train, y_train, cv, make_imputer, scale_pos_weight)
        else:
            oof = cross_val_predict(est, X_train, y_train, cv=cv, method="predict_proba")[:, 1]
        oof_proba_by_model[name] = oof
        oof_auprc[name] = average_precision_score(y_train, oof)
        est.fit(X_train, y_train)
        fitted_models[name] = est

    best_name = max(oof_auprc, key=oof_auprc.get)   # rank by OOF AUPRC, matches cell 54
    assert best_name == reported_best_name, \
        f"{label}: recomputed best model {best_name!r} != notebook's reported {reported_best_name!r}"
    best_model = fitted_models[best_name]
    proba_best_raw = best_model.predict_proba(X_test)[:, 1]
    ap = average_precision_score(y_test, proba_best_raw, sample_weight=w_test)
    auc = roc_auc_score(y_test, proba_best_raw, sample_weight=w_test)
    assert abs(ap - reported_ap) < 0.01, f"{label}: AUPRC {ap:.4f} != reported {reported_ap:.4f}"
    assert abs(auc - reported_auc) < 0.01, f"{label}: AUC {auc:.4f} != reported {reported_auc:.4f}"

    # ── Reproduce cell 80: Platt scaling (unpenalised logistic regression on the
    # logit of OOF train probabilities), applied to every model's test probabilities ──
    recal_proba_by_model = {}
    for name, model in fitted_models.items():
        proba_raw = model.predict_proba(X_test)[:, 1]
        recalibrator = LogisticRegression(C=np.inf).fit(
            _logit(oof_proba_by_model[name]).reshape(-1, 1), y_train)
        recal_proba_by_model[name] = recalibrator.predict_proba(_logit(proba_raw).reshape(-1, 1))[:, 1]

    proba_best_recal = recal_proba_by_model[best_name]
    prob_true_recal, prob_pred_recal = calibration_curve(y_test, proba_best_recal, n_bins=N_BINS, strategy="uniform")

    # ── Reproduce cells 84-85: DCA on the recalibrated probabilities, all 5 models ──
    y_test_arr = y_test.to_numpy()
    dca_data = pd.DataFrame({"O_TC_": y_test_arr})
    model_names = list(fitted_models.keys())
    for name in model_names:
        dca_data[name] = recal_proba_by_model[name]
    dca_result = dca(data=dca_data, outcome="O_TC_", modelnames=model_names, thresholds=DCA_THRESHOLDS)
    dca_table = dca_result.pivot(index="threshold", columns="model", values="net_benefit")
    nb_best = dca_table[best_name].to_numpy()
    nb_all = dca_table["all"].to_numpy()
    nb_none = dca_table["none"].to_numpy()

    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f})  n_test {len(y_test)}")
    return dict(label=label, model=best_name, color=color,
                prob_true=prob_true_recal, prob_pred=prob_pred_recal,
                thresholds=dca_table.index.to_numpy(), nb_best=nb_best, nb_all=nb_all, nb_none=nb_none)


def plot(results):
    plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#888888"})
    fig, (ax_cal, ax_dca) = plt.subplots(1, 2, figsize=(15.5, 6.4))

    # ── Left panel: Calibration overlay (Platt-recalibrated, best model per cohort) ──
    ax_cal.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_cal.set_axisbelow(True)
    ax_cal.plot([0, 1], [0, 1], color="#888888", linewidth=1.3,
               linestyle=(0, (5, 4)), alpha=0.8, zorder=2, label="Perfectly calibrated")
    for r in results:
        ax_cal.plot(r["prob_pred"], r["prob_true"], color=r["color"], linewidth=2.2,
                   marker="o", markersize=5.5, markeredgecolor="white", markeredgewidth=0.7,
                   zorder=3, label=f'{r["label"]} · {r["model"]} (Platt-recalibrated)')
    ax_cal.set_xlim(0, 1.0)
    ax_cal.set_ylim(0, 1.02)
    ax_cal.set_xlabel("Mean predicted probability")
    ax_cal.set_ylabel("Observed frequency")
    ax_cal.set_title("Calibration (Platt-recalibrated)", fontsize=12, loc="left")
    ax_cal.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=9.5)
    for s in ("top", "right"):
        ax_cal.spines[s].set_visible(False)

    # ── Right panel: DCA overlay (best model + Treat all / Treat none, per cohort) ──
    ax_dca.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_dca.set_axisbelow(True)
    ax_dca.axhline(0, color="#888888", linewidth=1.3, linestyle=(0, (5, 4)), alpha=0.8,
                   zorder=2, label="Treat none")
    for r in results:
        ax_dca.plot(r["thresholds"], r["nb_all"], color=r["color"], linewidth=1.1,
                   linestyle=(0, (1, 1)), alpha=0.75, zorder=2.5,
                   label=f'Treat all ({r["label"]})')
    for r in results:
        ax_dca.plot(r["thresholds"], r["nb_best"], color=r["color"], linewidth=2.2, zorder=3,
                   label=f'{r["label"]} · {r["model"]} (recalibrated)')
    y_min = min(0, min(r["nb_best"].min() for r in results)) - 0.03
    y_max = max(r["nb_best"].max() for r in results) + 0.03
    ax_dca.set_xlim(DCA_THRESHOLDS[0], DCA_THRESHOLDS[-1])
    ax_dca.set_ylim(y_min, y_max)
    ax_dca.set_xlabel("Threshold probability")
    ax_dca.set_ylabel("Net benefit")
    ax_dca.set_title("Decision Curve Analysis", fontsize=12, loc="left")
    ax_dca.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=8.5)
    for s in ("top", "right"):
        ax_dca.spines[s].set_visible(False)

    fig.suptitle("Cross-cohort calibration & decision-curve analysis — best model per age cohort (2024 test set)",
                 fontsize=12.5, x=0.01, ha="left")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_PNG, dpi=PNG_DPI, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    print(f"\nWrote {OUT_PNG} ({PNG_DPI} dpi) and {OUT_PDF}")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)
