"""
Cross-Cohort Forest Plot — SHAP-Informed Confirmatory Model (Figure 5)
=============================================================================
Adjusted odds ratios (aOR) with 95% CI from the SHAP-informed confirmatory
survey-weighted logistic regression (notebook §9.12), for the 50+ cohort and
the 65+ cohort, dodged on shared rows for direct side-by-side comparison.

Formerly built from the PRE-SPECIFIED model (§11.3), which used an identical,
theory-driven 18-covariate set in both cohorts. §11.3 has been removed; the
SHAP-informed model is data-driven per cohort (top-N by mean(|SHAP|), see
notebook TOP_N_SHAP), so the two cohorts' selected variables are NOT
guaranteed to match. This script plots the UNION of both cohorts' selected
variables: a row with only one cohort's marker means that variable was
selected into THAT cohort's model but not the other's -- it is not a missing
data point, the other cohort's model simply never estimated a coefficient
for it.

Why a separate script (not a notebook cell): each notebook only prints its own
cohort's aOR table (no re-fitting needed -- the svyglm output is already saved
as text in the notebook, so this script just parses it and plots; it does not
re-run the R/rpy2 pipeline).

Elsevier artwork spec targeted (same as the calibration-curve companion
figure -- general Elsevier artwork instructions, no Journal of Dentistry
override found): combination art >= 500 dpi, double-column width 190 mm
(this is a primary results figure, so double- rather than single-column),
~7 pt lettering at final printed size.
"""
import os, re, json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "..", "Main")   # repo-root Main/, two levels up from this script
sys.path.insert(0, MAIN)            # codebook_labels.py lives in Main/
from codebook_labels import label_for

# label, notebook file, plot colour (Okabe-Ito, CVD-safe), marker shape
COHORTS = [
    ("50+", "final.ipynb",       "#0072B2", "o"),
    ("65+", "final(65+).ipynb",  "#009E73", "s"),
]
MM_PER_IN = 25.4
FIG_WIDTH_MM = 190                  # Elsevier double-column width
OUT_BASENAME = os.path.join(HERE, "cross_cohort_forest_plot")


