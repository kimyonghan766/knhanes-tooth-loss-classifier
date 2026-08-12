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

Box sizing: every box's height is computed from its own line count and font
size (box_h below), rather than a fixed height per row -- the previous
version used generous fixed heights that left large empty margins around
short text blocks. UNITS_PER_INCH is pinned to the original figure's scale
(222 data-units / 16.5 in) so a given font size occupies the same physical
size on the page as before; only the padding around the text shrinks.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_BASENAME = os.path.join(HERE, "study_flow_diagram")

plt.rcParams["font.family"] = "serif"

XLIM = (0, 100)
UNITS_PER_INCH = 222 / 16.5       # pinned to the original figure's scale (data-units per inch)
LINESPACING = 1.55                # matches draw_box's linespacing
PAD_LINES = 0.9                   # extra whitespace above+below the text, in units of "lines"

MAIN_X0, MAIN_X1 = 6, 58          # main-column box span
MAIN_XC = (MAIN_X0 + MAIN_X1) / 2
SIDE_X0, SIDE_X1 = 66, 97         # exclusion side-box span

BOX_KW = dict(facecolor="white", edgecolor="black", linewidth=1.2, zorder=3)
LINE_KW = dict(color="black", linewidth=1.1, zorder=2)

MAIN_GAP = 9                      # vertical connector length between stacked main boxes
BRANCH_GAP = 6                    # branch point -> arm row, and arm row -> leaf-branch point
LEAF_GAP = 6                      # leaf-branch point -> leaf row
TOP_MARGIN = 4
BOTTOM_MARGIN = 4


def box_h(text, fontsize):
    n_lines = text.count("\n") + 1
    line_h = (fontsize / 72) * LINESPACING * UNITS_PER_INCH
    return (n_lines + PAD_LINES) * line_h


def draw_box(ax, x0, x1, y0, y1, text, fontsize=9.5, weight="normal"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **BOX_KW))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center",
             fontsize=fontsize, weight=weight, linespacing=LINESPACING, zorder=4)


def vline(ax, x, y0, y1):
    ax.plot([x, x], [y0, y1], **LINE_KW)


def hline(ax, y, x0, x1):
    ax.plot([x0, x1], [y, y], **LINE_KW)


def branch_to_side(ax, main_x, junction_y, side_x0):
    """Tee off the main vertical connector to a side exclusion box."""
    hline(ax, junction_y, main_x, side_x0)


def connect_main(ax, y_top, y_bottom):
    vline(ax, MAIN_XC, y_top, y_bottom)


# ── Box text (unchanged from the previous version) ───────────────────────────
M1_TEXT = ("KNHANES 2020–2024 (pooled), 5 waves\n"
           "N = 34,640 respondents assessed\n"
           "Candidate variables: 66 assessed → 57 retained")
S1_TEXT = ("Variables excluded (n = 9)\n"
           "• Missingness, NaN > 30% (n=5):\n"
           "  DI4_dg, DE1_4, BS3_1,\n"
           "  BD2_1, LW_ms\n"
           "• Redundancy / definitional\n"
           "  overlap, a priori (n=4):\n"
           "  HE_obe, HE_wc, HE_glu, N_EN")
M2_TEXT = ("Age-eligibility filter\n"
           "A (≥50): n = 17,545\n"
           "B (≥65): n = 9,003")
S2_TEXT = ("Excluded, below age threshold\n"
           "A (age < 50): excl. 17,095\n"
           "B (age < 65): excl. 25,637")
M3_TEXT = ("Missing/invalid target (O_TC) excluded\n"
           "A: analytic cohort n = 14,871\n"
           "B: analytic cohort n = 7,704")
S3_TEXT = ("Excluded, missing/invalid O_TC\n"
           "A: excl. 2,674\n"
           "B: excl. 1,299")
M4_TEXT = ("Data preparation\n"
           "• Missingness/collinearity screen (VIF): confirms\n"
           "  the 9 a priori exclusions above; 0 further\n"
           "  variables dropped from the 57 retained\n"
           "• Derive eGFR, diabetes, hypertension, brush_freq\n"
           "• Missing predictor values imputed (mode/median,\n"
           "  fit on development set only)")
