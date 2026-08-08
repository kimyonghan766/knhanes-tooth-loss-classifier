"""
Study Flow Diagram — Sample & Variable Attrition (both cohorts)
=============================================================================
Box-and-connector flow diagram tracking BOTH forms of attrition through the
pipeline described in Main/final.ipynb (cohort A, age >= 50) and
Main/final(65+).ipynb (cohort B, age >= 65):

  - ROW attrition (respondents): age-eligibility filter -> missing/invalid
    target (O_TC) exclusion -> analytic cohort.
  - COLUMN attrition (candidate predictors): the 9 variables excluded before
    modelling (5 by the computed NaN% > 30 missingness rule, 4 by a priori
    conceptual/definitional-overlap reasoning -- see notebook cell 6 and the
    §4.1.1 computed screen in cell 20, whose printed verdict table confirms
    all 9 and finds no further exclusions among the 57 retained variables).

After "Data preparation" the diagram BRANCHES into the two analysis arms,
because they draw on different samples:
  - ML (predictive) arm  -> temporal Development/Evaluation split (notebook
    §6 onward; feature_cols).
  - Inferential (confirmatory) arm -> full pooled cohort, survey-weighted
    (KNHANES strata/PSU/weights), no train/eval split (notebook §11 / §11.3;
    reg2/m2 built from df_subset with no year filter).
Collapsing both arms into one shared Dev/Eval split (the previous version of
this diagram) misstated the inferential arm's actual sample.

All Ns are taken directly from notebook outputs, not recomputed here.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_BASENAME = os.path.join(HERE, "study_flow_diagram")

plt.rcParams["font.family"] = "serif"

FIG_W, FIG_H = 12.0, 16.5   # inches
XLIM = (0, 100)
YLIM = (0, 222)             # y grows downward (axis inverted below)

MAIN_X0, MAIN_X1 = 6, 58          # main-column box span
MAIN_XC = (MAIN_X0 + MAIN_X1) / 2
SIDE_X0, SIDE_X1 = 66, 97         # exclusion side-box span

BOX_KW = dict(facecolor="white", edgecolor="black", linewidth=1.2, zorder=3)
LINE_KW = dict(color="black", linewidth=1.1, zorder=2)


def draw_box(ax, x0, x1, y0, y1, text, fontsize=9.5, weight="normal"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **BOX_KW))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center",
             fontsize=fontsize, weight=weight, linespacing=1.55, zorder=4)


def vline(ax, x, y0, y1):
    ax.plot([x, x], [y0, y1], **LINE_KW)


def hline(ax, y, x0, x1):
    ax.plot([x0, x1], [y, y], **LINE_KW)


def branch_to_side(ax, main_x, junction_y, side_x0):
    """Tee off the main vertical connector to a side exclusion box."""
    hline(ax, junction_y, main_x, side_x0)


def connect_main(ax, y_top, y_bottom):
    vline(ax, MAIN_XC, y_top, y_bottom)


fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)
ax.invert_yaxis()
ax.axis("off")

# ── M1: source population + candidate variables ─────────────────────────────
M1_Y0, M1_Y1 = 4, 28
draw_box(ax, MAIN_X0, MAIN_X1, M1_Y0, M1_Y1,
         "KNHANES 2020–2024 (pooled), 5 waves\n"
         "N = 34,640 respondents assessed\n"
         "Candidate variables: 66 assessed → 57 retained")

connect_main(ax, M1_Y1, 42)
J1 = 34
S1_Y0, S1_Y1 = 22, 46
draw_box(ax, SIDE_X0, SIDE_X1, S1_Y0, S1_Y1,
         "Variables excluded (n = 9)\n"
         "• Missingness, NaN > 30% (n=5):\n"
         "  DI4_dg, DE1_4, BS3_1,\n"
         "  BD2_1, LW_ms\n"
         "• Redundancy / definitional\n"
         "  overlap, a priori (n=4):\n"
         "  HE_obe, HE_wc, HE_glu, N_EN",
         fontsize=8.3)
branch_to_side(ax, MAIN_XC, J1, SIDE_X0)

# ── M2: age-eligibility filter ───────────────────────────────────────────────
M2_Y0, M2_Y1 = 42, 62
draw_box(ax, MAIN_X0, MAIN_X1, M2_Y0, M2_Y1,
         "Age-eligibility filter\n"
         "A (≥50): n = 17,545\n"
         "B (≥65): n = 9,003")

connect_main(ax, M2_Y1, 76)
J2 = 69
S2_Y0, S2_Y1 = 60, 78
draw_box(ax, SIDE_X0, SIDE_X1, S2_Y0, S2_Y1,
         "Excluded, below age threshold\n"
         "A (age < 50): excl. 17,095\n"
         "B (age < 65): excl. 25,637",
         fontsize=8.6)
branch_to_side(ax, MAIN_XC, J2, SIDE_X0)

# ── M3: missing/invalid target excluded -> analytic cohort ─────────────────
M3_Y0, M3_Y1 = 76, 98
draw_box(ax, MAIN_X0, MAIN_X1, M3_Y0, M3_Y1,
         "Missing/invalid target (O_TC) excluded\n"
         "A: analytic cohort n = 14,871\n"
         "B: analytic cohort n = 7,704")

connect_main(ax, M3_Y1, 112)
J3 = 105
S3_Y0, S3_Y1 = 96, 114
draw_box(ax, SIDE_X0, SIDE_X1, S3_Y0, S3_Y1,
         "Excluded, missing/invalid O_TC\n"
         "A: excl. 2,674\n"
         "B: excl. 1,299",
         fontsize=8.6)
branch_to_side(ax, MAIN_XC, J3, SIDE_X0)

# ── M4: data preparation ─────────────────────────────────────────────────────
M4_Y0, M4_Y1 = 112, 142
draw_box(ax, MAIN_X0, MAIN_X1, M4_Y0, M4_Y1,
         "Data preparation\n"
         "• Missingness/collinearity screen (VIF): confirms\n"
         "  the 9 a priori exclusions above; 0 further\n"
         "  variables dropped from the 57 retained\n"
         "• Derive eGFR, diabetes, hypertension, brush_freq\n"
         "• Missing predictor values imputed (mode/median,\n"
         "  fit on development set only)",
         fontsize=8.6)

# ── Branch into ML vs. Inferential arms ──────────────────────────────────────
BRANCH_Y = 156
connect_main(ax, M4_Y1, BRANCH_Y)

ML_XC, INF_XC = 22, 76
hline(ax, BRANCH_Y, ML_XC, INF_XC)
vline(ax, ML_XC, BRANCH_Y, 162)
vline(ax, INF_XC, BRANCH_Y, 162)

ARM_Y0, ARM_Y1 = 162, 188
ML_X0, ML_X1 = 4, 40
INF_X0, INF_X1 = 58, 96

draw_box(ax, ML_X0, ML_X1, ARM_Y0, ARM_Y1,
         "ML (predictive) arm\n"
         "Temporal split:\n"
         "Development (2020–2023) vs.\n"
         "Evaluation (2024)",
         fontsize=9)

draw_box(ax, INF_X0, INF_X1, ARM_Y0, ARM_Y1,
         "Inferential (confirmatory) arm\n"
         "Full pooled cohort,\n"
         "survey-weighted (strata/PSU/weight)\n"
         "No development/evaluation split",
         fontsize=9)

# ── Leaves: ML arm splits into A/B Dev/Eval; Inferential arm into A/B n's ───
LEAF_Y0, LEAF_Y1 = 200, 220
LEAF_BRANCH_Y = 194

# ML leaves
ML_AX, ML_BX = 13, 31
connect_main_ml = None
vline(ax, ML_XC, ARM_Y1, LEAF_BRANCH_Y)
hline(ax, LEAF_BRANCH_Y, ML_AX, ML_BX)
vline(ax, ML_AX, LEAF_BRANCH_Y, LEAF_Y0)
vline(ax, ML_BX, LEAF_BRANCH_Y, LEAF_Y0)
draw_box(ax, 4, 22, LEAF_Y0, LEAF_Y1,
         "A\nDev n = 11,536\nEval n = 3,335", fontsize=8.8)
draw_box(ax, 24, 42, LEAF_Y0, LEAF_Y1,
         "B\nDev n = 5,946\nEval n = 1,758", fontsize=8.8)

# Inferential leaves
INF_AX, INF_BX = 67, 85
vline(ax, INF_XC, ARM_Y1, LEAF_BRANCH_Y)
hline(ax, LEAF_BRANCH_Y, INF_AX, INF_BX)
vline(ax, INF_AX, LEAF_BRANCH_Y, LEAF_Y0)
vline(ax, INF_BX, LEAF_BRANCH_Y, LEAF_Y0)
draw_box(ax, 58, 76, LEAF_Y0, LEAF_Y1,
         "A\nn = 14,871", fontsize=8.8)
draw_box(ax, 78, 96, LEAF_Y0, LEAF_Y1,
         "B\nn = 7,704", fontsize=8.8)

plt.tight_layout()
fig.savefig(OUT_BASENAME + ".png", dpi=300, facecolor="white")
fig.savefig(OUT_BASENAME + ".pdf", facecolor="white")
print(f"Saved {OUT_BASENAME}.png and .pdf")
