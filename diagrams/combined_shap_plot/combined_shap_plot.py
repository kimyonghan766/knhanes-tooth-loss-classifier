"""
Combined mean |SHAP| feature-importance chart, ≥50 vs ≥65 cohort, side by side.

Run the new "Save mean |SHAP| ..." cell in final.ipynb and final(65+).ipynb first
(inserted right after the existing "Global feature importance" bar-plot cell) —
each writes an .npz with feature_names / mean_abs_shap / model_name into Main/.
Then run this script from Main/:

    python3 combined_shap_plot.py
"""
import numpy as np
import matplotlib.pyplot as plt

N_DISPLAY = 20

COHORTS = [
    {"label": "≥50 cohort", "npz": "shap_importance_50plus.npz"},
    {"label": "≥65 cohort", "npz": "shap_importance_65plus.npz"},
]


def load_top_features(npz_path, n_display=N_DISPLAY):
    data = np.load(npz_path, allow_pickle=True)
    names = data["feature_names"]
    values = data["mean_abs_shap"]
    model_name = str(data["model_name"])
    order = np.argsort(values)[::-1][:n_display]
    return names[order][::-1], values[order][::-1], model_name


def plot_combined(cohorts, out_path="combined_shap_importance.png"):
    fig, axes = plt.subplots(
        1, len(cohorts),
        figsize=(6.5 * len(cohorts), 4.5),
        constrained_layout=True,
    )
    if len(cohorts) == 1:
        axes = [axes]

    for ax, cohort in zip(axes, cohorts):
        names, values, model_name = load_top_features(cohort["npz"])
        ax.barh(names, values, color="#1f77ff", height=0.7)
        ax.set_title(f'{cohort["label"]} — {model_name}', fontsize=11)
        ax.set_xlabel("mean(|SHAP value|)", fontsize=9)
        ax.tick_params(axis="y", labelsize=8)
        ax.tick_params(axis="x", labelsize=8)
        ax.margins(y=0.01)

    fig.suptitle("Mean |SHAP| Feature Importance", fontsize=13)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")
    plt.show()


if __name__ == "__main__":
    plot_combined(COHORTS)
