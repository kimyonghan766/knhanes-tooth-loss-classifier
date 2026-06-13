# Tooth Loss Risk Analysis — KNHANES 2020–2024

Binary classification and inferential analysis of severe tooth loss (< 20 teeth) in Korean adults aged ≥ 50, using pooled data from five waves of the **Korea National Health and Nutrition Examination Survey (KNHANES 2020–2024)**.

---

## Research Question

> Do CKD (eGFR), diabetes, and socioeconomic status independently affect tooth loss after controlling for age, sex, and other covariates?

This project answers two related but distinct questions:
- **Predictive:** Which features best classify tooth loss? (ML models)
- **Explanatory:** Are the exposures of interest statistically independent risk factors? (survey-weighted logistic regression with adjusted ORs)

---

## Dataset

| Item | Detail |
|------|--------|
| Source | KNHANES 2020–2024 (`HN20_all.csv` – `HN24_all.csv`) |
| Population | Adults aged ≥ 50 |
| Target | `O_TC_` — `1` if tooth count < 20, `0` if ≥ 20 |
| Inferential complete-case n | 11,700 |
| Tooth-loss prevalence | 25.0% |

The < 20 threshold follows clinical literature establishing functional impairment in chewing and digestion.

---

## Features

### Core Exposures

| Column | Type | Description |
|--------|------|-------------|
| `eGFR` | Derived (continuous) | Estimated GFR via CKD-EPI 2021 equation (from `HE_crea` + age + sex) |
| `diabetes` | Binary | `DE1_dg == 1` OR `HE_HbA1c ≥ 6.5%` — combined criterion |
| `hypertension` | Binary | `HE_sbp ≥ 140` OR `HE_dbp ≥ 90` |
| `ho_incm` | Ordinal (1–4) | Household income quartile |
| `edu` | Ordinal (1–4) | Education level (1 = ≤ elementary, 4 = ≥ college) |

### SES / Demographics

| Column | Description |
|--------|-------------|
| `occp` | Occupation (7 categories; reference = Managers/Professionals) |
| `marri_1` | Marital status (1 = married, 0 = unmarried) |
| `town_t` | Urban (1) vs. rural (0) residence |
| `region` | 17 regional provinces (excluded from regression — no valid linear encoding) |

### Lifestyle

| Column | Description |
|--------|-------------|
| `sm_presnt` | Current smoker (1 = yes) |
| `BD1` | Lifetime alcohol experience (1 = yes, 0 = no) |
| `pa_aerobic` | Meets aerobic physical activity guidelines |
| `BP1` | Perceived stress (reversed: higher = more stressed) |
| `brush_freq` | Brushing occasions yesterday (sum of BM1_1–BM1_8, 0–8) |

### Clinical / Lab

| Column | Description |
|--------|-------------|
| `HE_HbA1c` | HbA1c (%) |
| `HE_BMI` | BMI (kg/m²) |
| `HE_sbp` / `HE_dbp` | Systolic / diastolic blood pressure |
| `HE_Uacid` | Serum uric acid (mg/dL) |
| `HE_Upro` | Urinary protein (proteinuria grade) |
| `HE_Ucrea` | Urinary creatinine |
| `HE_TG` | Triglycerides (mg/dL) |

### Dietary

`N_CA` (calcium), `N_NA` (sodium), `N_PROT` (protein), `N_TDF` (fiber), `LS_VEG1` (vegetable intake), `LS_FRUIT` (fruit intake), `N_SUGAR` (sugar).

### Dental

`O_pain` (oral pain), `MO4_00` (dental visit), `BM1_0`–`BM1_8` (brushing occasion flags → `brush_freq`).

`HE_crea` and `sex` are consumed by the eGFR derivation and dropped from the feature matrix.

---

## Pipeline

### Preprocessing
1. Age filter: ≥ 50
2. Invalid-code replacement — survey codes (8, 9, 88, 99, etc.) and sentinel floats (`-1.80E+308`) → `NaN`
3. eGFR derivation using CKD-EPI 2021 creatinine equation
4. Derived features: `diabetes` (combined criterion), `hypertension`, `brush_freq`
5. `BD1` recode (KNHANES 1/2 → 1/0); `BP1` reversal (higher = more stressed)

### Train / Test Split (Temporal)

