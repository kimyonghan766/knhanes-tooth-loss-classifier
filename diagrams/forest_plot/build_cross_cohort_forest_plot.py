"""
Cross-Cohort Forest Plot — Pre-Specified Survey-Weighted Model (Figure 5)
=============================================================================
Adjusted odds ratios (aOR) with 95% CI from the pre-specified survey-weighted
logistic regression (notebook §10.3, cell 88), for the 50+ cohort and the 65+
cohort, dodged on shared rows for direct side-by-side comparison.

Why a separate script (not a notebook cell): each notebook only prints its own
cohort's aOR table (no re-fitting needed — the svyglm output is already saved
as text in the notebook, so this script just parses it and plots; it does not
re-run the R/rpy2 pipeline).

Occupation dummies (occp_2..occp_7) and the intercept are excluded — 18 core
pre-specified covariates only (systemic, socioeconomic, behavioral blocks).

Elsevier artwork spec targeted (same as the calibration-curve companion
figure — general Elsevier artwork instructions, no Journal of Dentistry
override found): combination art >= 500 dpi, double-column width 190 mm
(this is a primary results figure with 18 rows, so double- rather than
single-column), ~7 pt lettering at final printed size.
"""
import os, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "Main")   # repo-root Main/, two levels up from this script

# label, notebook file, plot colour (Okabe-Ito, CVD-safe), marker shape
COHORTS = [
    ("50+", "final.ipynb",       "#0072B2", "o"),
    ("65+", "final(65+).ipynb",  "#009E73", "s"),
]
MM_PER_IN = 25.4
FIG_WIDTH_MM = 190                  # Elsevier double-column width
OUT_BASENAME = os.path.join(HERE, "cross_cohort_forest_plot")

# 18 core pre-specified variables, in display order (top row = first entry),
# grouped into the same systemic / SES / behavioral blocks as notebook §10.3.
VAR_ORDER = [
    ("Systemic",      "diabetes",     "Diabetes (yes vs no)"),
    ("Systemic",      "eGFR",         "eGFR (mL/min/1.73m²)"),
    ("Systemic",      "hypertension", "Hypertension (yes vs no)"),
    ("Systemic",      "HE_Uacid",     "Uric acid (mg/dL)"),
    ("Systemic",      "HE_BMI",       "BMI (kg/m²)"),
    ("Systemic",      "HE_TG",        "Triglycerides (mg/dL)"),
    ("Socioeconomic", "sex_female",   "Sex (female vs male)"),
    ("Socioeconomic", "age",          "Age (years)"),
    ("Socioeconomic", "ho_incm",      "Household income (quartile)"),
    ("Socioeconomic", "edu",          "Education level"),
    ("Socioeconomic", "town_t",       "Urban area (vs rural)"),
    ("Behavioral",    "sm_presnt",    "Current smoker (yes vs no)"),
    ("Behavioral",    "BD1",          "Current alcohol drinker (yes vs no)"),
    ("Behavioral",    "pa_aerobic",   "Aerobic activity adherent (yes vs no)"),
    ("Behavioral",    "BP1",          "Perceived stress (higher = more)"),
    ("Behavioral",    "brush_freq",   "Brushing frequency (occasions/day)"),
    ("Behavioral",    "N_TDF",        "Dietary fiber intake (g/day)"),
    ("Behavioral",    "N_CA",         "Calcium intake (mg/day)"),
]


