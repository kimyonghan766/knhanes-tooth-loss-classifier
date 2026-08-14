"""
Cross-Cohort ROC + PR Bootstrap Overlay (50+ vs 65+)
=====================================================================
Single figure, two panels: ROC (left), Precision-Recall (right), each
showing BOTH age cohorts on the same axes -- 50+ in blue, 65+ in red.

Per cohort: 2000 stratified bootstrap resamples of that cohort's 2024 test
set (prevalence-preserving, seed 42, same recipe -- and same draw count --
as the notebooks' own bootstrap-CI cell, cell 56) drive a percentile-based
95% CI band (2.5th-97.5th percentile across all 2000 draws, interpolated
onto a common grid) as a shaded region, with the mean curve as a bold line.
A subsample of 15 of the 2000 draws are additionally drawn as thin
translucent lines in the cohort's colour, purely for visual texture -- the
CI band itself is computed from the full 2000. The chance/
random-guessing reference (diagonal for ROC, prevalence line for PR) is
drawn in neutral gray -- red and blue are reserved for cohort identity,
not for baseline-vs-model contrast as in a single-cohort figure.

Why a separate script (not a notebook cell): each notebook only plots its
own cohort's curves, from a single fit, with no bootstrap variability band.
This rebuilds each cohort's data pipeline, refits only its best model using
the tuned params already recorded in the notebook, and bootstraps the FIXED
test-set predictions (no refitting per draw -- proba/y_test/w are resampled
together, matching the notebook's existing stratified-bootstrap idiom).

Faithfulness: each notebook uses a deterministic temporal split (train
2020-2023, test 2024) and fixed random_state=42, so the recomputed
AUPRC/AUC (on the full, non-bootstrapped test set) must equal the values
the notebook reports. The script asserts this before drawing.

Run with the same interpreter the notebooks used:
    ~/.pyenv/versions/3.11.9/bin/python build_roc_pr_overlay.py
"""
import os, re, ast, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.legend_handler import HandlerBase

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (precision_recall_curve, average_precision_score,
                              roc_curve, roc_auc_score)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "Main")   # repo-root Main/, two levels up from this script
os.chdir(MAIN)                      # notebooks read ../csv/ relative to Main/

# label, notebook file, plot colour (Okabe-Ito blue / true red -- validated CVD-safe pair)
COHORTS = [
    ("50+",  "final.ipynb",       "#0072B2"),
    ("65+",  "final(65+).ipynb",  "#D62728"),
]
DATA_CELL = 47                      # cell that defines X_train/X_test/y_train/y_test/w_test_arr,
                                     # make_imputer, make_scaler and SCALE_POS_WEIGHT
N_BOOT_DRAW = 2000                  # bootstrap draws used for the mean curve + 95% CI band
                                     # (matches the notebooks' own bootstrap-CI convention, cell 56)
