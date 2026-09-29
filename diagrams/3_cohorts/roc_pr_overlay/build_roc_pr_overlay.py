"""
Cross-Cohort ROC + PR Bootstrap Overlay (50+ vs 50-64 vs 65+)
=====================================================================
Single figure, two panels: ROC (left), Precision-Recall (right), each
showing ALL THREE age cohorts on the same axes -- 50+ in blue, 50-64 in
orange, 65+ in red.

Per cohort: 2000 PSU-within-stratum bootstrap resamples of that cohort's
2024 test set (seed 42, matching the notebooks' reported-metric CI method)
drive a percentile-based
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
This rebuilds each cohort's data pipeline, refits the common pinned CatBoost model using
the tuned params already recorded in the notebook, and bootstraps the FIXED
test-set predictions (no refitting per draw -- proba/y_test/w are resampled
together by PSU within survey stratum).

Faithfulness: each notebook uses a deterministic temporal split (train
2020-2023, test 2024) and fixed random_state=42, so the recomputed
AUPRC/AUC (on the full, non-bootstrapped test set) must equal the values
the notebook reports. The script asserts this before drawing.

Run with the same interpreter the notebooks used:
    ~/.pyenv/versions/3.11.9/bin/python build_roc_pr_overlay.py
"""
import os, re, ast, json, contextlib, io
import numpy as np
import pandas as pd
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
MAIN = os.path.join(HERE, "..", "..", "..", "Main")   # repo-root Main/, three levels up from this script
os.chdir(MAIN)                      # notebooks read ../csv/ relative to Main/

# label, notebook file, plot colour (Okabe-Ito blue / orange / true red -- validated CVD-safe trio)
COHORTS = [
    ("50+",    "CB_50+.ipynb",    "#0072B2"),
    ("50-64",  "CB_50-64.ipynb",  "#E69F00"),
    ("65+",    "CB_65+.ipynb",    "#D62728"),
]
# Execute only the cells needed to reconstruct the modeling frame. Notebook cell
# numbers shifted when the screening and inferential sections were revised; a
# positional slice now includes cell 34's full Optuna search, which must not be rerun.
PIPELINE_CELLS = (2, 4, 5, 7, 9, 13, 15, 16, 25, 28, 32)
N_BOOT_DRAW = 2000                  # bootstrap draws used for the mean curve + 95% CI band
                                     # (matches the notebooks' own bootstrap-CI convention, cell 56)
