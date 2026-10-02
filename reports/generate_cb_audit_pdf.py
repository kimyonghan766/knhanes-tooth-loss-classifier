from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "CB_Notebook_Audit_Report.pdf"

NAVY = "#17324D"
BLUE = "#246B9E"
LIGHT_BLUE = "#EAF3F8"
RED = "#A63D40"
AMBER = "#A66A00"
GREEN = "#2F6B4F"
GRAY = "#4B5563"
LIGHT_GRAY = "#F3F4F6"
WHITE = "#FFFFFF"


def new_page(title, subtitle=None):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0.94), 1, 0.06, color=NAVY, ec="none"))
    ax.text(0.06, 0.965, "CB NOTEBOOK JOURNAL-CODE AUDIT", color=WHITE,
            fontsize=9, fontweight="bold", va="center")
    ax.text(0.06, 0.91, title, color=NAVY, fontsize=20, fontweight="bold", va="top")
    y = 0.875
    if subtitle:
        ax.text(0.06, y, subtitle, color=GRAY, fontsize=9.5, va="top")
        y -= 0.04
    return fig, ax, y


def footer(ax, page):
    ax.plot([0.06, 0.94], [0.045, 0.045], color="#D1D5DB", lw=0.8)
    ax.text(0.06, 0.025, "Read-only audit; no analysis notebooks were modified.",
            fontsize=7.5, color=GRAY, va="center")
    ax.text(0.94, 0.025, str(page), fontsize=8, color=GRAY, ha="right", va="center")


def section(ax, y, text, color=NAVY):
    ax.text(0.06, y, text, fontsize=13, fontweight="bold", color=color, va="top")
    return y - 0.032


def paragraph(ax, y, text, width=103, size=9.1, color="#20242A", leading=0.0205, x=0.06):
    lines = []
    for block in text.split("\n"):
        lines.extend(textwrap.wrap(block, width=width) or [""])
    ax.text(x, y, "\n".join(lines), fontsize=size, color=color, va="top",
            linespacing=1.28)
    return y - leading * len(lines) - 0.012


def bullet(ax, y, text, severity=None, width=94, size=8.9):
    colors = {"CRITICAL": RED, "HIGH": AMBER, "MEDIUM": BLUE, "PASS": GREEN}
    x_text = 0.09
    if severity:
        ax.text(0.06, y, severity, fontsize=7.2, fontweight="bold",
                color=WHITE, va="top",
                bbox=dict(boxstyle="round,pad=0.25", fc=colors[severity], ec="none"))
        x_text = 0.16
        width -= 8
    else:
        ax.text(0.066, y, "•", fontsize=11, color=BLUE, va="top")
    lines = textwrap.wrap(text, width=width)
    ax.text(x_text, y, "\n".join(lines), fontsize=size, color="#20242A", va="top",
            linespacing=1.25)
    return y - 0.0195 * len(lines) - 0.010


def finding(ax, y, number, title, body, severity="HIGH"):
    colors = {"CRITICAL": RED, "HIGH": AMBER, "MEDIUM": BLUE}
    ax.text(0.06, y, f"{number}", fontsize=9, fontweight="bold", color=WHITE,
            va="top", ha="center",
            bbox=dict(boxstyle="circle,pad=0.35", fc=colors[severity], ec="none"))
    ax.text(0.095, y + 0.001, title, fontsize=10.5, fontweight="bold",
            color=NAVY, va="top")
    y -= 0.027
    return paragraph(ax, y, body, width=99, size=8.6, leading=0.0185)