DISPLAY_N_DRAW = 15                 # subsample of N_BOOT_DRAW plotted as individual spaghetti lines
GRID_N = 200                        # points on the common FPR / recall grid used for the mean/CI band
OUT_PNG = os.path.join(HERE, "roc_pr_overlay.png")
OUT_PDF = os.path.join(HERE, "roc_pr_overlay.pdf")
PNG_DPI = 600                       # Elsevier-grade combination art


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
    Optuna-tuned params -- all read live from the notebook's saved outputs, so this
    tracks the notebook without re-running the (expensive) Optuna search."""
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
    return best_name, reported_ap, reported_auc, params_by_model[best_name]


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


def stratified_boot_indices(y, n_draws, seed=42):
    """Prevalence-preserving bootstrap of row indices -- same recipe as the
    notebooks' _boot_idx (cell 56): resample the outcome-0 and outcome-1 rows
    separately (with replacement) so every draw keeps the same class balance."""
    rng = np.random.default_rng(seed)
    idx0 = np.where(y == 0)[0]
    idx1 = np.where(y == 1)[0]
    return [np.concatenate([rng.choice(idx0, idx0.size, replace=True),
                            rng.choice(idx1, idx1.size, replace=True)])
            for _ in range(n_draws)]


def run_cohort(label, nbfile, color):
    nb = json.load(open(nbfile))
    best_name, reported_ap, reported_auc, best_params = recover_best(nb)
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
    est = build_estimator(best_name, best_params, ns["make_imputer"], ns["make_scaler"],
                          ns["SCALE_POS_WEIGHT"])
    est.fit(ns["X_train"], ns["y_train"])
    proba = est.predict_proba(ns["X_test"])[:, 1]
    y_test = ns["y_test"].to_numpy()
    w = ns["w_test_arr"]

    ap = average_precision_score(y_test, proba, sample_weight=w)
    assert abs(ap - reported_ap) < 0.01, \
        f"{label}: AUPRC {ap:.4f} != reported {reported_ap:.4f} -- pipeline drifted, not drawing."
    auc = roc_auc_score(y_test, proba, sample_weight=w)
    assert abs(auc - reported_auc) < 0.01, \
        f"{label}: AUC {auc:.4f} != reported {reported_auc:.4f} -- pipeline drifted, not drawing."
    baseline = float(np.average(y_test, weights=w))

    # ── Bootstrap the FIXED test-set predictions (no refitting per draw) ──────
    boot_idx = stratified_boot_indices(y_test, N_BOOT_DRAW)
    fpr_grid = np.linspace(0, 1, GRID_N)
    rec_grid = np.linspace(0, 1, GRID_N)
    roc_draws, pr_draws = [], []           # only the first DISPLAY_N_DRAW raw curves are kept, for plotting
    tpr_interp_all, prec_interp_all = [], []
    for i, bi in enumerate(boot_idx):
        yb, pb, wb = y_test[bi], proba[bi], w[bi]
        fpr_b, tpr_b, _ = roc_curve(yb, pb, sample_weight=wb)
        prec_b, rec_b, _ = precision_recall_curve(yb, pb, sample_weight=wb)
        if i < DISPLAY_N_DRAW:
            roc_draws.append((fpr_b, tpr_b))
            pr_draws.append((rec_b, prec_b))
        tpr_interp_all.append(np.interp(fpr_grid, fpr_b, tpr_b))
        order = np.argsort(rec_b)
        prec_interp_all.append(np.interp(rec_grid, rec_b[order], prec_b[order]))

    tpr_interp_all = np.array(tpr_interp_all)
    prec_interp_all = np.array(prec_interp_all)
    tpr_mean = tpr_interp_all.mean(axis=0)
    prec_mean = prec_interp_all.mean(axis=0)
    tpr_lo, tpr_hi = np.percentile(tpr_interp_all, [2.5, 97.5], axis=0)
    prec_lo, prec_hi = np.percentile(prec_interp_all, [2.5, 97.5], axis=0)

    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f})  n_test {len(y_test)}  "
          f"n_boot {N_BOOT_DRAW}")
    return dict(label=label, model=best_name, color=color, baseline=baseline,
                ap=ap, auc=auc,
                roc_draws=roc_draws, pr_draws=pr_draws,
                fpr_grid=fpr_grid, tpr_mean=tpr_mean, tpr_lo=tpr_lo, tpr_hi=tpr_hi,
                rec_grid=rec_grid, prec_mean=prec_mean, prec_lo=prec_lo, prec_hi=prec_hi)


class _SplitBandHandler(HandlerBase):
    """Legend handler for the shared '95% CI' entry: draws a borderless patch,
    left half in `left_color` (50+), right half in `right_color` (65+), both at
    the same alpha as the plotted fill_between bands -- since both cohorts share
    this one legend row, the swatch itself carries the per-cohort colour split."""
    def __init__(self, left_color, right_color, alpha):
        super().__init__()
        self.left_color = left_color
        self.right_color = right_color
        self.alpha = alpha

    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        left = Rectangle((-xdescent, -ydescent), width / 2, height,
                         facecolor=self.left_color, alpha=self.alpha, linewidth=0, transform=trans)
        right = Rectangle((-xdescent + width / 2, -ydescent), width / 2, height,
                          facecolor=self.right_color, alpha=self.alpha, linewidth=0, transform=trans)
        return [left, right]


def plot(results):
    plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#888888"})
    fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(15.5, 6.4))
    blue_color = next(r["color"] for r in results if r["label"] == "50+")
    red_color = next(r["color"] for r in results if r["label"] == "65+")

    # ── Left panel: ROC overlay ─────────────────────────────────────────────
    ax_roc.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_roc.set_axisbelow(True)
    ax_roc.plot([0, 1], [0, 1], color="#888888", linewidth=1.3,
               linestyle=(0, (5, 4)), alpha=0.8, zorder=2, label="Chance")
    for r in results:
        for fpr_b, tpr_b in r["roc_draws"]:
            ax_roc.plot(fpr_b, tpr_b, color=r["color"], linewidth=0.7, alpha=0.30, zorder=2.5)
        ax_roc.plot(r["fpr_grid"], r["tpr_mean"], color=r["color"], linewidth=2.4, zorder=3,
                   label=f'{r["label"]} · {r["model"]}  (AUC {r["auc"]:.3f})')
        ax_roc.fill_between(r["fpr_grid"], r["tpr_lo"], r["tpr_hi"],
                            color=r["color"], alpha=0.15, zorder=1.5, linewidth=0)
    ax_roc.set_xlim(0, 1.0)
    ax_roc.set_ylim(0, 1.02)
    ax_roc.set_xlabel("False Positive Rate")
    ax_roc.set_ylabel("True Positive Rate")
    ax_roc.set_title("Receiver Operating Characteristic", fontsize=12, loc="left")
    # shared "95% CI" entry: a proxy handle rendered by _SplitBandHandler as a blue/red split patch
    roc_handles, roc_labels = ax_roc.get_legend_handles_labels()
    roc_ci_proxy = Rectangle((0, 0), 1, 1)
    roc_handles.append(roc_ci_proxy)
    roc_labels.append("95% CI")
    ax_roc.legend(roc_handles, roc_labels, handler_map={roc_ci_proxy: _SplitBandHandler(blue_color, red_color, 0.15)},
                 loc="lower right", frameon=True, framealpha=0.9, fontsize=9.5)
    for s in ("top", "right"):
        ax_roc.spines[s].set_visible(False)

    # ── Right panel: PR overlay ─────────────────────────────────────────────
    ax_pr.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_pr.set_axisbelow(True)
    for r in results:
        ax_pr.axhline(r["baseline"], color="#888888", linewidth=1.3,
                      linestyle=(0, (5, 4)), alpha=0.8, zorder=2)
    for r in results:
        for rec_b, prec_b in r["pr_draws"]:
            ax_pr.plot(rec_b, prec_b, color=r["color"], linewidth=0.7, alpha=0.30, zorder=2.5)
        ax_pr.plot(r["rec_grid"], r["prec_mean"], color=r["color"], linewidth=2.4, zorder=3,
                   label=f'{r["label"]} · {r["model"]}  (AUPRC {r["ap"]:.3f})')
        ax_pr.fill_between(r["rec_grid"], r["prec_lo"], r["prec_hi"],
                           color=r["color"], alpha=0.15, zorder=1.5, linewidth=0)
    # one representative "Chance" legend entry for both (differently-valued) baselines
    ax_pr.plot([], [], color="#888888", linewidth=1.3, linestyle=(0, (5, 4)), alpha=0.8, label="Chance")
    ax_pr.set_xlim(0, 1.0)
    ax_pr.set_ylim(0, 1.02)
    ax_pr.set_xlabel("Recall  (of tooth-loss cases, <20 teeth)")
    ax_pr.set_ylabel("Precision")
    ax_pr.set_title("Precision–Recall", fontsize=12, loc="left")
    # shared "95% CI" entry: a proxy handle rendered by _SplitBandHandler as a blue/red split patch
    pr_handles, pr_labels = ax_pr.get_legend_handles_labels()
    pr_ci_proxy = Rectangle((0, 0), 1, 1)
    pr_handles.append(pr_ci_proxy)
    pr_labels.append("95% CI")
    ax_pr.legend(pr_handles, pr_labels, handler_map={pr_ci_proxy: _SplitBandHandler(blue_color, red_color, 0.15)},
                loc="upper right", frameon=True, framealpha=0.9, fontsize=9.5)
    for s in ("top", "right"):
        ax_pr.spines[s].set_visible(False)

    fig.suptitle(f"Cross-cohort AUROC & AUPRC — best model per age cohort, "
                 f"{N_BOOT_DRAW} bootstrap resamples of the 2024 test set (mean, 95% CI)",
                 fontsize=12.5, x=0.01, ha="left")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_PNG, dpi=PNG_DPI, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    print(f"\nWrote {OUT_PNG} ({PNG_DPI} dpi) and {OUT_PDF}")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)
