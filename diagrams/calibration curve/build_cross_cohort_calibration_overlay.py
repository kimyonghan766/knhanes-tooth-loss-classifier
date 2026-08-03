"""
Cross-Cohort Calibration Overlay (50+ vs 65+) — Elsevier submission figure
=============================================================================
Single-column figure (90 mm wide, Elsevier artwork spec): a reliability
diagram overlaying the best model's calibration curve for the 50+ cohort and
the 65+ cohort, with a marginal histogram strip per cohort showing the
distribution of predicted probabilities that feed each calibration bin.

Why a separate script (not a notebook cell): each notebook only plots its own
cohort's calibration curves (all 5 tuned models). This rebuilds each cohort's
data pipeline, refits only its best model using the tuned params already
recorded in the notebook, and overlays just the two best models.

Faithfulness: each notebook uses a deterministic temporal split (train
2020-2023, test 2024) and fixed random_state=42. The refit AUPRC/AUC are
asserted against the notebook-reported values before drawing — this is the
same model object the calibration curve and Brier score are computed from,
so a passing assert also validates the calibration numbers.

Elsevier artwork spec targeted (Journal of Dentistry guide for authors ->
general Elsevier artwork instructions, no journal-specific override found):
  - combination art (line + color) >= 500 dpi
  - single column width = 90 mm
  - lettering ~7 pt at final printed size (figure is rendered directly at
    physical print size, so rcParams font sizes ARE the printed point sizes)

Run with the same interpreter the notebooks used:
    ~/.pyenv/versions/3.11.9/bin/python build_cross_cohort_calibration_overlay.py
"""
import os, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (average_precision_score, roc_auc_score,
                              brier_score_loss)
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
DATA_CELL = 40                      # cell that defines X_train/X_test/y_train/y_test + make_imputer
N_BINS = 10                         # matches the notebooks' calibration_curve(..., n_bins=10, strategy='uniform')
MM_PER_IN = 25.4
FIG_WIDTH_MM = 90                   # Elsevier single-column width
OUT_BASENAME = os.path.join(HERE, "cross_cohort_calibration_overlay")


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
    est = build_estimator(best_name, best_params, ns["make_imputer"])
    est.fit(ns["X_train"], ns["y_train"])
    proba = est.predict_proba(ns["X_test"])[:, 1]
    y_test = ns["y_test"]

    ap = average_precision_score(y_test, proba)
    assert abs(ap - reported_ap) < 0.01, \
        f"{label}: AUPRC {ap:.4f} != reported {reported_ap:.4f} — pipeline drifted, not drawing."
    auc = roc_auc_score(y_test, proba)
    assert abs(auc - reported_auc) < 0.01, \
        f"{label}: AUC {auc:.4f} != reported {reported_auc:.4f} — pipeline drifted, not drawing."

    brier = brier_score_loss(y_test, proba)
    prob_true, prob_pred = calibration_curve(y_test, proba, n_bins=N_BINS, strategy="uniform")

    print(f"[{label}] {best_name}: AUPRC {ap:.4f} (reported {reported_ap:.4f})  "
          f"AUC {auc:.4f} (reported {reported_auc:.4f})  Brier {brier:.4f}  n_test {len(y_test)}")
    return dict(label=label, model=best_name, proba=proba, brier=brier,
                prob_true=prob_true, prob_pred=prob_pred, color=color)


def plot(results):
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7,
        "axes.edgecolor": "#888888",
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "pdf.fonttype": 42,          # embed as real (editable/selectable) text, not outlines
        "ps.fonttype": 42,
    })
    fig_w = FIG_WIDTH_MM / MM_PER_IN
    fig_h = fig_w * 1.18
    fig, (ax_cal, ax_h1, ax_h2) = plt.subplots(
        3, 1, figsize=(fig_w, fig_h), sharex=True,
        gridspec_kw={"height_ratios": [3.0, 0.62, 0.62], "hspace": 0.10})

    # bin edges, for light reference gridlines shared by all three panels
    edges = np.linspace(0, 1, N_BINS + 1)

    # ── Top: calibration curve overlay ──────────────────────────────────
    for e in edges:
        ax_cal.axvline(e, color="#000000", alpha=0.05, linewidth=0.5, zorder=1)
    ax_cal.plot([0, 1], [0, 1], color="#888888", linewidth=1.0,
               linestyle=(0, (4, 3)), zorder=2, label="Perfectly calibrated")
    for r in results:
        ax_cal.plot(r["prob_pred"], r["prob_true"], color=r["color"], linewidth=1.4,
                   marker="o", markersize=3.2, markeredgecolor="white", markeredgewidth=0.4,
                   zorder=3, label=f'{r["label"]} · {r["model"]} (Brier {r["brier"]:.3f})')
    ax_cal.set_xlim(0, 1)
    ax_cal.set_ylim(0, 1)
    ax_cal.set_ylabel("Observed frequency")
    ax_cal.set_title("Calibration — best model per age cohort (2024 test set)",
                     fontsize=7.5, loc="left", pad=3)
    leg = ax_cal.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=6, handlelength=2.0)
    leg.get_frame().set_linewidth(0.5)
    for s in ("top", "right"):
        ax_cal.spines[s].set_visible(False)
    ax_cal.tick_params(labelbottom=False)

    # ── Middle / bottom: per-cohort predicted-probability histograms ────
    for ax, r in zip((ax_h1, ax_h2), results):
        for e in edges:
            ax.axvline(e, color="#000000", alpha=0.05, linewidth=0.5, zorder=1)
        ax.hist(r["proba"], bins=edges, density=True, color=r["color"], alpha=0.85,
               edgecolor="white", linewidth=0.3, zorder=2)
        ax.set_yticks([])
        ax.set_ylabel(r["label"], fontsize=6.5, color=r["color"], rotation=0,
                     ha="right", va="center", labelpad=2)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
    ax_h1.tick_params(labelbottom=False)
    ax_h2.set_xlabel("Mean predicted probability")
    ax_h2.set_xlim(0, 1)

    fig.align_ylabels([ax_cal, ax_h1, ax_h2])
    plt.tight_layout(pad=0.4)

    for ext, kw in ((".png", dict(dpi=300)),
                    (".pdf", dict()),
                    (".tiff", dict(dpi=600, pil_kwargs={"compression": "tiff_lzw"}))):
        fig.savefig(OUT_BASENAME + ext, bbox_inches="tight", **kw)
    print(f"\nWrote {OUT_BASENAME}.png (300 dpi preview), {OUT_BASENAME}.pdf (vector), "
          f"{OUT_BASENAME}.tiff (600 dpi, LZW) — 90 mm single-column width")


if __name__ == "__main__":
    results = [run_cohort(*c) for c in COHORTS]
    plot(results)