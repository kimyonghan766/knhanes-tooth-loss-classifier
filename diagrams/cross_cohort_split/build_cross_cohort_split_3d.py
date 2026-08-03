"""
Combined Temporal Train / Test Split — single faux-3D column chart.

x-axis  : survey years 2020-2024
depth   : Aged 65+ blocks in front, Aged 50+ blocks offset up-and-behind
colour  : cohort (50+ = blue, 65+ = orange)
texture : the 2024 (Test) bar of each cohort is hatched
counts  : reproduced exactly as at the split cell in final.ipynb / final(65+).ipynb
          (row filters before that cell: age >= threshold, then dropna on O_TC)

Output: cross_cohort_split_3d.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon, Patch

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(HERE, "..", "..", "csv")   # repo-root csv/, two levels up from this script
CSV_FILES = ["HN20_all.csv", "HN21_all.csv", "HN22_all.csv",
             "HN23_all.csv", "HN24_all.csv"]

COLOR_50 = "#4C72B0"   # front cohort
COLOR_65 = "#DD8452"   # back cohort
TEST_YEAR = 2024.0
YEARS = [2020, 2021, 2022, 2023, 2024]

# ---- geometry (arbitrary drawing units; axes are hidden) --------------------
SX = 3.0            # horizontal spacing between year slots
BW = 1.15           # bar width
EXT = (0.42, 0.42)  # extrusion vector -> block "thickness" (the 3-D skew)
DEPTH = (0.9, 1.0)  # offset of the back (65+) cohort: right & up
LEFT_MARGIN = 0.8
TALLEST = 6.0       # tallest bar maps to this height
LABEL_GAP = 0.6     # vertical clearance between a block's top and its value label


def load_raw():
    frames = [pd.read_csv(f"{CSV_DIR}/{f}", low_memory=False,
                          usecols=["year", "age", "O_TC"])
              for f in CSV_FILES]
    return pd.concat(frames, ignore_index=True)


def year_counts_for(df, age_threshold):
    sub = df[df["age"] >= age_threshold].copy()
    sub["O_TC"] = pd.to_numeric(sub["O_TC"], errors="coerce")
    sub["O_TC"] = sub["O_TC"].replace([np.inf, -np.inf], np.nan)
    sub = sub.dropna(subset=["O_TC"])
    return sub["year"].value_counts().sort_index()


def lighten(c, f=0.28):
    r, g, b = mcolors.to_rgb(c)
    return tuple(x + (1 - x) * f for x in (r, g, b))


def darken(c, f=0.68):
    r, g, b = mcolors.to_rgb(c)
    return (r * f, g * f, b * f)


def draw_block(ax, x0, base_y, height, color, hatch=False, z=0):
    """Draw one faux-3-D column: right + top faces, then the hatched front face."""
    vx, vy = EXT
    top = base_y + height

    # right side face (darker)
    right = [(x0 + BW, base_y), (x0 + BW + vx, base_y + vy),
             (x0 + BW + vx, top + vy), (x0 + BW, top)]
    ax.add_patch(Polygon(right, closed=True, facecolor=darken(color),
                         edgecolor="white", linewidth=0.6, zorder=z))

    # top face (lighter)
    topf = [(x0, top), (x0 + BW, top),
            (x0 + BW + vx, top + vy), (x0 + vx, top + vy)]
    ax.add_patch(Polygon(topf, closed=True, facecolor=lighten(color),
                         edgecolor="white", linewidth=0.6, zorder=z + 1))

    # front face (base colour, hatched for the test year)
    front = [(x0, base_y), (x0 + BW, base_y), (x0 + BW, top), (x0, top)]
    ax.add_patch(Polygon(
        front, closed=True, facecolor=color, edgecolor="white", linewidth=0.6,
        hatch="////" if hatch else None, zorder=z + 2))


def main():
    df = load_raw()
    yc = {50: year_counts_for(df, 50), 65: year_counts_for(df, 65)}
    vscale = TALLEST / max(yc[50].max(), yc[65].max())

    fig, ax = plt.subplots(figsize=(14, 7))

    # background reference gridlines (relative to the front baseline)
    x_span_end = LEFT_MARGIN + (len(YEARS) - 1) * SX + BW + DEPTH[0] + EXT[0] + 0.4
    for gc in range(0, int(max(yc[50].max(), yc[65].max())) + 1, 1000):
        gy = gc * vscale
        ax.plot([LEFT_MARGIN - 0.4, x_span_end], [gy, gy],
                color="#d9d9d9", linewidth=0.8, zorder=0)
        ax.text(LEFT_MARGIN - 0.6, gy, f"{gc:,}", ha="right", va="center",
                fontsize=9, color="#666")

    for i, yr in enumerate(YEARS):
        xc = LEFT_MARGIN + i * SX
        is_test = (float(yr) == TEST_YEAR)

        # back cohort (50+) first so the front cohort overlaps it
        c50 = yc[50].get(float(yr), 0)
        bx, by = xc + DEPTH[0], DEPTH[1]
        draw_block(ax, bx, by, c50 * vscale, COLOR_50, hatch=is_test, z=10 + i * 4)
        # label leans toward the right portion of the back block's top face —
        # a centered label would sit almost directly above the front block's
        # right edge and get clipped by it; shifting right clears that overlap
        ax.text(bx + BW * 1.15, by + c50 * vscale + EXT[1] + LABEL_GAP,
                f"{c50:,}", ha="center", va="bottom", fontsize=9,
                fontweight="bold", color="black", zorder=100)

        # front cohort (65+)
        c65 = yc[65].get(float(yr), 0)
        draw_block(ax, xc, 0.0, c65 * vscale, COLOR_65, hatch=is_test, z=12 + i * 4)
        ax.text(xc + BW / 2, c65 * vscale + LABEL_GAP, f"{c65:,}", ha="center",
                va="bottom", fontsize=9, fontweight="bold",
                color="black", zorder=100)

        # year label under the front bar
        ax.text(xc + BW / 2, -0.45, str(yr), ha="center", va="top",
                fontsize=11, color="#333")

    # titles
    t50, te50 = yc[50][yc[50].index != TEST_YEAR].sum(), yc[50].get(TEST_YEAR, 0)
    t65, te65 = yc[65][yc[65].index != TEST_YEAR].sum(), yc[65].get(TEST_YEAR, 0)
    ax.set_title("Temporal Train / Test Split by Cohort", fontsize=16,
                 fontweight="bold", pad=26)
    ax.text(0.5, 1.015,
            f"Aged 50+  Train n={t50:,} | Test n={te50:,}        "
            f"Aged 65+  Train n={t65:,} | Test n={te65:,}",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=11, color="#444")

    legend_elements = [
        Patch(facecolor=COLOR_50, edgecolor="white", label="Aged 50+"),
        Patch(facecolor=COLOR_65, edgecolor="white", label="Aged 65+"),
        Patch(facecolor="white", edgecolor="#666", hatch="////",
              label="2024 (Test year)"),
    ]
    ax.legend(handles=legend_elements, fontsize=10, framealpha=0.3,
              loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.02))

    ax.set_xlim(LEFT_MARGIN - 1.2, x_span_end + 0.2)
    ax.set_ylim(-1.2, TALLEST + DEPTH[1] + EXT[1] + 0.9)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()
    fig.savefig(os.path.join(HERE, "cross_cohort_split_3d.png"), dpi=150, bbox_inches="tight")
    print("Saved cross_cohort_split_3d.png")
    print(f"50+  train={t50:,}  test={te50:,}")
    print(f"65+  train={t65:,}  test={te65:,}")


if __name__ == "__main__":
    main()