def add_table(ax, y, columns, rows, widths=None, height=0.18, font_size=8.4):
    table_ax = ax.inset_axes([0.06, y - height, 0.88, height])
    table_ax.axis("off")
    table = table_ax.table(cellText=rows, colLabels=columns, cellLoc="left",
                           colLoc="left", loc="upper left", bbox=[0, 0, 1, 1],
                           colWidths=widths)
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#D1D5DB")
        cell.set_linewidth(0.6)
        cell.PAD = 0.04
        if r == 0:
            cell.set_facecolor(NAVY)
            cell.get_text().set_color(WHITE)
            cell.get_text().set_fontweight("bold")
        elif r % 2 == 0:
            cell.set_facecolor(LIGHT_GRAY)
    return y - height - 0.025


def cover(pdf):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0.72), 1, 0.28, color=NAVY, ec="none"))
    ax.add_patch(Rectangle((0.06, 0.13), 0.012, 0.49, color=BLUE, ec="none"))
    ax.text(0.08, 0.91, "JOURNAL SUBMISSION CODE AUDIT", fontsize=11,
            fontweight="bold", color="#9CCBE3")
    ax.text(0.08, 0.83, "Cross-Cohort CB Notebook\nConsistency & Methods Report",
            fontsize=27, fontweight="bold", color=WHITE, va="top", linespacing=1.15)
    ax.text(0.09, 0.61, "Notebooks reviewed", fontsize=10, fontweight="bold", color=NAVY)
    ax.text(0.09, 0.575, "CB_50+.ipynb\nCB_50-64.ipynb\nCB_65+.ipynb",
            fontsize=11, color="#20242A", va="top", linespacing=1.55)
    ax.text(0.09, 0.43, "Overall verdict", fontsize=10, fontweight="bold", color=NAVY)
    ax.text(0.09, 0.39, "Internally synchronized, but not yet submission-ready",
            fontsize=15, fontweight="bold", color=RED)
    summary = (
        "The three cohort implementations reconcile well: cohort counts, target coding, "
        "feature order, preprocessing, survey identifiers, and core formulas are aligned. "
        "Submission readiness is limited by stale notebook outputs, tuning-dependent OOF "
        "claims, temporal-test leakage during feature screening, survey-incompatible model "
        "comparison inference, and drift between the notebooks and repository documentation."
    )
    paragraph(ax, 0.345, summary, width=84, size=10.2, leading=0.023, x=0.09)
    ax.text(0.09, 0.17, "Prepared: 1 October 2026", fontsize=9, color=GRAY)
    ax.text(0.09, 0.145, "Project: PROJECT_DATA_ANALYSIS (TEETHCOUNT)", fontsize=9, color=GRAY)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def build_report():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUTPUT) as pdf:
        cover(pdf)

        fig, ax, y = new_page("Executive summary", "Scope, verdict, and the most consequential findings")
        y = section(ax, y, "Verdict")
        y = paragraph(ax, y, (
            "The notebooks are substantially consistent with one another, but the current repository "
            "should not be treated as a final journal analysis package. The largest risk is not a "
            "cross-cohort coding mismatch; it is that the same shared methodology contains validation "
            "and inferential weaknesses, while the saved outputs and documentation no longer represent "
            "the current source code."
        ))
        y = section(ax, y, "Priority findings")
        for sev, txt in [
            ("CRITICAL", "Saved notebook outputs were generated by an earlier version of at least one cell; a clean full rerun is required."),
            ("CRITICAL", "The reported OOF scores, thresholds, and recalibration reuse the folds used for Optuna selection and are not tuning-independent."),
            ("HIGH", "Feature screening uses 2024 data even though 2024 is presented as a temporal holdout."),
            ("HIGH", "Unweighted DeLong p-values assume independent observations and are not valid for clustered KNHANES data; ten pairwise tests are also unadjusted."),
            ("HIGH", "The 81–82-term survey regressions include sparse levels, high VIF terms, and no multiplicity adjustment; the 50–64 model is especially saturated."),
            ("HIGH", "README.md and ENVIRONMENT.md describe a materially different pipeline from the current notebooks."),
        ]:
            y = bullet(ax, y, txt, severity=sev)
        y = section(ax, y, "What this means")
        y = paragraph(ax, y, (
            "The 2024 test set remains separate from model fitting, so its discrimination results are not "
            "invalidated merely by the OOF issue. However, development performance, threshold selection, "
            "calibration, feature-policy provenance, inferential p-values, and the reproducibility trail "
            "need correction or more cautious labeling before submission."
        ))
        footer(ax, 2); pdf.savefig(fig); plt.close(fig)

        fig, ax, y = new_page("Cross-cohort reconciliation", "Checks that passed across all three notebooks")
        y = section(ax, y, "Cohort arithmetic")
        rows = [
            ["Total eligible sample", "14,871", "7,167 + 7,704", "Pass"],
            ["≥20 teeth", "10,730", "6,384 + 4,346", "Pass"],
            ["<20 teeth", "4,141", "783 + 3,358", "Pass"],
            ["Training rows (2020–2023)", "11,536", "5,590 + 5,946", "Pass"],
            ["Test rows (2024)", "3,335", "1,577 + 1,758", "Pass"],
            ["Regression complete cases", "11,695", "5,905 + 5,790", "Pass"],
        ]
        y = add_table(ax, y, ["Check", "50+", "50–64 + 65+", "Status"], rows,
                      widths=[0.42, 0.16, 0.27, 0.15], height=0.225)
        y = section(ax, y, "Structural checks")
        for txt in [
            "All three notebooks contain valid Python syntax and no saved exception outputs.",
            "Code differences are limited to intended cohort filters, cohort labels, comments, and cohort-specific SHAP filenames.",
            "All ML matrices contain 88 features in identical order, without duplicate names.",
            "Each CatBoost SHAP artifact contains 88 feature names and 88 importance values and identifies CatBoost as the explained model.",
            "Observed tooth counts span 0–32; no retained target value falls outside the valid range.",
            "Alcohol, stress, vaping, fruit, and vegetable recodes agree between the predictive and inferential arms.",
            "The CKD-EPI 2021 eGFR equation and calcium/sodium reporting-unit conversions are identical across notebooks.",
            "Median/mode imputation is fitted inside the model pipelines, including inside CV folds.",
            "Year-specific strata and PSU identifiers are constructed consistently for pooled survey analyses.",
        ]:
            y = bullet(ax, y, txt, severity="PASS")
        footer(ax, 3); pdf.savefig(fig); plt.close(fig)

        fig, ax, y = new_page("Submission-blocking findings I", "Reproducibility, temporal validation, and model development")
        y = finding(ax, y, 1, "Saved output/source mismatch", (
            "The current Platt-scaling cell uses LogisticRegression(C=np.inf), while its saved stderr contains "
            "warnings stating that penalty=None was used. Those warnings cannot be produced by the current "
            "cell. The source was therefore edited after execution. Any table, plot, artifact, or downstream "
            "script that reads saved notebook output must be regenerated after a clean restart-and-run-all."
        ), "CRITICAL")
        y = finding(ax, y, 2, "OOF estimates reuse the tuning folds", (
            "Optuna selects hyperparameters from five-fold CV and cross_val_predict then evaluates the selected "
            "configuration on the same fold partition. Predictions are out-of-fold for fitting, but fold outcomes "
            "already influenced hyperparameter selection. Consequently, OOF AUPRC, model ranking, MCC/Youden "
            "thresholds, Platt calibration, and their bootstrap intervals are not tuning-independent. Use nested "
            "CV or separate tuning and calibration/threshold partitions."
        ), "CRITICAL")
        y = finding(ax, y, 3, "The 2024 temporal test informs feature screening", (
            "Missingness, VIF, and redundancy diagnostics are run on the full 2020–2024 50+ sample, and the "
            "resulting policy is applied to the models. If 2024 is the external temporal holdout, candidate "
            "exclusions, rare-level pooling rules, and other data-derived preprocessing choices should be fixed "
            "using 2020–2023 only."
        ), "HIGH")
        y = finding(ax, y, 4, "Random CV ignores survey clusters", (
            "StratifiedKFold can place respondents from the same PSU in different folds. Even without repeated "
            "individuals, within-cluster similarity may make internal validation optimistic. A grouped or "
            "stratified-group design using year-specific PSU identifiers should be considered and reported."
        ), "MEDIUM")
        footer(ax, 4); pdf.savefig(fig); plt.close(fig)

        fig, ax, y = new_page("Submission-blocking findings II", "Survey inference and the adjusted-odds-ratio model")
        y = finding(ax, y, 5, "DeLong p-values do not respect the survey design", (
            "The implemented fast DeLong test assumes unweighted, independent observations. KNHANES observations "
            "are clustered by PSU, so switching to unweighted AUC does not restore independence. In addition, ten "
            "pairwise model tests are judged at p<0.05 without multiplicity correction. Prefer a cluster-aware "
            "paired bootstrap of AUC differences, or present model differences descriptively without inferential claims."
        ), "HIGH")
        y = finding(ax, y, 6, "The inferential model is very large", (
            "The 50+ regression has 82 terms; each subgroup has 81 after zero-variance removal. The 50–64 model "
            "contains approximately 603 events, or about 7.4 events per term, and includes sparse dummy levels. "
            "A smaller prespecified model or principled category consolidation would yield more defensible estimates."
        ), "HIGH")
        y = finding(ax, y, 7, "Multiplicity correction is absent", (
            "The notebooks report nominal p-values across more than 80 regression terms. README.md claims Holm "
            "and Benjamini–Hochberg corrections, but no such correction exists in the notebook code. Implement "
            "the stated correction or remove the claim and frame the table as exploratory."
        ), "HIGH")
        y = finding(ax, y, 8, "High VIF terms remain in the reported models", (
            "The post-fit VIF table reports genertn_4=10.78 in the 50–64 model and cfam=10.91 plus occp_7=10.19 "
            "in the 65+ model. The notebook describes VIF>10 as serious, but takes no action. VIF assessment should "
            "inform the finalized specification or be accompanied by an explicit sensitivity analysis."
        ), "HIGH")
        y = finding(ax, y, 9, "Causal wording exceeds the design", (
            "The analysis is cross-sectional and includes plausible consequences of tooth loss, including oral "
            "pain, oral-health rating, dental visits, and recent brushing. Replace 'affect' and 'independent risk "
            "factor' with 'is associated with' unless a causal identification strategy is supplied."
        ), "HIGH")
        footer(ax, 5); pdf.savefig(fig); plt.close(fig)

        fig, ax, y = new_page("Calculation and reporting issues", "Specific corrections that affect interpretation or reproducibility")
        items = [
            ("10", "MCC threshold search can miss the optimum", "roc_curve drops intermediate thresholds by default. This is suitable for ROC plotting but not guaranteed to preserve the maximum of nonlinear MCC. Use drop_intermediate=False or all unique predicted probabilities.", "HIGH"),
            ("11", "Non-converged logistic-regression trials", "Saved tuning output contains 50 convergence warnings in 50+, 19 in 50–64, and 23 in 65+. Optuna therefore compared some incomplete fits. Increase max_iter, set a convergence policy, and fail or prune non-converged trials.", "HIGH"),
            ("12", "Pinned CatBoost is called the best model", "CatBoost is intentionally fixed for cross-cohort SHAP comparability, but XGBoost leads OOF AUPRC in 50–64 and logistic regression leads in 65+. Replace 'best model' with 'pinned CatBoost comparison model' throughout.", "MEDIUM"),
            ("13", "Calibration coefficients are mislabeled", "The displayed slope and intercept are Platt-recalibrator coefficients fitted to development OOF predictions. They are not 2024 test-set calibration slope and calibration-in-the-large diagnostics.", "HIGH"),
            ("14", "Weighting terminology is ambiguous", "Models are not survey-weighted, but they are outcome-class weighted. Thresholds are optimized on unweighted development data and evaluated using survey-weighted test metrics; this distinction should be explicit.", "MEDIUM"),
            ("15", "Table 1 omits nominal-level summaries", "tins, house, and live_t are tested, but no level labels are supplied, leaving their group-summary cells blank.", "MEDIUM"),
            ("16", "Screening verdict conflicts with the applied policy", "The automated table marks HE_BMI for exclusion at VIF>10 but the manual policy keeps HE_BMI and drops HE_obe. The clinical choice may be valid, but the displayed decision rule and actual action should agree.", "HIGH"),
        ]
        for n, title, body, sev in items:
            y = finding(ax, y, n, title, body, sev)
        footer(ax, 6); pdf.savefig(fig); plt.close(fig)

        fig, ax, y = new_page("Variable-definition and documentation findings", "Items requiring clarification in the methods and repository narrative")
        y = section(ax, y, "Variable definitions")
        y = bullet(ax, y, (
            "Diabetes is coded as diagnosed diabetes OR HbA1c ≥6.5%; fasting glucose is not included. "
            "The redundancy discussion nevertheless invokes fasting glucose ≥126 as a diagnostic criterion."
        ), severity="HIGH")
        y = bullet(ax, y, (
            "When one composite component is negative and the other is missing, diabetes and hypertension may "
            "be coded negative rather than unknown. This available-component rule should be stated and sensitivity-tested."
        ), severity="MEDIUM")
        y = bullet(ax, y, (
            "The screening narrative calls N_EN a sum of the retained nutrient variables. Energy intake is not "
            "literally the sum of calcium, sodium, protein, fiber, and sugar; the redundancy justification should be rewritten."
        ), severity="MEDIUM")
        y = section(ax, y, "Repository documentation drift")
        doc_rows = [
            ["Notebook names", "README/ENVIRONMENT cite nonexistent final.ipynb files"],
            ["Cohorts", "Documentation describes two cohorts; analysis now has three"],
            ["Age form", "README claims restricted cubic splines; code uses linear age"],
            ["Inference", "README claims Holm/BH correction; code reports nominal p-values"],
            ["Regression", "README describes ~32 terms/SHAP model; code has one 81–82-term model"],
            ["Variable roles", "Several variables described as ML-only are included in §11"],
            ["XGBoost", "README says class weight is tuned; current code fixes it from class counts"],
            ["Results", "Reported model winners and performance numbers are obsolete"],
        ]
        y = add_table(ax, y, ["Area", "Mismatch"], doc_rows, widths=[0.25, 0.75], height=0.29,
                      font_size=8.2)
        y = paragraph(ax, y, (
            "These files should be regenerated only after the final notebook code has been executed from a clean "
            "kernel. Cross-cohort figure scripts that parse saved notebook output must then be rerun as well."
        ), size=8.8)
        footer(ax, 7); pdf.savefig(fig); plt.close(fig)

        fig, ax, y = new_page("Recommended remediation plan", "Suggested order of operations before manuscript submission")
        steps = [
            ("1", "Freeze the analysis specification", "Decide the inferential exposure set, category pooling, multiplicity policy, CatBoost pin, survey estimand, and validation design before regenerating results."),
            ("2", "Move screening into development data", "Derive missingness/VIF/rare-level decisions from the 2020–2023 50+ reference cohort only, then apply the frozen rules unchanged to all cohorts and 2024."),
            ("3", "Correct internal validation", "Use nested CV or dedicated tuning versus calibration/threshold folds; consider year-specific PSU grouping."),
            ("4", "Repair model calculations", "Evaluate all MCC thresholds, enforce logistic-regression convergence, and label pinned versus selected models correctly."),
            ("5", "Strengthen survey inference", "Replace DeLong with a cluster-aware paired comparison or remove its p-values; simplify the aOR model and implement the stated multiple-testing correction."),
            ("6", "Centralize shared code", "Move preprocessing, feature schema, model builders, bootstraps, and survey identifiers into a tested Python module. Keep only cohort configuration in each notebook."),
            ("7", "Perform a clean reproducibility run", "Restart the kernel, run all three notebooks top-to-bottom, confirm no exceptions or convergence warnings, and record software/R package versions."),
            ("8", "Regenerate all deliverables", "Recreate SHAP files, cross-cohort figures, tables, README.md, and ENVIRONMENT.md from the clean run. Archive the exact submitted outputs."),
        ]
        for n, title, body in steps:
            ax.text(0.06, y, n, fontsize=9, fontweight="bold", color=WHITE, va="top", ha="center",
                    bbox=dict(boxstyle="circle,pad=0.35", fc=BLUE, ec="none"))
            ax.text(0.095, y + 0.001, title, fontsize=10.2, fontweight="bold", color=NAVY, va="top")
            y -= 0.025
            y = paragraph(ax, y, body, width=99, size=8.6, leading=0.018)
        footer(ax, 8); pdf.savefig(fig); plt.close(fig)

        fig, ax, y = new_page("Final assessment", "Journal-code readiness statement")
        ax.add_patch(Rectangle((0.06, y - 0.19), 0.88, 0.17, facecolor=LIGHT_BLUE,
                               edgecolor="#B7D4E5", linewidth=1.0))
        ax.text(0.09, y - 0.055, "NOT YET SUBMISSION-READY", fontsize=16,
                fontweight="bold", color=RED, va="top")
        ax.text(0.09, y - 0.10,
                "Cross-cohort implementation consistency: strong\n"
                "Methodological and inferential readiness: requires revision\n"
                "Output provenance and documentation readiness: requires full regeneration",
                fontsize=10, color="#20242A", va="top", linespacing=1.5)
        y -= 0.23
        y = section(ax, y, "Bottom line")
        y = paragraph(ax, y, (
            "The three notebooks behave as coordinated variants of one pipeline. Their counts, feature schemas, "
            "recodes, core calculations, and survey identifiers are aligned. The essential next step is not to "
            "repair cohort-to-cohort drift, but to revise the shared validation and inference strategy and establish "
            "a clean, auditable chain from final source code to notebook outputs, saved artifacts, figures, and manuscript text."
        ), width=100, size=10, leading=0.022)
        y = section(ax, y, "Audit basis")
        for txt in [
            "Cell-by-cell source comparison of CB_50+, CB_50-64, and CB_65+.",
            "Static syntax and notebook-output inspection.",
            "Raw-data checks for cohort arithmetic, target range, and selected code distributions.",
            "Cross-check of feature-name order and saved CatBoost SHAP artifacts.",
            "Review of README.md, ENVIRONMENT.md, requirements, and cross-cohort figure scripts.",
            "No analytical source file or notebook was modified during the audit.",
        ]:
            y = bullet(ax, y, txt)
        y = section(ax, y, "Files reviewed")
        y = paragraph(ax, y, (
            "Main/CB_50+.ipynb; Main/CB_50-64.ipynb; Main/CB_65+.ipynb; README.md; "
            "ENVIRONMENT.md; requirements.txt; relevant cross-cohort plotting scripts and saved SHAP artifacts."
        ), size=8.8)
        footer(ax, 9); pdf.savefig(fig); plt.close(fig)

        metadata = pdf.infodict()
        metadata["Title"] = "CB Notebook Journal-Code Audit Report"
        metadata["Author"] = "Codex"
        metadata["Subject"] = "Cross-cohort consistency, preprocessing, weighting, validation, and inference audit"
        metadata["Keywords"] = "KNHANES, tooth loss, notebook audit, journal submission, reproducibility"

    print(OUTPUT)


if __name__ == "__main__":
    build_report()
