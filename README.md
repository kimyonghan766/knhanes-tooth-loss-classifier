# Tooth Loss Risk Analysis — KNHANES 2020–2024

Binary classification and inferential analysis of severe tooth loss (< 20 teeth) in Korean adults, using pooled data from five waves of the **Korea National Health and Nutrition Examination Survey (KNHANES 2020–2024)**. The analysis runs on two cohorts — adults **≥ 50** (primary) and **≥ 65** (sensitivity subgroup) — to check whether findings hold in the higher-prevalence older-adult population.

---

## Research Question

> Do CKD (eGFR), diabetes, and socioeconomic status independently affect tooth loss after controlling for age, sex, and other covariates?

This project answers two related but distinct questions:
- **Predictive:** Which features best classify tooth loss? (ML models)
- **Explanatory:** Are the exposures of interest statistically independent risk factors? (survey-weighted logistic regression with adjusted ORs)

---

## Cohort Design

| Notebook | Cohort | Role |
|---|---|---|
| `Main/final.ipynb` | Age ≥ 50 | Primary analysis |
| `Main/final(65+).ipynb` | Age ≥ 65 | Sensitivity analysis — identical pipeline re-run on the older-adult subgroup |

Both notebooks share the same preprocessing, feature engineering, model set, tuning procedure, and inferential model specification — only the age filter differs. The `diagrams/` scripts (below) recombine outputs from both notebooks into side-by-side comparison figures.

---

## Dataset

| Item | 50+ cohort | 65+ cohort |
|------|-----------|-----------|
| Source | KNHANES 2020–2024 (`HN20_all.csv` – `HN24_all.csv`) | same |
| Target | `O_TC_` — `1` if tooth count < 20, `0` if ≥ 20 | same |
| ML sample (train + test) | 14,871 (11,536 train / 3,335 test) | 7,704 (5,946 train / 1,758 test) |
| Inferential complete-case n | 11,781 | 5,832 |
| Tooth-loss prevalence (complete-case) | 25.0% | 40.1% |

