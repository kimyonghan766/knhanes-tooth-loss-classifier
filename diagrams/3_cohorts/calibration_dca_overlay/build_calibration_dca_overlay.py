"""
Cross-Cohort Calibration + DCA Overlay (50+ vs 50-64 vs 65+)
=====================================================================
Single figure, two panels: Platt-recalibrated calibration curve (left),
Decision Curve Analysis / net benefit (right), each showing ALL THREE age
cohorts on the same axes -- 50+ in blue, 50-64 in orange, 65+ in red (the
common pinned CatBoost model). Both panels reuse the notebooks' algorithms
verbatim (cells 54, 80, 84-85 of Main/CB_50+.ipynb / CB_50-64.ipynb / CB_65+.ipynb):

  - Calibration: the development-fitted Platt slope and intercept saved by each
    revised notebook from tuning-independent nested OOF predictions -> apply to
    the TEST set -> 10-bin
    calibration curve on the common CatBoost model's recalibrated probabilities. A 95%
    CI band is added around this by bootstrapping the FIXED (y_test,
    recalibrated proba, wt_itvex) values 2000 times by PSU within stratum
    (seed 42), recomputing the weighted-bin calibration curve per draw and
    interpolating each draw onto a common predicted-probability
    grid; the plotted center line is the bootstrap mean curve (not the
    single-fit curve) and the band is the 2.5th-97.5th percentile across
    draws.
  - DCA: net benefit of the common CatBoost model's recalibrated probabilities across
    thresholds 0.01-0.50 (dcurves), alongside "Treat all" (differs by
    cohort prevalence) and "Treat none" (0 for both) reference lines. No
    bootstrap band on this panel.

Why a separate script (not a notebook cell): each notebook only plots its own
cohort. Re-running the notebooks' nested Optuna searches would be needlessly
expensive, so this script recovers the final CatBoost best_params and the
nested-OOF Platt mapping coefficients from the notebooks' saved outputs. It
then reproduces the test-set calibration and DCA without re-searching.

Faithfulness: each notebook uses a deterministic temporal split (train
2020-2023, test 2024) and fixed random_state=42. The recomputed common-model
Test AUPRC/AUC must equal the values the notebook reports, and the recovered
pinned model name and Platt mapping must exist. The script asserts these
conditions before drawing.

Run with the same interpreter the notebooks used:
    ~/.pyenv/versions/3.11.9/bin/python build_calibration_dca_overlay.py
"""
import os, re, ast, json, contextlib, io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from dcurves import dca

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "..", "Main")   # repo-root Main/, three levels up from this script
os.chdir(MAIN)                      # notebooks read ../csv/ relative to Main/

# label, notebook file, plot colour (Okabe-Ito blue / orange / true red -- validated CVD-safe trio)
COHORTS = [
    ("≥50",    "CB_50+.ipynb",    "#0072B2"),
    ("50–64",  "CB_50-64.ipynb",  "#E69F00"),
    ("≥65",    "CB_65+.ipynb",    "#D62728"),
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
N_BINS = 10                         # matches the notebooks' calibration_curve(..., n_bins=10, strategy='uniform')
DCA_THRESHOLDS = np.arange(0.01, 0.51, 0.01)   # matches notebook cell 84's dca_thresholds
N_BOOT_DRAW = 2000                  # bootstrap draws for the calibration curve's 95% CI band
                                     # (matches the notebooks' own bootstrap-CI convention, cell 56)
GRID_N = 200                        # points on the common predicted-probability grid for the CI band
OUT_PNG = os.path.join(HERE, "calibration_dca_overlay.png")
PNG_DPI = 600                       # Elsevier-grade combination art

# Match the cross-cohort SHAP summary's source-figure typography.
FS_FALLBACK = 9                     # global fallback text
FS_BASE = 10                        # tick labels and ordinary annotations
FS_AXIS = 10                        # axis titles
FS_TITLE = 11                       # panel titles and figure title
FS_LEGEND = 10


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


def recover_best_params_and_platt(nb):
    """Pinned model name + reported Test AUPRC/AUC (from cell 44's printed summary line),
    and every tuned model's best_params + CV AUPRC (from cell 39's printed lines) --
    all read live from the notebook's saved outputs, never re-searched. The _catboost
    notebooks HARD-PIN CatBoost across cohorts (cell 44); this need not be the
    OOF-AUPRC leaderboard winner (for the 65+ cohort it is not)."""
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
    assert best_name in params_by_model, f"best model {best_name!r} missing from parsed params"

    calibration_txt = next(
        cell_output_text(c) for c in nb["cells"]
        if "Development-fitted Platt mapping" in cell_output_text(c)
    )
    platt_by_model = {}
    for name in params_by_model:
        for line in calibration_txt.split("\n"):
            m = re.match(rf"^{re.escape(name)}\s+(-?[\d.]+)\s+(-?[\d.]+)\s+", line.strip())
            if m:
                platt_by_model[name] = (float(m.group(1)), float(m.group(2)))
                break
    assert best_name in platt_by_model, \
        f"pinned model {best_name!r} missing from saved Platt mapping table"
    dca_txt = next(
        cell_output_text(c) for c in nb["cells"]
        if "threshold" in cell_output_text(c) and "Random Forest" in cell_output_text(c)
        and "CatBoost" in cell_output_text(c) and "none" in cell_output_text(c)
    )
    saved_catboost_dca = {}
    for line in dca_txt.split("\n"):
        fields = line.split()
        if len(fields) >= 8 and re.fullmatch(r"0\.\d{2}", fields[0]):
            # Printed order is threshold, RF, XGBoost, LightGBM, CatBoost, LR, all, none.
            saved_catboost_dca[float(fields[0])] = float(fields[4])
    assert len(saved_catboost_dca) == len(DCA_THRESHOLDS), \
        f"expected {len(DCA_THRESHOLDS)} saved CatBoost DCA rows, found {len(saved_catboost_dca)}"
    return (best_name, reported_ap, reported_auc, params_by_model[best_name],
            platt_by_model[best_name], saved_catboost_dca)


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
                                                      solver="saga", max_iter=5000, random_state=42, **params))])
    raise ValueError(name)


