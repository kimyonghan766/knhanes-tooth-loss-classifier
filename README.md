# Tooth Loss Classification and Survey-Weighted Regression in KNHANES 2020–2024

This repository contains the reproducible analysis for a three-cohort study of functional tooth loss among Korean adults using the 2020–2024 Korea National Health and Nutrition Examination Survey (KNHANES).

The current, manuscript-authoritative notebooks are:

| Cohort | Notebook | Role |
|---|---|---|
| Adults aged ≥50 years | [`Main/CB_50+.ipynb`](Main/CB_50+.ipynb) | Overall cohort |
| Adults aged 50–64 years | [`Main/CB_50-64.ipynb`](Main/CB_50-64.ipynb) | Middle-aged subgroup |
| Adults aged ≥65 years | [`Main/CB_65+.ipynb`](Main/CB_65+.ipynb) | Older-adult subgroup |

Files beginning with `OG_` are archived earlier versions and are not sources for manuscript results. The executed outputs in the three `CB_` notebooks are the source of truth for tables, metrics, and figures.

## Study design

The analysis has two complementary components:

- Predictive analysis: five machine-learning algorithms classify prevalent functional tooth loss in a temporally held-out survey wave.
- Explanatory analysis: exploratory survey-weighted multivariable logistic regression estimates adjusted associations with functional tooth loss.

This is a cross-sectional classification study. Model predictions should not be described as forecasts of future incident tooth loss, and adjusted associations should not be interpreted as causal effects.

### Cohorts and analytic samples

| Cohort | Full 2020–2024 ML sample | Development, 2020–2023 | Held-out test, 2024 | Full-regression complete cases |
|---|---:|---:|---:|---:|
| ≥50 years | 14,871 | 11,536 | 3,335 | 11,695 |
| 50–64 years | 7,167 | 5,590 | 1,577 | 5,905 |
| ≥65 years | 7,704 | 5,946 | 1,758 | 5,790 |

The ≥50 cohort contains both age subgroups. The 50–64 and ≥65 cohorts are mutually exclusive, but comparisons involving the ≥50 cohort are not independent.

### Outcome

The binary outcome is derived from natural tooth count:

```text
O_TC_ = 1 when O_TC < 20 natural teeth
O_TC_ = 0 when O_TC ≥ 20 natural teeth
```

Observations without a usable outcome are not included in the analytic cohort.

## Data

The notebooks expect the five KNHANES files below in `csv/`:

```text
csv/HN20_all.csv
csv/HN21_all.csv
csv/HN22_all.csv
csv/HN23_all.csv
csv/HN24_all.csv
```

KNHANES source data must be obtained through the official data-access process. Raw survey files are not redistributed by this repository. Variable definitions and English labels used by the analysis are documented in [`codebook.md`](codebook.md) and resolved for plots by [`Main/codebook_labels.py`](Main/codebook_labels.py).

## Predictor specification and preprocessing

The three notebooks use the same candidate-variable policy and modeling sequence. Cohort-specific preprocessing is learned only from the relevant development data.

The implemented workflow is:

1. Combine the 2020–2024 survey files and apply the cohort age restriction.
2. Replace KNHANES invalid, nonresponse, and sentinel codes with missing values.
3. Derive eGFR using the 2021 CKD-EPI creatinine equation, diabetes from diagnosis or HbA1c ≥6.5%, and tooth-brushing frequency from the brushing-time indicators.
4. Screen candidate predictors for more than 15% apparent missingness in the 2020–2023 development data only.
5. Remove redundant representations before fitting.
6. Apply a fixed cross-cohort categorical schema and explicit reference levels.
7. Fit imputation and any scaling within each cross-validation training fold.
8. Refit the selected specification on all 2020–2023 data and evaluate once on 2024.

The five variables excluded by the development-data availability rule are `DI4_dg`, `DE1_4`, `BS3_1`, `BD2_1`, and `LW_ms`. Some apparent missingness reflects questionnaire eligibility or skip patterns rather than ordinary item nonresponse. The four redundant variables excluded are `HE_obe`, `HE_wc`, `HE_glu`, and `N_EN`.