def cell_output_text(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif "data" in o and "text/plain" in o["data"]:
            out.append("".join(o["data"]["text/plain"]))
    return "\n".join(out)


def parse_prespec_table(nbfile):
    nb = json.load(open(os.path.join(MAIN, nbfile)))
    # find the cell by its output content (robust to cells being added/removed)
    text = next((cell_output_text(c) for c in nb["cells"]
                 if "Pre-specified survey-weighted LR" in cell_output_text(c)), None)
    assert text is not None, \
        f"{nbfile}: no cell output contains the pre-specified survey-weighted LR table"

    n_match = re.search(r"Complete-case n = (\d+)\s*\|\s*tooth-loss prevalence = ([\d.]+)%", text)
    n_complete, prevalence = int(n_match.group(1)), float(n_match.group(2))

    rows = {}
    in_table = False
    for line in text.split("\n"):
        if line.strip().startswith("aOR"):
            in_table = True
            continue
        if not in_table or not line.strip():
            continue
        parts = line.split()
        if len(parts) != 5:      # name + aOR + CI lo + CI hi + p-value
            continue
        name, aor, lo, hi, p = parts
        rows[name] = dict(aOR=float(aor), lo=float(lo), hi=float(hi), p=float(p))
    return rows, n_complete, prevalence


def plot(cohort_data, cohort_data_lookup):
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7,
        "axes.edgecolor": "#888888",
        "axes.linewidth": 0.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    n_vars = len(VAR_ORDER)
    fig_w = FIG_WIDTH_MM / MM_PER_IN
    fig_h = fig_w * 0.62
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    y_positions = np.arange(n_vars)[::-1]   # first VAR_ORDER entry drawn at top
    dodge = 0.16

    # ── Group-block shading (systemic / socioeconomic / behavioral) ─────
    blocks = [g for g, _, _ in VAR_ORDER]
    block_bounds = []
    start = 0
    for i in range(1, n_vars + 1):
        if i == n_vars or blocks[i] != blocks[start]:
            block_bounds.append((blocks[start], start, i - 1))
            start = i
    for gi, (gname, i0, i1) in enumerate(block_bounds):
        if gi % 2 == 1:
            ax.axhspan(y_positions[i1] - 0.5, y_positions[i0] + 0.5,
                      color="#000000", alpha=0.035, zorder=0)

    ax.axvline(1.0, color="#888888", linewidth=1.0, linestyle=(0, (4, 3)), zorder=1)

    for label, nbfile, color, marker in cohort_data:
        rows, n_complete, prevalence = cohort_data_lookup[label]
        offset = dodge if label == cohort_data[0][0] else -dodge
        for i, (_, varname, _) in enumerate(VAR_ORDER):
            r = rows[varname]
            y = y_positions[i] + offset
            significant = r["p"] < 0.05
            xerr = [[r["aOR"] - r["lo"]], [r["hi"] - r["aOR"]]]
            ax.errorbar(r["aOR"], y, xerr=xerr, fmt=marker, color=color,
                       markersize=4.0, markerfacecolor=color if significant else "white",
                       markeredgecolor=color, markeredgewidth=0.8,
                       elinewidth=1.0, capsize=2.0, zorder=3)

    ax.set_xscale("log")
    ax.set_xlim(0.55, 2.6)
    ax.set_xticks([0.6, 0.8, 1.0, 1.25, 1.6, 2.0, 2.5])
    ax.set_xticklabels(["0.6", "0.8", "1.0", "1.25", "1.6", "2.0", "2.5"])
    ax.set_yticks(y_positions)
    ax.set_yticklabels([lbl for _, _, lbl in VAR_ORDER])
    ax.set_ylim(-0.5, n_vars - 0.5)
    ax.set_xlabel("Adjusted odds ratio (95% CI), log scale")
    ax.set_title("Adjusted odds ratios — pre-specified survey-weighted model, by age cohort",
                fontsize=8, loc="left", pad=6)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)

    # ── Group labels along the left margin ───────────────────────────────
    for gname, i0, i1 in block_bounds:
        y_mid = (y_positions[i0] + y_positions[i1]) / 2
        ax.text(-0.30, y_mid, gname, transform=ax.get_yaxis_transform(),
               fontsize=6.5, fontweight="bold", color="#555555",
               ha="right", va="center", rotation=90)

    # ── Legend: cohort (color+shape) and significance (fill) ────────────
    from matplotlib.lines import Line2D
    legend_elems = []
    for label, nbfile, color, marker in cohort_data:
        _, n_complete, prevalence = cohort_data_lookup[label]
        legend_elems.append(Line2D([0], [0], marker=marker, color=color, linestyle="",
                                   markersize=4.5, markerfacecolor=color,
                                   label=f"{label}  (n={n_complete:,}, prevalence {prevalence:.1f}%)"))
    legend_elems.append(Line2D([0], [0], marker="o", color="#555555", linestyle="",
                               markersize=4.5, markerfacecolor="#555555",
                               label="Filled = p < 0.05"))
    legend_elems.append(Line2D([0], [0], marker="o", color="#555555", linestyle="",
                               markersize=4.5, markerfacecolor="white", markeredgewidth=0.8,
                               label="Open = not significant"))
    leg = ax.legend(handles=legend_elems, loc="upper right", frameon=True, framealpha=0.92,
                    fontsize=6, handlelength=1.5, borderpad=0.6)
    leg.get_frame().set_linewidth(0.5)

    plt.tight_layout()
    for ext, kw in ((".png", dict(dpi=300)),
                    (".pdf", dict()),
                    (".tiff", dict(dpi=600, pil_kwargs={"compression": "tiff_lzw"}))):
        fig.savefig(OUT_BASENAME + ext, bbox_inches="tight", **kw)
    print(f"\nWrote {OUT_BASENAME}.png (300 dpi preview), {OUT_BASENAME}.pdf (vector), "
          f"{OUT_BASENAME}.tiff (600 dpi, LZW) — 190 mm double-column width")


if __name__ == "__main__":
    cohort_data_lookup = {}
    for label, nbfile, color, marker in COHORTS:
        rows, n_complete, prevalence = parse_prespec_table(nbfile)
        cohort_data_lookup[label] = (rows, n_complete, prevalence)
        print(f"[{label}] parsed {len(rows)} rows from {nbfile}  "
              f"(n_complete={n_complete}, prevalence={prevalence:.1f}%)")
        missing = [v for _, v, _ in VAR_ORDER if v not in rows]
        assert not missing, f"{nbfile}: expected variables missing from parsed table: {missing}"
    plot(COHORTS, cohort_data_lookup)