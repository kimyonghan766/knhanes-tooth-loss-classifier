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
| Inferential complete-case n | *pending rerun* | *pending rerun* |
| Tooth-loss prevalence (complete-case) | *pending rerun* | *pending rerun* |

The two numbers above described §11.3's complete-case sample specifically; §11 and §9.12 each have their own (different) complete-case n depending on which covariates' missingness applies. §11.3 has been retired (see [Inferential Analysis](#inferential-analysis)) — re-run both notebooks and fill in §11's and §9.12's printed `Complete-case n` / prevalence here.

The < 20 threshold follows clinical literature establishing functional impairment in chewing and digestion. The ML sample uses mode/median imputation (see Pipeline); the inferential sample is complete-case only — see the caveat under [Inferential Analysis](#inferential-analysis).

---

## Features

Candidate variables are drawn from KNHANES and one-hot encoded where nominal. Two survey-weighted regressions are reported (see [Inferential Analysis](#inferential-analysis)): **§11**, a fixed, full-candidate model (nearly everything below except a short ML-only list), and **§9.12**, a data-driven model that refits whichever top-15 variables SHAP ranks highest per cohort — that set isn't fixed in advance, so it can't be marked in a static table; check each notebook's own §9.12 output for the current list. The column below reflects §11 only. (The previously reported pre-specified model, §11.3, used a smaller theory-driven 18-variable subset of these; it has been retired in favor of the SHAP-informed model.)

### Core Exposures

| Column | Type | Description | In §11 (full model) |
|--------|------|-------------|:---:|
| `eGFR` | Derived (continuous) | Estimated GFR via CKD-EPI 2021 equation (from `HE_crea` + age + sex) | ✓ |
| `diabetes` | Binary | `DE1_dg == 1` OR `HE_HbA1c ≥ 6.5%` — combined criterion | ✓ |
| `hypertension` | Binary | `HE_sbp ≥ 140` OR `HE_dbp ≥ 90` | ML only — §11 uses `HE_sbp`/`HE_dbp` directly instead |
| `ho_incm` | Ordinal (1–4) | Household income quartile | ✓ |
| `edu` | Ordinal (1–4) | Education level (1 = ≤ elementary, 4 = ≥ college) | ✓ |

### SES / Demographics

| Column | Description | In §11 (full model) |
|--------|-------------|:---:|
| `occp` | Occupation (7 categories; reference = Managers/Professionals) | ✓ |
| `sex` | Biological sex | ✓ (as `sex_female`) |
| `age` | Chronological age (top-coded at 80) | ✓ (restricted cubic spline in §11; linear in §9.12) |
| `town_t` | Urban (1) vs. rural (0) residence | ✓ |
| `region` | 17 regional provinces | ✓ (16 dummies, reference = code 1) |
| `marri_1` | Marital status (basic) | ML only — exact function of `marri_2`, dropped to avoid a zero-variance column |
| `marri_2` | Marital status (detailed) | ✓ (5 dummies, reference = married/cohabiting) |
| `genertn` | Household generation composition | ✓ (6 dummies) |
| `fam_rela` | Relationship to household head | ✓ (7 dummies) |
| `house` | Home ownership | ML only |
| `cfam` | Household size | ML only |
| `live_t` | Dwelling type | ML only |
| `tins` | Health insurance category | ML only |

### Lifestyle

| Column | Description | In §11 (full model) |
|--------|-------------|:---:|
| `sm_presnt` | Current smoker (1 = yes) | ✓ |
| `BD1` | Lifetime alcohol experience (1 = yes, 0 = no) | ✓ |
| `pa_aerobic` | Meets aerobic physical activity guidelines | ✓ |
| `BP1` | Perceived stress (reversed: higher = more stressed) | ✓ |
| `brush_freq` | Brushing occasions yesterday (sum of `BM1_1`–`BM1_8`, 0–8) | ML only — temporality (recorded for "yesterday", after the outcome accumulated) |

### Clinical / Lab

| Column | Description | In §11 (full model) |
|--------|-------------|:---:|
| `HE_HbA1c` | HbA1c (%) | ML only (feeds `diabetes`) |
| `HE_BMI` | BMI (kg/m²) | ✓ |
| `HE_sbp` / `HE_dbp` | Systolic / diastolic blood pressure | ✓ (used directly, not via a derived `hypertension` flag) |
| `HE_Uacid` | Serum uric acid (mg/dL) | ✓ |
| `HE_Upro` | Urinary protein (proteinuria grade) | ✓ |
| `HE_Ucrea` | Urinary creatinine | ✓ |
| `HE_TG` | Triglycerides (mg/dL) | ✓ |
| `HE_chol` / `HE_HDL_st2` | Total / HDL cholesterol | ✓ |

### Dietary

`N_CA` (calcium), `N_NA` (sodium), `N_PROT` (protein), `N_TDF` (fiber), `LS_VEG1` (vegetable intake), `LS_FRUIT` (fruit intake), `N_SUGAR` (sugar) are all ✓ in §11. `L_BR_FQ` (meal frequency) is ML only.

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
6. §11 only: `age` entered as a restricted cubic spline (knots vary by cohort). §9.12 (SHAP-informed model) deliberately leaves `age` linear instead, to match the ML arm's feature representation.

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

Two survey-weighted logistic regressions (`svyglm`, Taylor linearization) are reported per cohort, on the complete-case subset:

- **§11 — Full exploratory model.** Nearly every candidate KNHANES predictor (~32 terms after dummy-encoding; see [Features](#features) for the exact list). Holm (FWER) + Benjamini-Hochberg (FDR) corrected across all terms, since this is a broad, un-restricted search and several nominally-significant rows are expected by chance alone.
- **§9.12 — SHAP-informed confirmatory model.** Bridges the ML and inferential arms: refits the top-15 predictors by mean(|SHAP|) from the tuned best model (`TOP_N_SHAP` in the notebook) as a design-weighted regression, giving aOR + 95% CI for exactly the variables the ML model relied on most. Also Holm/BH corrected — its covariates are SHAP-*selected* rather than fixed in advance, so its p-values are post-selection and the notebook itself labels this table exploratory, not confirmatory in the pre-registered sense.

The previously reported **pre-specified model (§11.3)** — an 18-covariate, theory-driven set fixed independently of SHAP, used specifically so agreement with the SHAP arm counted as genuine triangulation rather than circular self-confirmation — has been retired. The SHAP-informed model above is now the sole data-driven arm; its own VIF check (§9.13) and analytic-sample-composition / dietary-sensitivity refit (§9.14) replace the diagnostics §11.3 used to carry.

> **Numbers below need a fresh notebook run.** Removing §11.3 and raising `TOP_N_SHAP` from 10 to 15 changed both models' printed output, so the aOR/CI/p-value tables previously reproduced here (which described §11.3's now-retired 18-variable fit) have been removed rather than left stale. Re-run §9.9 → §9.14 and §11 in both notebooks, then paste the printed `or_table` (§11) / `or_table_shap` (§9.12) outputs back into this section.

**Directionally consistent across prior runs of this pipeline** (magnitudes will shift now that §11.3 is retired, and need reconfirming from a fresh run): smoking and diabetes as risk factors; education, income, urban residence, dietary fiber, and female sex as protective; eGFR has never been an independent predictor after full adjustment (p ≈ 0.9 in both cohorts) despite being the project's primary CKD exposure of interest.

**Limitation — complete-case selection bias:** the complete-case restriction is **outcome-related** in prior runs (retained vs. excluded rows differed on the target, driven mainly by uneven dietary-recall coverage across survey waves). This is now checked in each notebook's §9.14 (part 2, SMD of included vs. excluded rows) for the SHAP-informed model specifically; re-run to get current figures.

Full side-by-side SHAP-informed-model coefficients across cohorts, once regenerated: `diagrams/forest_plot/cross_cohort_forest_plot.png` (union of both cohorts' top-15 SHAP-selected variables — see [Cross-Cohort Diagrams](#cross-cohort-diagrams)).

---

## Cross-Cohort Diagrams

`diagrams/` holds standalone scripts that recombine saved outputs from **both** notebooks into side-by-side comparison figures (they refit only the already-tuned best model per cohort, or parse already-printed notebook output — no re-tuning).

| Folder | Script | Output | Shows |
|---|---|---|---|
| `forest_plot/` | `build_cross_cohort_forest_plot.py` | `cross_cohort_forest_plot.{pdf,png,tiff}` | SHAP-informed-model aORs, 50+ vs 65+, union of both cohorts' top-15 SHAP-selected variables, dodged on shared rows (cohort-only rows show one marker) |
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