The final machine-learning matrix represents 43 predictor concepts as 88 columns after categorical expansion. Categorical, ordinal, and binary variables are imputed with their training-fold mode; continuous variables are imputed with their training-fold median. Multi-category nominal missingness is retained as an explicit unknown level where specified. Logistic-regression scaling is applied to continuous and ordinal columns only; binary indicator columns are not standardized.

## Predictive modeling

The evaluated algorithms are:

- random forest;
- XGBoost;
- LightGBM;
- CatBoost; and
- elastic-net logistic regression.

### Nested cross-validation and tuning

Model development uses honest nested cross-validation within the 2020–2023 development sample:

- five stratified outer folds estimate out-of-fold performance;
- each outer training portion uses five-fold inner cross-validation;
- Optuna runs 50 trials per model in each inner search;
- unweighted average precision (AUPRC) is the selection score; and
- a separate 50-trial, five-fold search on the complete development set selects hyperparameters for the final 2024 refit.

This is intentionally computationally intensive. Reducing the number of inner folds or Optuna trials can shorten exploratory runs, but manuscript results should be generated with the settings recorded in the notebooks.

Class-imbalance handling is fixed rather than tuned. Random forest, LightGBM, and logistic regression use balanced class weighting; CatBoost uses automatic balanced class weights. XGBoost's `scale_pos_weight` is calculated from the outcome counts in the applicable training fold and from the full development set for the final refit. It is not an Optuna hyperparameter.

### Held-out evaluation and weighting

The notebooks distinguish model-development quantities from population-oriented test estimates:

| Analysis | Data | Survey weighting |
|---|---|---|
| Nested-CV model selection | 2020–2023 development data | Unweighted |
| Final discrimination and Brier score | 2024 held-out test data | Weighted by `wt_itvex` |
| Metric confidence intervals | 2024 held-out test data | PSU-within-stratum survey bootstrap, 2,000 replicates |
| Pairwise DeLong AUROC comparison | 2024 held-out test data | Unweighted; secondary analysis |
| MCC threshold and confusion matrix | 2024 held-out test data | Unweighted |
| Decision-curve analysis | 2024 held-out test data | Unweighted |

The notebooks report AUROC, AUPRC, Brier score, calibration, threshold-dependent classification measures, subgroup performance, learning curves, and decision curves. The MCC operating threshold is defined on the raw model score; Platt-recalibrated probabilities are used for the calibration and decision-curve sections as labeled in each notebook.

### Calibration and explainability

Platt calibration is fitted to nested out-of-fold development predictions and then applied to held-out 2024 predictions. Weighted Brier score, expected calibration error, and calibration curves are calculated for the test population.

SHAP summaries use the CatBoost model as a common algorithm across all three cohorts. These are three separately fitted cohort models, not one shared fitted model. Global importance is the unweighted mean absolute SHAP value in the 2024 test sample. SHAP is descriptive and does not establish an independent or causal association.

CatBoost is retained as the common algorithm for cross-cohort explainability even when another algorithm has the highest nested out-of-fold AUPRC in a particular cohort. This choice should not be described as test-set model selection.

## Survey-weighted descriptive and regression analyses

Descriptive estimates use the full eligible 2020–2024 cohort and the KNHANES complex survey design.

The multivariable analysis is one full exploratory survey-weighted logistic-regression model in each cohort. It includes the current 43 predictor concepts, including dental variables. It is not the deleted SHAP-informed confirmatory model. Age is entered linearly; no age spline is used in the current regression.

Implementation details:

- complete-case analysis for the regression specification;
- Taylor-series variance estimation with R's `survey::svyglm`;
- five-year pooled examination weights, `wt_itvex / 5`;
- survey-year-specific stratum and PSU identifiers to prevent identifier collisions across waves;
- explicit categorical reference levels;
- calcium scaled per 100 mg and sodium per 1,000 mg for reporting;
- no imputation or synthetic oversampling in the regression; and
- nominal, unadjusted P values.

The regression analyses are exploratory. P values are nominal and are not adjusted for multiple comparisons; consequently, P<0.05 is not interpreted as confirmatory evidence.

Categorical expansion produces more coefficient rows than the 43 underlying predictor concepts. Forest-plot sample sizes and adjusted odds ratios must match the full regression output in the corresponding executed notebook.