| Set | Source files | Years |
|-----|-------------|-------|
| **Train** | HN20, HN21, HN22, HN23 | 2020–2023 |
| **Test** | HN24 | 2024 |

The imputer is fitted on the training fold only and applied to the test set without refitting, preventing data leakage. `year` is used solely as a split key.

### Class Imbalance
No SMOTE. XGBoost tunes `scale_pos_weight` via Optuna; all other models use `class_weight="balanced"`.

---

## Predictive Models

### Hyperparameter Tuning (Optuna TPE)
100-trial Optuna TPE study per model, 5-fold `StratifiedKFold`, scored by `roc_auc`. `StandardScaler` is applied inside the Logistic Regression pipeline only — tree-based models are scale-invariant.

| Model | Key Hyperparameters Tuned |
|-------|--------------------------|
| **XGBoost** | `n_estimators`, `max_depth`, `learning_rate`, `subsample`, `colsample_bytree`, `min_child_weight`, `gamma`, `reg_lambda`, `scale_pos_weight` |
| **LightGBM** | `n_estimators`, `num_leaves`, `learning_rate`, `min_child_samples`, `reg_lambda` |
| **CatBoost** | `iterations`, `depth`, `learning_rate`, `l2_leaf_reg` |
| **Random Forest** | `n_estimators`, `max_depth`, `min_samples_leaf` |
| **Logistic Regression** | `C`, `l1_ratio` (ElasticNet, SAGA solver) |

### Evaluation
- ROC-AUC and AUPRC on the held-out 2024 test set
- Threshold selection via Youden's J and MCC (optimised on out-of-fold probabilities)
- Calibration curves (Brier score)
- SHAP values: beeswarm, waterfall, dependence plots, mean |SHAP| bar chart

---

## Inferential Analysis

Survey-weighted multivariable logistic regression (`svyglm`, Taylor linearization) on the complete-case subset (n = 11,700, tooth-loss prevalence = 25.0%).

**Adjusted Odds Ratios (aOR) — selected variables:**

| Variable | aOR | 95% CI | p-value |
|----------|-----|--------|---------|
| Current smoker | 1.90 | [1.58, 2.28] | **< 0.001** |
| Occupation: Craft/Trade (`occp_4`) | 1.51 | [1.05, 2.15] | **0.024** |
| Occupation: Machine op. (`occp_5`) | 1.42 | [1.02, 1.98] | **0.037** |
| Diabetes (combined criterion) | 1.39 | [1.22, 1.59] | **< 0.001** |
| Occupation: Elementary (`occp_6`) | 1.33 | [0.96, 1.86] | 0.091 |
| Education level | 0.78 | [0.73, 0.83] | **< 0.001** |
| Income quartile | 0.90 | [0.84, 0.95] | **0.0004** |
| Urban residence | 0.76 | [0.66, 0.87] | **0.0001** |
| Proteinuria (`HE_Upro`) | 1.14 | [1.01, 1.29] | **0.033** |
| Triglycerides | 1.0008 | [1.0003, 1.0014] | **0.005** |
| eGFR | 1.00 | [1.00, 1.01] | 0.603 |
| Alcohol experience | 1.12 | [0.96, 1.32] | 0.142 |
| Marital status (married) | 0.77 | [0.51, 1.16] | 0.208 |

**Key findings:**
- Smoking is the strongest modifiable risk factor (aOR ≈ 1.90, p < 0.001)
- Diabetes remains an independent risk factor after adjustment (aOR ≈ 1.39, p < 0.001)
- Education and income are protective; urban residence is also protective
- eGFR is **not** an independent predictor after adjustment (p = 0.603)
- Manual/elementary occupations carry elevated risk vs. managerial/professional reference

**VIF check:** All predictors < 5 — no problematic multicollinearity despite eGFR–age correlation.

---

## Requirements

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost lightgbm catboost optuna shap statsmodels
```

Python 3.11+ recommended.

---

## File Structure

```
├── Main/
│   └── test(age).ipynb      # full analysis notebook
├── csv/
│   ├── HN20_all.csv         # KNHANES 2020 (not tracked)
│   ├── HN21_all.csv         # KNHANES 2021 (not tracked)
│   ├── HN22_all.csv         # KNHANES 2022 (not tracked)
│   ├── HN23_all.csv         # KNHANES 2023 (not tracked)
│   └── HN24_all.csv         # KNHANES 2024 (not tracked)
└── README.md
```