The < 20 threshold follows clinical literature establishing functional impairment in chewing and digestion. The ML sample uses mode/median imputation (see Pipeline); the inferential sample is complete-case only — see the caveat under [Inferential Analysis](#inferential-analysis).

---

## Features

Candidate variables are drawn from KNHANES and one-hot encoded where nominal. The **pre-specified inferential model** (§11.3 in each notebook) uses a smaller, theory-driven subset of these — marked with `*` below.

### Core Exposures

| Column | Type | Description | In inferential model |
|--------|------|-------------|:---:|
| `eGFR` | Derived (continuous) | Estimated GFR via CKD-EPI 2021 equation (from `HE_crea` + age + sex) | ✓ |
| `diabetes` | Binary | `DE1_dg == 1` OR `HE_HbA1c ≥ 6.5%` — combined criterion | ✓ |
| `hypertension` | Binary | `HE_sbp ≥ 140` OR `HE_dbp ≥ 90` | ✓ |
| `ho_incm` | Ordinal (1–4) | Household income quartile | ✓ |
| `edu` | Ordinal (1–4) | Education level (1 = ≤ elementary, 4 = ≥ college) | ✓ |

### SES / Demographics

| Column | Description | In inferential model |
|--------|-------------|:---:|
| `occp` | Occupation (7 categories; reference = Managers/Professionals) | ✓ |
| `sex` | Biological sex | ✓ (as `sex_female`) |
| `age` | Chronological age (top-coded at 80) | ✓ (restricted cubic spline) |
| `town_t` | Urban (1) vs. rural (0) residence | ✓ |
| `region` | 17 regional provinces | ML only — no valid linear encoding for regression |
| `marri_1` / `marri_2` | Marital status (basic / detailed) | ML only |
| `genertn` | Household generation composition | ML only |
| `fam_rela` | Relationship to household head | ML only |
| `house` | Home ownership | ML only |
| `cfam` | Household size | ML only |
| `live_t` | Dwelling type | ML only |
| `tins` | Health insurance category | ML only |

### Lifestyle

| Column | Description | In inferential model |
|--------|-------------|:---:|
| `sm_presnt` | Current smoker (1 = yes) | ✓ |
| `BD1` | Lifetime alcohol experience (1 = yes, 0 = no) | ✓ |
| `pa_aerobic` | Meets aerobic physical activity guidelines | ✓ |
| `BP1` | Perceived stress (reversed: higher = more stressed) | ✓ |
| `brush_freq` | Brushing occasions yesterday (sum of `BM1_1`–`BM1_8`, 0–8) | ML only |

### Clinical / Lab

| Column | Description | In inferential model |
|--------|-------------|:---:|
| `HE_HbA1c` | HbA1c (%) | ML only (feeds `diabetes`) |
| `HE_BMI` | BMI (kg/m²) | ✓ |
| `HE_sbp` / `HE_dbp` | Systolic / diastolic blood pressure | ML only (feeds `hypertension`) |
| `HE_Uacid` | Serum uric acid (mg/dL) | ✓ |
| `HE_Upro` | Urinary protein (proteinuria grade) | ML only |
| `HE_Ucrea` | Urinary creatinine | ML only |
| `HE_TG` | Triglycerides (mg/dL) | ✓ |
| `HE_chol` / `HE_HDL_st2` | Total / HDL cholesterol | ML only |

### Dietary

`N_CA` (calcium, ✓ inferential), `N_NA` (sodium), `N_PROT` (protein), `N_TDF` (fiber, ✓ inferential), `LS_VEG1` (vegetable intake), `LS_FRUIT` (fruit intake), `N_SUGAR` (sugar), `L_BR_FQ` (meal frequency) — remainder ML only.

### Dental

`O_pain` (oral pain), `MO4_00` (dental visit), `OR1` (dental visit reason), `BM1_0`–`BM1_8` (brushing occasion flags → `brush_freq`) — all ML only, excluded from the inferential model on temporality grounds (plausible consequences of tooth loss rather than antecedents).

`HE_crea` and `sex` (raw) are consumed by the eGFR derivation / `sex_female` dummy and dropped from the raw feature matrix. `BS12_1` (secondhand smoke exposure) is a candidate variable, ML only.

---

## Pipeline

### Preprocessing
1. Age filter: ≥ 50 (or ≥ 65 for the sensitivity notebook)
2. Invalid-code replacement — survey codes (8, 9, 88, 99, etc.) and sentinel floats (`-1.80E+308`) → `NaN`
3. eGFR derivation using CKD-EPI 2021 creatinine equation
4. Derived features: `diabetes` (combined criterion), `hypertension`, `brush_freq`
5. `BD1` recode (KNHANES 1/2 → 1/0); `BP1` reversal (higher = more stressed)
6. Inferential model only: `age` entered as a restricted cubic spline (knots vary by cohort — see notebook §11.3)

### Train / Test Split (Temporal)

| Set | Source files | Years |
|-----|-------------|-------|
| **Train** | HN20, HN21, HN22, HN23 | 2020–2023 |
| **Test** | HN24 | 2024 |

The imputer is rebuilt inside every CV fold during tuning, and fitted on the training fold only for the final refit — never on the test set, preventing data leakage. `year` is used solely as a split key.

### Class Imbalance
No SMOTE. XGBoost tunes `scale_pos_weight` via Optuna; all other models use `class_weight="balanced"` (`auto_class_weights="Balanced"` for CatBoost).

---

## Predictive Models

### Hyperparameter Tuning (Optuna TPE)
50-trial Optuna TPE study per model, 5-fold `StratifiedKFold` (seed 42), scored by `average_precision` (AUPRC). `StandardScaler` is applied inside the Logistic Regression pipeline only — tree-based models are scale-invariant.

| Model | Key Hyperparameters Tuned |
|-------|--------------------------|
| **XGBoost** | `n_estimators`, `max_depth`, `learning_rate`, `subsample`, `colsample_bytree`, `min_child_weight`, `gamma`, `reg_lambda` |
| **LightGBM** | `n_estimators`, `num_leaves`, `learning_rate`, `min_child_samples`, `reg_lambda` |
| **CatBoost** | `iterations`, `depth`, `learning_rate`, `l2_leaf_reg` |
| **Random Forest** | `n_estimators`, `max_depth`, `min_samples_leaf` |
| **Logistic Regression** | `C`, `l1_ratio` (ElasticNet, SAGA solver) |

The best model is selected by **OOF AUPRC** on the 2020–2023 development sample (unweighted) — not by test-set performance, so the selected model need not top every test-set column.

### Test-Set Performance (bootstrap 95% CI, 2000 stratified resamples, seed 42)

**50+ cohort** (n_test = 3,335) — selected: **CatBoost** (OOF AUPRC 0.6500)

| Model | AUC | AUPRC | Brier |
|-------|-----|-------|-------|
| **CatBoost** | **0.834 (0.817–0.850)** | **0.650 (0.634–0.666)** | **0.152 (0.145–0.159)** |
| XGBoost | 0.835 (0.818–0.852) | 0.649 (0.634–0.666) | 0.151 (0.144–0.158) |
| LightGBM | 0.834 (0.817–0.850) | 0.648 (0.633–0.665) | 0.152 (0.145–0.159) |
| Logistic Regression | 0.832 (0.815–0.849) | 0.648 (0.633–0.665) | 0.154 (0.147–0.161) |
| Random Forest | 0.824 (0.807–0.841) | 0.631 (0.615–0.648) | 0.138 (0.132–0.143) |

**65+ cohort** (n_test = 1,758) — selected: **Logistic Regression** (OOF AUPRC 0.6935)

| Model | AUC | AUPRC | Brier |
|-------|-----|-------|-------|
| **Logistic Regression** | **0.752 (0.727–0.775)** | **0.694 (0.678–0.710)** | **0.197 (0.189–0.206)** |
| CatBoost | 0.755 (0.730–0.779) | 0.693 (0.677–0.708) | 0.196 (0.188–0.205) |
| XGBoost | 0.759 (0.735–0.782) | 0.692 (0.677–0.708) | 0.195 (0.187–0.204) |
| LightGBM | 0.748 (0.724–0.773) | 0.685 (0.670–0.701) | 0.199 (0.190–0.207) |
| Random Forest | 0.747 (0.722–0.771) | 0.679 (0.663–0.696) | 0.202 (0.195–0.208) |

Note the simpler Logistic Regression wins the 65+ cohort's model-selection metric — the tree ensembles' edge over linear models narrows in the smaller, higher-prevalence subgroup.

### Additional Evaluation
- Sex-stratified AUROC/AUPRC (both cohorts show a consistent female > male discrimination gap)
- DeLong pairwise significance test between model AUCs
- Learning curves for the top 3 models (overfitting check)
- Post-hoc Platt (logistic) recalibration
- Decision curve analysis — clinical utility on recalibrated probabilities
- Sensitivity analyses: reverse-causation predictors removed; leave-region-out
- SHAP values: beeswarm, waterfall, dependence plots, mean |SHAP| bar chart (computed on the selected best model)

---

## Inferential Analysis

Survey-weighted multivariable logistic regression (`svyglm`, Taylor linearization) on the complete-case subset, pre-specified independently of the SHAP results (theory-driven covariate list, no circularity with the ML arm).

**Adjusted Odds Ratios (aOR) — 50+ cohort, n = 11,781, prevalence = 25.0%:**

| Variable | aOR | 95% CI | p-value |
|----------|-----|--------|---------|
| Current smoker | 1.99 | [1.67, 2.38] | **< 0.001** |
| Diabetes (combined criterion) | 1.40 | [1.24, 1.59] | **< 0.001** |
| Occupation: Craft/Trade (`occp_4`) | 1.50 | [1.06, 2.13] | **0.023** |
| Occupation: Machine op. (`occp_5`) | 1.38 | [0.99, 1.92] | 0.054 |
| Occupation: Elementary (`occp_6`) | 1.33 | [0.95, 1.85] | 0.098 |
| Triglycerides | 1.0009 | [1.0003, 1.0015] | **0.006** |
| Female sex | 0.75 | [0.65, 0.86] | **< 0.001** |
| Education level | 0.78 | [0.74, 0.83] | **< 0.001** |
| Urban residence | 0.76 | [0.67, 0.87] | **< 0.001** |
| Income quartile | 0.88 | [0.83, 0.93] | **< 0.001** |
| Dietary fiber (`N_TDF`) | 0.989 | [0.984, 0.994] | **< 0.001** |
| eGFR | 1.0002 | [0.9956, 1.0047] | 0.942 |
| Hypertension | 0.94 | [0.82, 1.09] | 0.417 |
| Alcohol experience | 0.89 | [0.76, 1.03] | 0.123 |
| Physical activity (aerobic) | 0.93 | [0.82, 1.06] | 0.291 |
| Uric acid | 1.005 | [0.956, 1.056] | 0.851 |
| Calcium intake | 0.9999 | [0.9997, 1.0001] | 0.469 |
| Perceived stress | 0.994 | [0.922, 1.073] | 0.887 |

Age is entered as a restricted cubic spline (4 knots); a design-based Wald test found no evidence against linearity (p = 0.43).

**Key findings:**
- Smoking is the strongest modifiable risk factor (aOR ≈ 1.99, p < 0.001)
- Diabetes remains an independent risk factor after adjustment (aOR ≈ 1.40, p < 0.001)
- Education, income, urban residence, and dietary fiber are protective; female sex is protective
- eGFR is **not** an independent predictor after adjustment (p = 0.94)
- Craft/trade occupation carries elevated risk vs. the managerial/professional reference

**65+ cohort (sensitivity), n = 5,832, prevalence = 40.1%:** the same direction and approximate magnitude holds for the two dominant effects — smoking (aOR 1.84, p < 0.001) and diabetes (aOR 1.35, p < 0.001) — while eGFR remains non-significant (p = 0.90). Full side-by-side coefficients: `diagrams/forest_plot/cross_cohort_forest_plot.png`.

**VIF check (50+ cohort):** all 23 terms < 5 (max 4.34, `occp_7`) — no problematic multicollinearity despite eGFR–age correlation (r ≈ −0.51).

**Limitation — complete-case selection bias:** the complete-case restriction is **outcome-related** (retained vs. excluded rows differ on the target by SMD = −0.30, driven mainly by uneven dietary-recall coverage across survey waves). This is flagged explicitly in each notebook's §11.3.3 sensitivity check; the aORs above should be read with that caveat rather than as unconditionally population-representative.

---

## Cross-Cohort Diagrams

`diagrams/` holds standalone scripts that recombine saved outputs from **both** notebooks into side-by-side comparison figures (they refit only the already-tuned best model per cohort, or parse already-printed notebook output — no re-tuning).

| Folder | Script | Output | Shows |
|---|---|---|---|
| `forest_plot/` | `build_cross_cohort_forest_plot.py` | `cross_cohort_forest_plot.{pdf,png,tiff}` | Pre-specified aORs, 50+ vs 65+, dodged on shared rows |
| `shap_summary/` | `build_cross_cohort_shap_summary_overlay.py` | `cross_cohort_shap_summary_overlay.{pdf,png}` | SHAP beeswarm, best model per cohort, side by side |
| `cross_cohort_overlay/` | `build_cross_cohort_overlay.py` | `cross_cohort_overlay.{pdf,png}` | ROC + PR + calibration curves, both cohorts overlaid |
| `cross_cohort_split/` | `build_cross_cohort_split_3d.py` | `cross_cohort_split_3d.png` | Temporal train/test row counts, both cohorts |
| `combined_shap_plot/` | `combined_shap_plot.py` | `combined_shap_importance.png` | Mean \|SHAP\| bar chart, both cohorts (reads `Main/shap_importance_{50,65}plus.npz`, saved by a notebook cell first) |

---

## Web App

`webapp/` is a single-page Streamlit screening tool wrapping the tuned XGBoost model (`export_model.py` reproduces the notebook preprocessing and refits with tuned params → `model.pkl` + `meta.json`; `app.py` serves the form + prediction + SHAP). See `webapp/README.md` for run instructions.

> Its bundled `meta.json` (test AUC 0.8025) predates the current best-model selection above (CatBoost, 50+ cohort) — rerun `export_model.py` if the app needs to reflect the latest tuned model.

---

## Codebook

`codebook.md` is a translated/structured reference from the KNHANES 9th-cycle (2022–2024) documentation (변수설명서). `Main/codebook_labels.py` parses it live to relabel SHAP plot axes with plain-English variable names.

---

## Requirements

Full pinned dependency set: [`requirements.txt`](requirements.txt) (154 packages). Both notebooks also call into R (`survey` package) via `rpy2` for the survey-weighted regression — a Python-only environment is **not** sufficient. See [`ENVIRONMENT.md`](ENVIRONMENT.md) for exact versions and setup steps.

---

## File Structure

```
├── Main/
│   ├── final.ipynb                  # primary analysis — age ≥ 50 cohort
│   ├── final(65+).ipynb             # sensitivity analysis — age ≥ 65 subgroup
│   ├── codebook_labels.py           # KNHANES code → plain-English label resolver
│   ├── shap_importance_50plus.npz   # saved mean |SHAP| values, 50+ cohort
│   └── shap_importance_65plus.npz   # saved mean |SHAP| values, 65+ cohort
├── csv/
│   ├── HN20_all.csv                 # KNHANES 2020 (not tracked)
│   ├── HN21_all.csv                 # KNHANES 2021 (not tracked)
│   ├── HN22_all.csv                 # KNHANES 2022 (not tracked)
│   ├── HN23_all.csv                 # KNHANES 2023 (not tracked)
│   └── HN24_all.csv                 # KNHANES 2024 (not tracked)
├── diagrams/
│   ├── forest_plot/
│   ├── shap_summary/
│   ├── cross_cohort_overlay/
│   ├── cross_cohort_split/
│   └── combined_shap_plot/
├── webapp/
│   ├── app.py
│   ├── export_model.py
│   ├── model.pkl / meta.json
│   ├── requirements.txt
│   └── README.md
├── codebook.md
├── ENVIRONMENT.md
├── requirements.txt
└── README.md
```