def _logit(p, eps=1e-6):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


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


def weighted_calibration_curve(y_true, y_prob, weight, n_bins=10):
    """Uniform-bin calibration curve using interview-weighted bin means."""
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_idx = np.clip(np.digitize(y_prob, edges[1:-1]), 0, n_bins - 1)
    prob_true, prob_pred = [], []
    for b in range(n_bins):
        mask = bin_idx == b
        if not mask.any():
            continue
        wb = weight[mask]
        prob_true.append(np.average(y_true[mask], weights=wb))
        prob_pred.append(np.average(y_prob[mask], weights=wb))
    return np.asarray(prob_true), np.asarray(prob_pred)


def run_cohort(label, nbfile, color):
    nb = json.load(open(nbfile))
    best_name, reported_ap, reported_auc, best_params, platt_mapping, saved_dca = \
        recover_best_params_and_platt(nb)
    ns = {"__name__": "__nb__"}
    _real_show = plt.show
    plt.show = lambda *a, **k: None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            for c in pipeline_cells(nb):
                exec("".join(c["source"]), ns)
    finally:
        plt.show = _real_show
        plt.close("all")
    X_train, y_train = ns["X_train"], ns["y_train"]
    X_test, y_test = ns["X_test"], ns["y_test"]
    w_test = ns["w_test_arr"]
    make_imputer, make_scaler = ns["make_imputer"], ns["make_scaler"]
    scale_pos_weight = ns["SCALE_POS_WEIGHT"]
    # Refit the notebook's common pinned model with its final full-development
    # hyperparameters. The development Platt mapping itself is read from the saved
    # nested-OOF calibration output above, so no optimistic ordinary-CV OOF loop is used.
    best_model = build_estimator(
        best_name, best_params, make_imputer, make_scaler, scale_pos_weight
    )
    best_model.fit(X_train, y_train)
    proba_best_raw = best_model.predict_proba(X_test)[:, 1]
    ap = average_precision_score(y_test, proba_best_raw, sample_weight=w_test)
    auc = roc_auc_score(y_test, proba_best_raw, sample_weight=w_test)
    assert abs(ap - reported_ap) < 0.01, f"{label}: AUPRC {ap:.4f} != reported {reported_ap:.4f}"
    assert abs(auc - reported_auc) < 0.01, f"{label}: AUC {auc:.4f} != reported {reported_auc:.4f}"

    # Apply the exact slope/intercept fitted by the notebook from tuning-independent
    # nested OOF predictions: sigmoid(intercept + slope * logit(raw probability)).
    platt_slope, platt_intercept = platt_mapping
    platt_linear = platt_intercept + platt_slope * _logit(proba_best_raw)
    proba_best_recal = 1.0 / (1.0 + np.exp(-platt_linear))
    y_test_arr = y_test.to_numpy()
    psu_test = ns["df_subset"].loc[ns["test_mask"], "psu"].to_numpy()
    strata_test = ns["df_subset"].loc[ns["test_mask"], "kstrata"].to_numpy()
    assert len(psu_test) == len(y_test_arr) == len(w_test)

    # ── Bootstrap the FIXED (y_test, recalibrated proba) pairs for a 95% CI band ──
    # No refitting/re-recalibrating per draw. PSUs are sampled within strata and
    # respondents retain their original interview weights. Each weighted-bin curve
    # is interpolated onto a common grid for the bootstrap mean and percentile band.
    boot_idx = psu_within_stratum_boot_indices(psu_test, strata_test, N_BOOT_DRAW)
    prob_grid = np.linspace(0, 1, GRID_N)
    true_interp_all = []
    for bi in boot_idx:
        yb, pb, wb = y_test_arr[bi], proba_best_recal[bi], w_test[bi]
        prob_true_b, prob_pred_b = weighted_calibration_curve(yb, pb, wb, n_bins=N_BINS)
        true_interp_all.append(np.interp(prob_grid, prob_pred_b, prob_true_b))
    true_interp_all = np.array(true_interp_all)
    prob_true_mean = true_interp_all.mean(axis=0)
    prob_true_lo, prob_true_hi = np.percentile(true_interp_all, [2.5, 97.5], axis=0)

    # ── Reproduce the pinned-model DCA on recalibrated probabilities ────────────
    dca_data = pd.DataFrame({"O_TC_": y_test_arr})
    dca_data[best_name] = proba_best_recal
    dca_result = dca(
        data=dca_data, outcome="O_TC_", modelnames=[best_name],
        thresholds=DCA_THRESHOLDS
    )
    dca_table = dca_result.pivot(index="threshold", columns="model", values="net_benefit")
    nb_best = dca_table[best_name].to_numpy()
    nb_all = dca_table["all"].to_numpy()
    nb_none = dca_table["none"].to_numpy()

    dca_drift = max(
        abs(float(dca_table.loc[t, best_name]) - saved_dca[round(float(t), 2)])
        for t in DCA_THRESHOLDS
    )
    assert dca_drift < 0.002, \
        f"{label}: regenerated DCA differs from saved notebook output by {dca_drift:.4f}"
    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f})  n_test {len(y_test)}  "
          f"n_boot {N_BOOT_DRAW}  max saved-DCA drift {dca_drift:.4f}")
    return dict(label=label, model=best_name, color=color,
                prob_grid=prob_grid, prob_true_mean=prob_true_mean,
                prob_true_lo=prob_true_lo, prob_true_hi=prob_true_hi,
                thresholds=dca_table.index.to_numpy(), nb_best=nb_best, nb_all=nb_all, nb_none=nb_none)