DISPLAY_N_DRAW = 15                 # subsample of N_BOOT_DRAW plotted as individual spaghetti lines
GRID_N = 200                        # points on the common FPR / recall grid used for the mean/CI band
OUT_PNG = os.path.join(HERE, "roc_pr_overlay.png")
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
    """Pinned model name, its reported (survey-weighted) Test AUPRC/AUC, and its
    Optuna-tuned params -- all read live from the notebook's saved outputs, so this
    tracks the notebook without re-running the (expensive) Optuna search. The
    _catboost notebooks HARD-PIN CatBoost across cohorts (cell 44), which need not be
    the OOF-AUPRC leaderboard winner."""
    best_name = reported_ap = reported_auc = None
    for c in nb["cells"]:
        m = re.search(r"Model pinned for cross-cohort SHAP comparability:\s*([A-Za-z ]+?)\s*"
                      r"\(OOF AUPRC\s*=\s*[\d.]+\s*\|\s*Test AUPRC:\s*([\d.]+)\s*\|\s*Test AUC:\s*([\d.]+)",
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


def psu_within_stratum_boot_indices(psu, strata, n_draws, seed=42):
    """Sample PSUs with replacement within each survey stratum."""
    rng = np.random.default_rng(seed)
    cluster_id = pd.factorize(
        pd.Series(strata).astype(int).astype(str) + '_' + pd.Series(psu).astype(str)
    )[0]
    strata_id = pd.factorize(pd.Series(strata).astype(int).astype(str))[0]
    strata_to_clusters = {s: np.unique(cluster_id[strata_id == s])
                          for s in np.unique(strata_id)}
    cluster_to_rows = {c: np.where(cluster_id == c)[0] for c in np.unique(cluster_id)}
    draws = []
    for _ in range(n_draws):
        sampled_rows = []
        for clusters in strata_to_clusters.values():
            sampled = rng.choice(clusters, size=len(clusters), replace=True)
            sampled_rows.extend(cluster_to_rows[c] for c in sampled)
        draws.append(np.concatenate(sampled_rows))
    return draws


def run_cohort(label, nbfile, color):
    nb = json.load(open(nbfile))
    best_name, reported_ap, reported_auc, best_params = recover_best(nb)
    ns = {"__name__": "__nb__"}
    _real_show = plt.show
    plt.show = lambda *a, **k: None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            for i in PIPELINE_CELLS:
                c = nb["cells"][i]
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
    psu_test = ns["df_subset"].loc[ns["test_mask"], "psu"].to_numpy()
    strata_test = ns["df_subset"].loc[ns["test_mask"], "kstrata"].to_numpy()
    assert len(psu_test) == len(y_test) == len(w)

    ap = average_precision_score(y_test, proba, sample_weight=w)
    assert abs(ap - reported_ap) < 0.01, \
        f"{label}: AUPRC {ap:.4f} != reported {reported_ap:.4f} -- pipeline drifted, not drawing."
    auc = roc_auc_score(y_test, proba, sample_weight=w)
    assert abs(auc - reported_auc) < 0.01, \
        f"{label}: AUC {auc:.4f} != reported {reported_auc:.4f} -- pipeline drifted, not drawing."
    baseline = float(np.average(y_test, weights=w))

    # ── Bootstrap the FIXED test-set predictions (no refitting per draw) ──────
    boot_idx = psu_within_stratum_boot_indices(psu_test, strata_test, N_BOOT_DRAW)
    fpr_grid = np.linspace(0, 1, GRID_N)
    rec_grid = np.linspace(0, 1, GRID_N)
    roc_draws, pr_draws = [], []           # only the first DISPLAY_N_DRAW raw curves are kept, for plotting
    tpr_interp_all, prec_interp_all = [], []
    ap_boot, auc_boot = [], []             # per-draw scalar AUPRC/AUC, for the legend's 95% CI
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
        ap_boot.append(average_precision_score(yb, pb, sample_weight=wb))
        auc_boot.append(roc_auc_score(yb, pb, sample_weight=wb))

    tpr_interp_all = np.array(tpr_interp_all)
    prec_interp_all = np.array(prec_interp_all)
    tpr_mean = tpr_interp_all.mean(axis=0)
    prec_mean = prec_interp_all.mean(axis=0)
    tpr_lo, tpr_hi = np.percentile(tpr_interp_all, [2.5, 97.5], axis=0)
    prec_lo, prec_hi = np.percentile(prec_interp_all, [2.5, 97.5], axis=0)
    ap_lo, ap_hi = np.percentile(ap_boot, [2.5, 97.5])
    auc_lo, auc_hi = np.percentile(auc_boot, [2.5, 97.5])

    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f}, "
          f"95% CI {ap_lo:.4f}-{ap_hi:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f}, 95% CI {auc_lo:.4f}-{auc_hi:.4f})  "
          f"n_test {len(y_test)}  n_boot {N_BOOT_DRAW}")
    return dict(label=label, model=best_name, color=color, baseline=baseline,
                ap=ap, auc=auc, ap_lo=ap_lo, ap_hi=ap_hi, auc_lo=auc_lo, auc_hi=auc_hi,
                roc_draws=roc_draws, pr_draws=pr_draws,
                fpr_grid=fpr_grid, tpr_mean=tpr_mean, tpr_lo=tpr_lo, tpr_hi=tpr_hi,
                rec_grid=rec_grid, prec_mean=prec_mean, prec_lo=prec_lo, prec_hi=prec_hi)


class _SplitBandHandler(HandlerBase):
    """Legend handler for the shared '95% CI' entry: draws a borderless patch
    split into N equal vertical strips, one per cohort colour, all at the same
    alpha as the plotted fill_between bands -- since all cohorts share this one
    legend row, the swatch itself carries the per-cohort colour split."""
    def __init__(self, colors, alpha):
        super().__init__()
        self.colors = colors
        self.alpha = alpha

    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        n = len(self.colors)
        strip_w = width / n
        return [Rectangle((-xdescent + i * strip_w, -ydescent), strip_w, height,
                          facecolor=c, alpha=self.alpha, linewidth=0, transform=trans)
                for i, c in enumerate(self.colors)]


