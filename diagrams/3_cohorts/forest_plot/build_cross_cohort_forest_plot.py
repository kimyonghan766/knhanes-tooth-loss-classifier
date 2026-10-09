"""
Cross-Cohort Forest Plot — SHAP-Ranked Features in the Exploratory Full Model
=============================================================================
Adjusted odds ratios (aORs) with 95% CIs from each cohort's full exploratory
survey-weighted logistic regression, displayed for the union of the 15 features
with the highest unweighted mean absolute SHAP contribution in that cohort.

The full regression contains the same 43 predictor concepts in every cohort;
SHAP is used only to decide which estimates to display. Rows are grouped by
whether a feature appears in all three, two, or one cohort's top-15 SHAP list.
A row with fewer than three markers therefore means that the feature was not in
the other cohort's top-15 list, not that it was omitted from that regression.

Why a separate script (not a notebook cell): each notebook prints its own full
survey-weighted aOR table and its own unweighted SHAP ranking. This script parses
those saved outputs and combines them without re-fitting the R/rpy2 models. If
the notebook outputs predate the unweighted ranking change, the script rebuilds
only the pinned CatBoost SHAP rankings; it still reads the saved R regression.

Elsevier artwork spec targeted (same as the calibration-curve companion
figure -- general Elsevier artwork instructions, no Journal of Dentistry
override found): combination art >= 500 dpi, double-column width 190 mm
(this is a primary results figure, so double- rather than single-column),
~7 pt lettering at final printed size.
"""
import os, re, json, sys, importlib.util
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "..", "Main")   # repo-root Main/, three levels up from this script
sys.path.insert(0, MAIN)            # codebook_labels.py lives in Main/
from codebook_labels import label_for

# label, notebook file, plot colour (blue/orange/red -- validated CVD-safe trio, matches
# the ROC/PR and calibration/DCA overlay figures), marker shape
COHORTS = [
    ("50+",    "CB_50+.ipynb",    "#0072B2", "o"),
    ("50-64",  "CB_50-64.ipynb",  "#E69F00", "^"),
    ("65+",    "CB_65+.ipynb",    "#D62728", "s"),
]
MM_PER_IN = 25.4
FIG_WIDTH_MM = 345.0                # deliberately wide landscape presentation
FIG_HEIGHT_MM = 218.0               # fixed height keeps the figure horizontally stretched
OUT_BASENAME = os.path.join(HERE, "cross_cohort_forest_plot")

# Regression-specific display units/contrasts. N_CA and N_NA are rescaled only
# in the inferential model, so these overrides belong in the forest plot rather
# than the shared SHAP/codebook label resolver.
FOREST_LABEL_OVERRIDES = {
    "sex_female": "Female sex",
    "diabetes": "Diabetes",
    "sm_presnt": "Current smoking",
    "O_pain": "Toothache",
    "town_t": "City/countryside",
    "live_t_2": "Dwelling type: apartment",
    "HE_dbp": "Diastolic BP",
    "eGFR": "eGFR",
    "LS_FRUIT": "Fruit intake frequency",
    "N_CA": "Daily total calcium",
    "N_NA": "Sodium Intake",
    "BD1": "Lifetime alcohol drinking experience",
    "L_BR_FQ_2": "Breakfast 3–4×/week vs 5–7×/week",
    "L_BR_FQ_3": "Breakfast 1–2×/week vs 5–7×/week",
    "L_BR_FQ_4": "Breakfast almost never vs 5–7×/week",
}


def forest_label(name):
    return FOREST_LABEL_OVERRIDES[name] if name in FOREST_LABEL_OVERRIDES else label_for(name)