def plot(results):
    from matplotlib.lines import Line2D

    plt.rcParams.update({"font.size": FS_FALLBACK, "axes.edgecolor": "#888888"})
    fig, (ax_cal, ax_dca) = plt.subplots(1, 2, figsize=(15.5, 6.4))

    # ── Left panel: Calibration overlay (Platt-recalibrated, best model per cohort) ──
    ax_cal.grid(True, color="#000000", alpha=0.08, linewidth=0.8)
    ax_cal.set_axisbelow(True)
    ax_cal.plot([0, 1], [0, 1], color="#888888", linewidth=1.3,
               linestyle=(0, (5, 4)), alpha=0.8, zorder=2, label="Perfectly calibrated")
    for r in results:
        ax_cal.plot(r["prob_grid"], r["prob_true_mean"], color=r["color"], linewidth=2.2,
                   zorder=3, label=r["label"])
    ax_cal.set_xlim(0, 1.0)
    ax_cal.set_ylim(0, 1.02)
    _unit_ticks = np.linspace(0, 1, 6)
    ax_cal.set_xticks(_unit_ticks)
    ax_cal.set_yticks(_unit_ticks)
    ax_cal.set_xticklabels([f"{v:.1f}" for v in _unit_ticks], fontsize=FS_BASE)
    ax_cal.set_yticklabels([f"{v:.1f}" for v in _unit_ticks], fontsize=FS_BASE)
    ax_cal.tick_params(axis="both", labelcolor="black", labelleft=True, labelbottom=True)
    ax_cal.set_xlabel("Mean predicted probability", fontsize=FS_AXIS)
    ax_cal.set_ylabel("Observed frequency", fontsize=FS_AXIS)
    ax_cal.set_title("Calibration (Platt-recalibrated)", fontsize=FS_TITLE, loc="left")
    ax_cal.legend(loc="upper left", frameon=True, framealpha=0.9,
                  fontsize=FS_LEGEND)
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
    ax_dca.set_xlabel("Threshold probability", fontsize=FS_AXIS)
    ax_dca.set_ylabel("Net benefit", fontsize=FS_AXIS)
    ax_dca.set_title("Decision Curve Analysis", fontsize=FS_TITLE, loc="left")
    cohort_handles = [
        Line2D([0], [0], color=r["color"], linewidth=2.2, label=r["label"])
        for r in results
    ]
    strategy_handles = [
        Line2D([0], [0], color="#333333", linewidth=2.2, label="Model"),
        Line2D([0], [0], color="#666666", linewidth=1.1,
               linestyle=(0, (1, 1)), label="Treat all"),
        Line2D([0], [0], color="#888888", linewidth=1.3,
               linestyle=(0, (5, 4)), label="Treat none"),
    ]
    cohort_legend = ax_dca.legend(handles=cohort_handles, loc="upper right",
                                  frameon=True, framealpha=0.9,
                                  fontsize=FS_LEGEND, title="Cohort",
                                  title_fontsize=FS_LEGEND)
    ax_dca.add_artist(cohort_legend)
    ax_dca.legend(handles=strategy_handles, loc="lower left",
                  frameon=True, framealpha=0.9,
                  fontsize=FS_LEGEND, title="Strategy",
                  title_fontsize=FS_LEGEND)
    for s in ("top", "right"):
        ax_dca.spines[s].set_visible(False)

    fig.suptitle("Cross-cohort calibration & decision-curve analysis — common CatBoost model (2024 test set)",
                 fontsize=FS_TITLE, x=0.5, ha="center")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_PNG, dpi=PNG_DPI, bbox_inches="tight")
    print(f"\nWrote {OUT_PNG} ({PNG_DPI} dpi)")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)