def plot(results):
    plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#888888"})
    fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(15.5, 6.4))
    cohort_colors = [r["color"] for r in results]

    # ── Left panel: ROC overlay ─────────────────────────────────────────────
    ax_roc.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_roc.set_axisbelow(True)
    ax_roc.plot([0, 1], [0, 1], color="#888888", linewidth=1.3,
               linestyle=(0, (5, 4)), alpha=0.8, zorder=2, label="Chance")
    for r in results:
        for fpr_b, tpr_b in r["roc_draws"]:
            ax_roc.plot(fpr_b, tpr_b, color=r["color"], linewidth=0.7, alpha=0.30, zorder=2.5)
        ax_roc.plot(r["fpr_grid"], r["tpr_mean"], color=r["color"], linewidth=2.4, zorder=3,
                   label=f'{r["label"]} · {r["model"]}  (AUC {r["auc"]:.3f} ({r["auc_lo"]:.3f} - {r["auc_hi"]:.3f}))')
        ax_roc.fill_between(r["fpr_grid"], r["tpr_lo"], r["tpr_hi"],
                            color=r["color"], alpha=0.15, zorder=1.5, linewidth=0)
    ax_roc.set_xlim(0, 1.0)
    ax_roc.set_ylim(0, 1.02)
    ax_roc.set_xlabel("False Positive Rate")
    ax_roc.set_ylabel("True Positive Rate")
    ax_roc.set_title("Receiver Operating Characteristic", fontsize=12, loc="left")
    # shared "95% CI" entry: a proxy handle rendered by _SplitBandHandler as an N-way split patch
    roc_handles, roc_labels = ax_roc.get_legend_handles_labels()
    roc_ci_proxy = Rectangle((0, 0), 1, 1)
    roc_handles.append(roc_ci_proxy)
    roc_labels.append("95% CI")
    ax_roc.legend(roc_handles, roc_labels, handler_map={roc_ci_proxy: _SplitBandHandler(cohort_colors, 0.15)},
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
                   label=f'{r["label"]} · {r["model"]}  (AUPRC {r["ap"]:.3f} ({r["ap_lo"]:.3f} - {r["ap_hi"]:.3f}))')
        ax_pr.fill_between(r["rec_grid"], r["prec_lo"], r["prec_hi"],
                           color=r["color"], alpha=0.15, zorder=1.5, linewidth=0)
    # one representative "Chance" legend entry for both (differently-valued) baselines
    ax_pr.plot([], [], color="#888888", linewidth=1.3, linestyle=(0, (5, 4)), alpha=0.8, label="Chance")
    ax_pr.set_xlim(0, 1.0)
    ax_pr.set_ylim(0, 1.02)
    ax_pr.set_xlabel("Recall  (of tooth-loss cases, <20 teeth)")
    ax_pr.set_ylabel("Precision")
    ax_pr.set_title("Precision–Recall", fontsize=12, loc="left")
    # shared "95% CI" entry: a proxy handle rendered by _SplitBandHandler as an N-way split patch
    pr_handles, pr_labels = ax_pr.get_legend_handles_labels()
    pr_ci_proxy = Rectangle((0, 0), 1, 1)
    pr_handles.append(pr_ci_proxy)
    pr_labels.append("95% CI")
    ax_pr.legend(pr_handles, pr_labels, handler_map={pr_ci_proxy: _SplitBandHandler(cohort_colors, 0.15)},
                loc="upper right", frameon=True, framealpha=0.9, fontsize=9.5)
    for s in ("top", "right"):
        ax_pr.spines[s].set_visible(False)

    fig.suptitle(f"Cross-cohort AUROC & AUPRC — common CatBoost model, "
                 f"{N_BOOT_DRAW} bootstrap resamples of the 2024 test set (mean, 95% CI)",
                 fontsize=12.5, x=0.01, ha="left")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_PNG, dpi=PNG_DPI, bbox_inches="tight")
    print(f"\nWrote {OUT_PNG} ({PNG_DPI} dpi)")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)