def cell_output_text(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif "data" in o and "text/plain" in o["data"]:
            out.append("".join(o["data"]["text/plain"]))
    return "\n".join(out)


_ROW_RE = re.compile(r"^(\S+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)")
TOP_N_SHAP = 15
SHAP_TO_REGRESSION = {
    "sex": "sex_female",
}


def parse_shap_table(nbfile, ranked_override=None):
    """Parse the unweighted SHAP top 15 and the full survey-weighted aOR table."""
    nb = json.load(open(os.path.join(MAIN, nbfile)))
    if ranked_override is None:
        shap_text = next((cell_output_text(c) for c in nb["cells"]
                          if "features by unweighted mean |SHAP|" in cell_output_text(c)), None)
        assert shap_text is not None, \
            f"{nbfile}: no saved unweighted SHAP ranking -- rerun the SHAP summary cell"
        ranked = []
        for line in shap_text.split("\n"):
            m = re.match(r"\s*(\d+)\.\s+(\S+)\s+[-\d.]+", line)
            if m and int(m.group(1)) <= TOP_N_SHAP:
                ranked.append(SHAP_TO_REGRESSION.get(m.group(2), m.group(2)))
    else:
        ranked = [SHAP_TO_REGRESSION.get(name, name) for name in ranked_override]
    assert len(ranked) == TOP_N_SHAP, \
        f"{nbfile}: expected {TOP_N_SHAP} unweighted SHAP features, found {len(ranked)}"

    text = next((cell_output_text(c) for c in nb["cells"]
                 if "=== Adjusted odds ratios (survey::svyglm" in cell_output_text(c)), None)
    assert text is not None, \
        f"{nbfile}: no saved full survey-weighted regression table -- rerun §11"

    n_match = re.search(r"Complete-case n = (\d+)\s*\|\s*tooth-loss prevalence = ([\d.]+)%", text)
    n_complete, prevalence = int(n_match.group(1)), float(n_match.group(2))

    all_rows = {}
    in_table = False
    for line in text.split("\n"):
        if line.strip().startswith("aOR"):
            in_table = True
            continue
        if not in_table:
            continue
        m = _ROW_RE.match(line.strip())
        if not m:
            continue
        name, aor, lo, hi, p = m.groups()
        if name == "(Intercept)":
            continue
        all_rows[name] = dict(aOR=float(aor), lo=float(lo), hi=float(hi), p=float(p))
    missing = [name for name in ranked if name not in all_rows]
    assert not missing, f"{nbfile}: top-15 SHAP terms absent from the regression table: {missing}"
    rows = {name: all_rows[name] for name in ranked}
    return rows, n_complete, prevalence, TOP_N_SHAP


def recompute_unweighted_rankings():
    """Rebuild top-15 SHAP lists when notebook outputs have not yet been refreshed."""
    builder_path = os.path.join(
        HERE, "..", "shap_summary", "build_cross_cohort_shap_summary_overlay.py"
    )
    spec = importlib.util.spec_from_file_location("cross_cohort_shap_builder", builder_path)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)

    # Return raw feature names rather than display labels so they match regression terms.
    builder.label_list = lambda names: list(names)
    builder.LABEL_OVERRIDES = {}
    notebook_to_ranking = {}
    for label, nbfile in builder.COHORTS:
        result = builder.run_cohort(label, nbfile)
        notebook_to_ranking[nbfile] = result["names"][:TOP_N_SHAP]
    return notebook_to_ranking