ML_TEXT = ("ML (predictive) arm\n"
           "Temporal split:\n"
           "Development (2020–2023) vs.\n"
           "Evaluation (2024)")
INF_TEXT = ("Inferential (confirmatory) arm\n"
            "Full pooled cohort,\n"
            "survey-weighted (strata/PSU/weight)\n"
            "No development/evaluation split")
ML_LEAF_A_TEXT = "A\nDev n = 11,536\nEval n = 3,335"
ML_LEAF_B_TEXT = "B\nDev n = 5,946\nEval n = 1,758"
INF_LEAF_A_TEXT = "A\nn = 14,871"
INF_LEAF_B_TEXT = "B\nn = 7,704"

# ── Font sizes ─────────────────────────────────────────────────────────────
FS_MAIN = 12
FS_S1 = 10.5
FS_S2 = FS_S3 = 10.8
FS_M4 = 10.8
FS_ARM = 11.3
FS_LEAF = 11

# ── Vertical layout: a running cursor, box heights computed from their own
# text, main boxes stacked with a fixed connector gap, side boxes centred on
# the midpoint of that gap ────────────────────────────────────────────────
y = TOP_MARGIN

M1_Y0 = y
M1_Y1 = M1_Y0 + box_h(M1_TEXT, FS_MAIN)
J1 = M1_Y1 + MAIN_GAP / 2
h_s1 = box_h(S1_TEXT, FS_S1)
S1_Y0, S1_Y1 = J1 - h_s1 / 2, J1 + h_s1 / 2

M2_Y0 = M1_Y1 + MAIN_GAP
M2_Y1 = M2_Y0 + box_h(M2_TEXT, FS_MAIN)
J2 = M2_Y1 + MAIN_GAP / 2
h_s2 = box_h(S2_TEXT, FS_S2)
S2_Y0, S2_Y1 = J2 - h_s2 / 2, J2 + h_s2 / 2

M3_Y0 = M2_Y1 + MAIN_GAP
M3_Y1 = M3_Y0 + box_h(M3_TEXT, FS_MAIN)
J3 = M3_Y1 + MAIN_GAP / 2
h_s3 = box_h(S3_TEXT, FS_S3)
S3_Y0, S3_Y1 = J3 - h_s3 / 2, J3 + h_s3 / 2

M4_Y0 = M3_Y1 + MAIN_GAP
M4_Y1 = M4_Y0 + box_h(M4_TEXT, FS_M4)

BRANCH_Y = M4_Y1 + BRANCH_GAP

ARM_Y0 = BRANCH_Y + BRANCH_GAP
ARM_Y1 = ARM_Y0 + max(box_h(ML_TEXT, FS_ARM), box_h(INF_TEXT, FS_ARM))

LEAF_BRANCH_Y = ARM_Y1 + BRANCH_GAP
LEAF_Y0 = LEAF_BRANCH_Y + LEAF_GAP
LEAF_Y1 = LEAF_Y0 + max(box_h(ML_LEAF_A_TEXT, FS_LEAF), box_h(ML_LEAF_B_TEXT, FS_LEAF),
                        box_h(INF_LEAF_A_TEXT, FS_LEAF), box_h(INF_LEAF_B_TEXT, FS_LEAF))

YLIM = (0, LEAF_Y1 + BOTTOM_MARGIN)
FIG_W = 12.0
FIG_H = YLIM[1] / UNITS_PER_INCH

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)
ax.invert_yaxis()
ax.axis("off")

# ── M1: source population + candidate variables ─────────────────────────────
draw_box(ax, MAIN_X0, MAIN_X1, M1_Y0, M1_Y1, M1_TEXT, fontsize=FS_MAIN)
connect_main(ax, M1_Y1, M2_Y0)
draw_box(ax, SIDE_X0, SIDE_X1, S1_Y0, S1_Y1, S1_TEXT, fontsize=FS_S1)
branch_to_side(ax, MAIN_XC, J1, SIDE_X0)