## Cross-cohort figures

Current manuscript figure builders and rendered PNGs are under `diagrams/3_cohorts/`:

| Figure | Builder | Interpretation |
|---|---|---|
| Regression forest plot | [`build_cross_cohort_forest_plot.py`](diagrams/3_cohorts/forest_plot/build_cross_cohort_forest_plot.py) | Current full exploratory survey-weighted regression, not the deleted SHAP-informed model |
| SHAP summary | [`build_cross_cohort_shap_summary_overlay.py`](diagrams/3_cohorts/shap_summary/build_cross_cohort_shap_summary_overlay.py) | Cohort-specific CatBoost SHAP distributions |
| ROC and precision–recall overlay | [`build_roc_pr_overlay.py`](diagrams/3_cohorts/roc_pr_overlay/build_roc_pr_overlay.py) | Held-out 2024 discrimination across the three cohorts |
| Calibration and decision-curve overlay | [`build_calibration_dca_overlay.py`](diagrams/3_cohorts/calibration_dca_overlay/build_calibration_dca_overlay.py) | Recalibrated held-out probabilities and clinical net benefit |

The corresponding rendered files are:

```text
diagrams/3_cohorts/forest_plot/cross_cohort_forest_plot_annotated.png
diagrams/3_cohorts/shap_summary/cross_cohort_shap_summary_overlay.png
diagrams/3_cohorts/roc_pr_overlay/roc_pr_overlay.png
diagrams/3_cohorts/calibration_dca_overlay/calibration_dca_overlay.png
```

Regenerate figures after any notebook rerun that changes sample sizes, model predictions, SHAP values, or regression coefficients.

## Environment and execution

The exact analysis environment is documented in [`ENVIRONMENT.md`](ENVIRONMENT.md), and the pinned Python dependencies are listed in [`requirements.txt`](requirements.txt). The regression sections additionally require R, `rpy2`, and the R `survey` package; a Python-only installation cannot reproduce the complete analysis.

The notebooks use paths relative to `Main/`. Start Jupyter from that directory:

```bash
cd Main
jupyter lab
```

Then restart the kernel and run all cells in this order:

1. `CB_50+.ipynb`
2. `CB_50-64.ipynb`
3. `CB_65+.ipynb`

The notebooks are analytically independent, so the order does not affect their results. The suggested order only makes cross-cohort checking easier. Do not run only selected downstream cells after changing preprocessing, the cohort definition, or model settings.

Before transferring results to a manuscript, verify all of the following from the newly executed notebooks:

- cohort, development, test, and regression sample sizes;
- tooth-loss prevalence and survey-weighted descriptive statistics;
- nested out-of-fold model-selection results;
- weighted 2024 metrics and confidence intervals;
- calibration and decision-curve values;
- SHAP variable labels and ranks;
- regression adjusted odds ratios, confidence intervals, and P values; and
- all figure annotations and legends.

Avoid manually preserving numeric results in this README. The executed notebook outputs should remain the single source of truth whenever the pipeline is rerun.

## Repository structure

```text
.
├── Main/
│   ├── CB_50+.ipynb
│   ├── CB_50-64.ipynb
│   ├── CB_65+.ipynb
│   ├── OG_*.ipynb                 # archived; not manuscript-authoritative
│   ├── codebook_labels.py
│   └── shap_importance_*_catboost.npz
├── csv/
│   └── HN20_all.csv ... HN24_all.csv
├── diagrams/
│   └── 3_cohorts/
├── webapp/
├── codebook.md
├── ENVIRONMENT.md
├── requirements.txt
└── README.md
```

## Ancillary web application

`webapp/` is an ancillary demonstration and is not an authoritative source for manuscript estimates. Its bundled artifacts currently cover the ≥50 and ≥65 cohorts only. They should not be used to reproduce three-cohort manuscript results unless the application models are explicitly re-exported and validated against the current notebooks.

## Reproducibility boundary

Reproduction requires the original KNHANES files, the recorded Python and R environments, and a complete run of all three `CB_` notebooks. Random seeds are fixed where supported, but small differences can still occur across operating systems or library builds for multithreaded learners. Any rerun used for submission should archive the executed notebooks and regenerated figures together.