def plot(cohort_data, cohort_data_lookup, mode, out_suffix):
    labels = [label for label, _, _, _ in cohort_data]
    colors = {label: color for label, _, color, _ in cohort_data}
    markers = {label: marker for label, _, _, marker in cohort_data}
    rows_by_label = {label: cohort_data_lookup[label][0] for label in labels}
    n_by_label = {label: cohort_data_lookup[label][1] for label in labels}
    prev_by_label = {label: cohort_data_lookup[label][2] for label in labels}
    topn_by_label = {label: cohort_data_lookup[label][3] for label in labels}
    n_cohorts = len(labels)

    def membership(varname):
        return [label for label in labels if varname in rows_by_label[label]]

    all_vars = sorted(set().union(*(set(r) for r in rows_by_label.values())))

    def effect_size(varname):
        return max(abs(np.log(rows_by_label[label][varname]["aOR"])) for label in membership(varname))

    # Grouped by HOW MANY of the N cohorts selected the variable, not by which
    # exact cohort(s) -- the simplest generalisation of the old "BOTH / A-only /
    # B-only" split to N cohorts, avoiding a combinatorial explosion of blocks.
    all_n = [v for v in all_vars if len(membership(v)) == n_cohorts]
    two_of = [v for v in all_vars if len(membership(v)) == 2]
    single = [v for v in all_vars if len(membership(v)) == 1]

    blocks = [
        (f"ALL {n_cohorts} COHORTS  ({len(all_n)})", sorted(all_n, key=effect_size, reverse=True)),
        (f"IN 2 OF {n_cohorts} COHORTS  ({len(two_of)})", sorted(two_of, key=effect_size, reverse=True)),
        (f"SINGLE COHORT ONLY  ({len(single)})", sorted(single, key=effect_size, reverse=True)),
    ]
    blocks = [(name, vars_) for name, vars_ in blocks if vars_]
    var_order = [v for _, vars_ in blocks for v in vars_]
    n_vars = len(var_order)

    # Block names render as their own bold header ROW in the y-axis (not side-margin
    # text) -- side-margin text at a fixed axes-fraction x collided with long
    # codebook-derived labels (e.g. "Household generation-composition code: ..."),
    # since matplotlib doesn't know how far left an unrelated Text artist extends.
    # A header row is a normal tick label, so layout can never collide with it.
    render_items = []
    for name, vars_ in blocks:
        render_items.append(("header", name))
        for v in vars_:
            render_items.append(("var", v))
    n_items = len(render_items)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 12.5,
        "axes.edgecolor": "#888888",
        "axes.linewidth": 0.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    ROW_SPACING = 1.3                   # extra vertical gap between rows, to keep clearance
                                         # around the wider per-row marker dodge below
    fig_w = FIG_WIDTH_MM / MM_PER_IN
    fig_h = FIG_HEIGHT_MM / MM_PER_IN
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    all_y = np.arange(n_items)[::-1] * ROW_SPACING
    var_y, header_rows = {}, []
    for y, (kind, val) in zip(all_y, render_items):
        if kind == "header":
            header_rows.append((y, val))
        else:
            var_y[val] = y
    dodge_step = 0.32                   # vertical gap between the 3 cohorts' markers per row
    callout_dodge_step = 0.55           # extra separation for multi-line off-scale annotations
    offsets = {label: (i - (n_cohorts - 1) / 2) * dodge_step for i, label in enumerate(labels)}
    callout_offsets = {
        label: (i - (n_cohorts - 1) / 2) * callout_dodge_step
        for i, label in enumerate(labels)
    }

    # ── Block shading (Both cohorts / cohort-A-only / cohort-B-only), header row
    # included in its own block's band ──────────────────────────────────────────
    block_bounds = []
    pos = 0
    for name, vars_ in blocks:
        block_bounds.append((pos, pos + len(vars_)))   # header + its variable rows
        pos += 1 + len(vars_)
    for gi, (i0, i1) in enumerate(block_bounds):
        if gi % 2 == 1:
            ax.axhspan(all_y[i1] - 0.5 * ROW_SPACING, all_y[i0] + 0.5 * ROW_SPACING,
                      color="#000000", alpha=0.035, zorder=0)

    ax.axvline(1.0, color="#888888", linewidth=1.0, linestyle=(0, (4, 3)), zorder=1)

    # ── Outlier detection (Tukey "far out" fence on log aOR) ─────────────────
    # A row whose point estimate sits far outside the bulk of the other effect
    # sizes (BM1_0 / "Brushed teeth yesterday" in the 65+ cohort: aOR 0.08 vs.
    # everything else in roughly 0.6-2.4) forces the shared log-scale axis wide
    # enough to squash every other row's CI into a sliver near x=1. Flag those
    # rows and keep them OUT of the x-limit calculation, rendering them per
    # `mode` instead of a normal marker. Tukey's standard *inner* fence
    # (1.5*IQR) is too sensitive with only ~30 points here -- it also caught
    # OR1/"Self-rated oral health" (aOR 2.16), a genuinely large but perfectly
    # normal effect, not a scale-breaking one. The *outer* "far out" fence
    # (3*IQR) isolates just the true outlier and leaves real large effects on
    # the shared axis where they belong.
    all_points = [(label, varname, r)
                  for label, rows in rows_by_label.items()
                  for varname, r in rows.items()]
    log_aors = np.array([np.log(r["aOR"]) for _, _, r in all_points])
    q1, q3 = np.percentile(log_aors, [25, 75])
    iqr = q3 - q1
    fence_lo, fence_hi = q1 - 3.0 * iqr, q3 + 3.0 * iqr
    outliers = {(label, varname) for label, varname, r in all_points
                if not (fence_lo <= np.log(r["aOR"]) <= fence_hi)}

    # ── Data-driven x-limits from the non-outlier rows only (old fixed
    # 0.55-2.6 range was tuned for the pre-specified covariate set; the
    # SHAP-selected set differs per run) ──
    all_los = [r["lo"] for label, varname, r in all_points if (label, varname) not in outliers]
    all_his = [r["hi"] for label, varname, r in all_points if (label, varname) not in outliers]
    log_lo, log_hi = np.log(min(all_los)), np.log(max(all_his))
    pad = max(0.08 * (log_hi - log_lo), 0.05)
    xlim = (np.exp(log_lo - pad), np.exp(log_hi + pad))

    for label in labels:
        rows, color, marker, offset = rows_by_label[label], colors[label], markers[label], offsets[label]
        for varname in var_order:
            if varname not in rows:
                continue
            r = rows[varname]
            y = var_y[varname] + offset
            significant = r["p"] < 0.05

            if (label, varname) in outliers:
                # Text callouts need more vertical clearance than compact markers.
                # This keeps multiple off-scale estimates on distinct readable lines.
                y = var_y[varname] + callout_offsets[label]
                edge = xlim[0] if r["aOR"] < xlim[0] else xlim[1]
                txt_x, ha = (edge * 1.06, "left") if edge == xlim[0] else (edge * 0.94, "right")
                label_txt = f"{r['aOR']:.2f} ({r['lo']:.2f}–{r['hi']:.2f})"
                if mode == "clip":
                    arrow_marker = "<" if edge == xlim[0] else ">"
                    ax.plot(edge, y, marker=arrow_marker, color=color, markersize=5.0,
                            markerfacecolor=color if significant else "white",
                            markeredgecolor=color, markeredgewidth=0.8,
                            clip_on=False, zorder=3)
                    ax.text(txt_x, y, label_txt, fontsize=9.0, va="center", ha=ha,
                            color=color, style="italic")
                else:  # mode == "annotate": no marker/whisker on the shared axis at all
                    ax.text(txt_x, y, f"{label}: aOR {label_txt} — off shared scale",
                            fontsize=9.0, va="center", ha=ha, color=color, style="italic")
                continue

            xerr = [[r["aOR"] - r["lo"]], [r["hi"] - r["aOR"]]]
            ax.errorbar(r["aOR"], y, xerr=xerr, fmt=marker, color=color,
                       markersize=4.0, markerfacecolor=color if significant else "white",
                       markeredgecolor=color, markeredgewidth=0.8,
                       elinewidth=1.0, capsize=2.0, zorder=3)

    ax.set_xscale("log")
    ax.set_xlim(*xlim)
    _candidate_ticks = [0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                        1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0]
    ticks = [t for t in _candidate_ticks if xlim[0] <= t <= xlim[1]]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}" for t in ticks])
    ax.set_yticks(all_y)
    tick_labels = [name if kind == "header" else forest_label(name) for kind, name in render_items]
    # Larger, medium-weight feature labels for manuscript-scale readability; the
    # three cohort-group headings are promoted to full bold immediately below.
    label_fontsize = 13
    legend_fontsize = 11.5
    ax.set_yticklabels(tick_labels, fontsize=label_fontsize, fontweight="medium")
    for y, _ in header_rows:
        tick = ax.yaxis.get_ticklabels()[list(all_y).index(y)]
        tick.set_fontweight("bold")
        tick.set_fontsize(label_fontsize + 0.3)
        tick.set_color("#333333")
    ax.set_ylim(-0.5 * ROW_SPACING, (n_items - 0.5) * ROW_SPACING)
    ax.set_xlabel("Adjusted odds ratio (95% CI), log scale")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)

    # ── Legend: cohort (color+shape), significance (fill), blank-row note ─
    from matplotlib.lines import Line2D
    legend_elems = [
        Line2D([0], [0], marker=markers[label], color=colors[label], linestyle="",
              markersize=6.5, markerfacecolor=colors[label],
              label=f"{label}  (n={n_by_label[label]:,}, prevalence {prev_by_label[label]:.1f}%)")
        for label in labels
    ] + [
        Line2D([0], [0], marker="o", color="#555555", linestyle="",
              markersize=6.5, markerfacecolor="#555555",
              label="Filled = nominal unadjusted p < 0.05"),
        Line2D([0], [0], marker="o", color="#555555", linestyle="",
              markersize=6.5, markerfacecolor="white", markeredgewidth=0.9,
              label="Open = nominal unadjusted p ≥ 0.05"),
    ]
    # Legend moved OFF the data area (was "upper right" inside the axes, which sat
    # directly on top of the right-hand whiskers of the top rows -- e.g. "Self-rated
    # oral health" / "Current smoking rate indicator" -- whenever their CIs reached
    # into the plot's upper-right corner). A figure-level legend below the x-axis
    # can never collide with a data row, regardless of which rows have the widest CIs.
    fig.subplots_adjust(left=0.275, right=0.985, top=0.985, bottom=0.205)
    leg = fig.legend(handles=legend_elems, loc="lower center", bbox_to_anchor=(0.5, 0.012),
                     ncol=3, frameon=True, framealpha=0.92,
                     fontsize=legend_fontsize, handlelength=1.7, borderpad=0.75, columnspacing=1.5,
                     labelspacing=0.75)
    leg.get_frame().set_linewidth(0.5)

    out_base = OUT_BASENAME + out_suffix
    fig.savefig(out_base + ".png", bbox_inches="tight", dpi=600)
    print(f"\nWrote {out_base}.png (600 dpi) -- {n_vars} rows "
          f"({len(all_n)} in all {n_cohorts}, {len(two_of)} in 2 of {n_cohorts}, {len(single)} single-cohort)")