# ── M2: age-eligibility filter ───────────────────────────────────────────────
draw_box(ax, MAIN_X0, MAIN_X1, M2_Y0, M2_Y1, M2_TEXT, fontsize=FS_MAIN)
connect_main(ax, M2_Y1, M3_Y0)
draw_box(ax, SIDE_X0, SIDE_X1, S2_Y0, S2_Y1, S2_TEXT, fontsize=FS_S2)
branch_to_side(ax, MAIN_XC, J2, SIDE_X0)

# ── M3: missing/invalid target excluded -> analytic cohort ─────────────────
draw_box(ax, MAIN_X0, MAIN_X1, M3_Y0, M3_Y1, M3_TEXT, fontsize=FS_MAIN)
connect_main(ax, M3_Y1, M4_Y0)
draw_box(ax, SIDE_X0, SIDE_X1, S3_Y0, S3_Y1, S3_TEXT, fontsize=FS_S3)
branch_to_side(ax, MAIN_XC, J3, SIDE_X0)

# ── M4: data preparation ─────────────────────────────────────────────────────
draw_box(ax, MAIN_X0, MAIN_X1, M4_Y0, M4_Y1, M4_TEXT, fontsize=FS_M4)

# ── Branch into ML vs. Inferential arms ──────────────────────────────────────
connect_main(ax, M4_Y1, BRANCH_Y)

ML_XC, INF_XC = 22, 76
hline(ax, BRANCH_Y, ML_XC, INF_XC)
vline(ax, ML_XC, BRANCH_Y, ARM_Y0)
vline(ax, INF_XC, BRANCH_Y, ARM_Y0)

ML_X0, ML_X1 = 4, 40
INF_X0, INF_X1 = 58, 96

draw_box(ax, ML_X0, ML_X1, ARM_Y0, ARM_Y1, ML_TEXT, fontsize=FS_ARM)
draw_box(ax, INF_X0, INF_X1, ARM_Y0, ARM_Y1, INF_TEXT, fontsize=FS_ARM)

# ── Leaves: ML arm splits into A/B Dev/Eval; Inferential arm into A/B n's ───
# ML leaves
ML_AX, ML_BX = 13, 31
vline(ax, ML_XC, ARM_Y1, LEAF_BRANCH_Y)
hline(ax, LEAF_BRANCH_Y, ML_AX, ML_BX)
vline(ax, ML_AX, LEAF_BRANCH_Y, LEAF_Y0)
vline(ax, ML_BX, LEAF_BRANCH_Y, LEAF_Y0)
draw_box(ax, 4, 22, LEAF_Y0, LEAF_Y1, ML_LEAF_A_TEXT, fontsize=FS_LEAF)
draw_box(ax, 24, 42, LEAF_Y0, LEAF_Y1, ML_LEAF_B_TEXT, fontsize=FS_LEAF)

# Inferential leaves
INF_AX, INF_BX = 67, 85
vline(ax, INF_XC, ARM_Y1, LEAF_BRANCH_Y)
hline(ax, LEAF_BRANCH_Y, INF_AX, INF_BX)
vline(ax, INF_AX, LEAF_BRANCH_Y, LEAF_Y0)
vline(ax, INF_BX, LEAF_BRANCH_Y, LEAF_Y0)
draw_box(ax, 58, 76, LEAF_Y0, LEAF_Y1, INF_LEAF_A_TEXT, fontsize=FS_LEAF)
draw_box(ax, 78, 96, LEAF_Y0, LEAF_Y1, INF_LEAF_B_TEXT, fontsize=FS_LEAF)

plt.tight_layout()
fig.savefig(OUT_BASENAME + ".png", dpi=600, facecolor="white")
fig.savefig(OUT_BASENAME + ".pdf", facecolor="white")
print(f"Saved {OUT_BASENAME}.png (600 dpi) and .pdf  (figure size {FIG_W:.2f} x {FIG_H:.2f} in)")