def cell_output_text(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif "data" in o and "text/plain" in o["data"]:
            out.append("".join(o["data"]["text/plain"]))
    return "\n".join(out)


_ROW_RE = re.compile(r"^(\S+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)")


def parse_shap_table(nbfile):
    """Parse §9.12's printed 'SHAP-informed confirmatory model' table: name,
    aOR, CI 2.5%, CI 97.5%, p-value (ignoring the trailing Holm p / BH q /
    Survives columns, which the old pre-specified table didn't have)."""
    nb = json.load(open(os.path.join(MAIN, nbfile)))
    text = next((cell_output_text(c) for c in nb["cells"]
                 if "SHAP-informed confirmatory model" in cell_output_text(c)), None)
    assert text is not None, \
        f"{nbfile}: no cell output contains the SHAP-informed confirmatory model table " \
        "-- rerun §9.9-9.12 in this notebook first"

    n_match = re.search(r"Complete-case n = (\d+)\s*\|\s*tooth-loss prevalence = ([\d.]+)%", text)
    n_complete, prevalence = int(n_match.group(1)), float(n_match.group(2))

    top_n_match = re.search(r"Top (\d+) SHAP-ranked variables", text)
    top_n = int(top_n_match.group(1)) if top_n_match else None

    rows = {}
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
        rows[name] = dict(aOR=float(aor), lo=float(lo), hi=float(hi), p=float(p))
    assert rows, f"{nbfile}: found the SHAP-informed model header but parsed zero variable rows"
    return rows, n_complete, prevalence, top_n


def plot(cohort_data, cohort_data_lookup):
    (label_a, _, color_a, marker_a), (label_b, _, color_b, marker_b) = cohort_data
    rows_a, n_a, prev_a, topn_a = cohort_data_lookup[label_a]
    rows_b, n_b, prev_b, topn_b = cohort_data_lookup[label_b]

    both = sorted(set(rows_a) & set(rows_b))
    only_a = sorted(set(rows_a) - set(rows_b))
    only_b = sorted(set(rows_b) - set(rows_a))

    def effect_size(varname):
        vals = []
        if varname in rows_a:
            vals.append(abs(np.log(rows_a[varname]["aOR"])))
        if varname in rows_b:
            vals.append(abs(np.log(rows_b[varname]["aOR"])))
        return max(vals)

    blocks = [
        (f"BOTH COHORTS  ({len(both)})", sorted(both, key=effect_size, reverse=True)),
        (f"{label_a.upper()} ONLY  ({len(only_a)})", sorted(only_a, key=effect_size, reverse=True)),
        (f"{label_b.upper()} ONLY  ({len(only_b)})", sorted(only_b, key=effect_size, reverse=True)),
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
        "font.size": 7,
        "axes.edgecolor": "#888888",
        "axes.linewidth": 0.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    fig_w = FIG_WIDTH_MM / MM_PER_IN
    fig_h = fig_w * (0.20 + 0.030 * n_items)     # scales with row count (union size varies run to run)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    all_y = np.arange(n_items)[::-1]
    var_y, header_rows = {}, []
    for y, (kind, val) in zip(all_y, render_items):
        if kind == "header":
            header_rows.append((y, val))
        else:
            var_y[val] = y
    dodge = 0.16

    # ── Block shading (Both cohorts / cohort-A-only / cohort-B-only), header row
    # included in its own block's band ──────────────────────────────────────────
    block_bounds = []
    pos = 0
    for name, vars_ in blocks:
        block_bounds.append((pos, pos + len(vars_)))   # header + its variable rows
        pos += 1 + len(vars_)
    for gi, (i0, i1) in enumerate(block_bounds):
        if gi % 2 == 1:
            ax.axhspan(all_y[i1] - 0.5, all_y[i0] + 0.5,
                      color="#000000", alpha=0.035, zorder=0)

    ax.axvline(1.0, color="#888888", linewidth=1.0, linestyle=(0, (4, 3)), zorder=1)

    # ── Data-driven x-limits (old fixed 0.55-2.6 range was tuned for the
    # pre-specified covariate set; the SHAP-selected set differs per run) ──
    all_los = [r["lo"] for rows in (rows_a, rows_b) for r in rows.values()]
    all_his = [r["hi"] for rows in (rows_a, rows_b) for r in rows.values()]
    log_lo, log_hi = np.log(min(all_los)), np.log(max(all_his))
    pad = max(0.08 * (log_hi - log_lo), 0.05)
    xlim = (np.exp(log_lo - pad), np.exp(log_hi + pad))

    for label, rows, color, marker in ((label_a, rows_a, color_a, marker_a),
                                        (label_b, rows_b, color_b, marker_b)):
        offset = dodge if label == label_a else -dodge
        for varname in var_order:
            if varname not in rows:
                continue
            r = rows[varname]
            y = var_y[varname] + offset
            significant = r["p"] < 0.05
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
    tick_labels = [name if kind == "header" else label_for(name) for kind, name in render_items]
    ax.set_yticklabels(tick_labels, fontsize=6.5)
    for y, _ in header_rows:
        tick = ax.yaxis.get_ticklabels()[list(all_y).index(y)]
        tick.set_fontweight("bold")
        tick.set_fontsize(6.8)
        tick.set_color("#333333")
    ax.set_ylim(-0.5, n_items - 0.5)
    ax.set_xlabel("Adjusted odds ratio (95% CI), log scale")
    ax.set_title(
        "Adjusted odds ratios — SHAP-informed confirmatory model, by age cohort\n"
        f"union of top-{topn_a or '?'} ({label_a}) / top-{topn_b or '?'} ({label_b}) "
        "SHAP-selected predictors",
        fontsize=8, loc="left", pad=6)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)

    # ── Legend: cohort (color+shape), significance (fill), blank-row note ─
    from matplotlib.lines import Line2D
    legend_elems = [
        Line2D([0], [0], marker=marker_a, color=color_a, linestyle="",
              markersize=4.5, markerfacecolor=color_a,
              label=f"{label_a}  (n={n_a:,}, prevalence {prev_a:.1f}%)"),
        Line2D([0], [0], marker=marker_b, color=color_b, linestyle="",
              markersize=4.5, markerfacecolor=color_b,
              label=f"{label_b}  (n={n_b:,}, prevalence {prev_b:.1f}%)"),
        Line2D([0], [0], marker="o", color="#555555", linestyle="",
              markersize=4.5, markerfacecolor="#555555", label="Filled = p < 0.05"),
        Line2D([0], [0], marker="o", color="#555555", linestyle="",
              markersize=4.5, markerfacecolor="white", markeredgewidth=0.8,
              label="Open = not significant"),
    ]
    leg = ax.legend(handles=legend_elems, loc="upper right", frameon=True, framealpha=0.92,
                    fontsize=6, handlelength=1.5, borderpad=0.6)
    leg.get_frame().set_linewidth(0.5)
    ax.text(0.99, 0.02,
            "One marker per row = selected into only that cohort's SHAP-informed model",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=5.5,
            color="#777777", style="italic")

    plt.tight_layout()
    for ext, kw in ((".png", dict(dpi=300)),
                    (".pdf", dict()),
                    (".tiff", dict(dpi=600, pil_kwargs={"compression": "tiff_lzw"}))):
        fig.savefig(OUT_BASENAME + ext, bbox_inches="tight", **kw)
    print(f"\nWrote {OUT_BASENAME}.png (300 dpi preview), {OUT_BASENAME}.pdf (vector), "
          f"{OUT_BASENAME}.tiff (600 dpi, LZW) -- {n_vars} rows "
          f"({len(both)} shared, {len(only_a)} {label_a}-only, {len(only_b)} {label_b}-only)")


if __name__ == "__main__":
    cohort_data_lookup = {}
    for label, nbfile, color, marker in COHORTS:
        rows, n_complete, prevalence, top_n = parse_shap_table(nbfile)
        cohort_data_lookup[label] = (rows, n_complete, prevalence, top_n)
        print(f"[{label}] parsed {len(rows)} rows from {nbfile}  "
              f"(n_complete={n_complete}, prevalence={prevalence:.1f}%, TOP_N_SHAP={top_n})")
    plot(COHORTS, cohort_data_lookup)