if __name__ == "__main__":
    saved_rankings_current = True
    for _, nbfile, _, _ in COHORTS:
        nb = json.load(open(os.path.join(MAIN, nbfile)))
        if not any("features by unweighted mean |SHAP|" in cell_output_text(c)
                   for c in nb["cells"]):
            saved_rankings_current = False
            break
    ranking_overrides = {} if saved_rankings_current else recompute_unweighted_rankings()
    if ranking_overrides:
        print("Notebook SHAP outputs are stale; using freshly recomputed unweighted rankings.")

    cohort_data_lookup = {}
    for label, nbfile, color, marker in COHORTS:
        rows, n_complete, prevalence, top_n = parse_shap_table(
            nbfile, ranking_overrides.get(nbfile)
        )
        cohort_data_lookup[label] = (rows, n_complete, prevalence, top_n)
        print(f"[{label}] parsed {len(rows)} rows from {nbfile}  "
              f"(n_complete={n_complete}, prevalence={prevalence:.1f}%, TOP_N_SHAP={top_n})")
    # "annotate" outlier handling: drop the outlier's marker/whisker entirely and report
    # its aOR (95% CI) as a text-only callout on its row. (The "clip" variant -- arrow
    # marker at the axis edge -- has been retired.)
    plot(COHORTS, cohort_data_lookup, "annotate", "_annotated")
