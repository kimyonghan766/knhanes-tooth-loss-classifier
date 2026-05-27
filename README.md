# Tooth Loss Risk Analysis — KNHANES IX

Binary classification and inferential analysis of severe tooth loss (< 20 teeth) in Korean adults aged ≥ 40, using data from the **Korea National Health and Nutrition Examination Survey IX (KNHANES IX)**.

---

## Research Question

> Do CKD (eGFR), diabetes (HbA1c), and socioeconomic status independently affect tooth loss after controlling for age, sex, and alcohol use?

This project answers two related but distinct questions:
- **Predictive:** Which features best classify tooth loss? (ML models)
- **Explanatory:** Are the exposures of interest statistically independent risk factors? (logistic regression with adjusted ORs)

---

## Dataset

| Item | Detail |
|------|--------|
| Source | KNHANES IX (`KNHANES9.csv`) |
| Population | Adults aged ≥ 40 (n = 4,680 after age filter) |
| Valid records | 4,147 after dropping invalid `O_TC` entries |
| Target | `O_TC_` — `1` if tooth count < 20, `0` if ≥ 20 |
| Class distribution | 3,242 (≥ 20 teeth) vs 905 (< 20 teeth), ratio ≈ 3.58× |

The < 20 threshold follows clinical literature establishing functional impairment in chewing and digestion.

---

## Features

| Column | Type | Description |
|--------|------|-------------|
| `age_group` | Ordinal (0–3) | Age binned into decades: 40s / 50s / 60s / 70+ |
| `ho_incm` | Ordinal (1–4) | Household income quartile (1 = low, 4 = high) |
| `edu` | Ordinal (1–4) | Education level (1 = ≤ elementary, 4 = ≥ college) |
| `BD1` | Binary | Lifetime alcohol experience (1 = never, 2 = yes) |
| `BM7` | Ordinal (reversed) | Chewing difficulty — recoded so higher = more difficulty |
| `HE_HbA1c` | Continuous | HbA1c (%), diabetes cutoff ≥ 6.5% |
| `HE_BMI` | Continuous | BMI (kg/m²) |
| `eGFR` | Derived | Estimated GFR via CKD-EPI 2021 equation (from creatinine + age + sex) |

`HE_crea` (serum creatinine) and `sex` are consumed by the eGFR derivation and dropped from the feature matrix.

---

## Pipeline

### Preprocessing
1. Age filter: ≥ 40
2. Invalid-code replacement — survey codes (8, 9, 88, 99, etc.) and sentinel floats → `NaN`
3. eGFR derivation using CKD-EPI 2021 creatinine equation
4. `BM7` ordinal reversal (`6 − BM7`)
5. 80/20 stratified train/test split
6. Median imputation fitted on training fold only (666 values imputed)

### Class Imbalance
SMOTE applied **inside each CV fold** via `ImbPipeline` (sampling ratio 1:1.5) to prevent leakage. Not used in the inferential section — SMOTE distorts class proportions and biases odds ratios.

---

## Predictive Models

### Hyperparameter Tuning (RandomizedSearchCV)
5-fold `StratifiedKFold`, 50 iterations per model, scored by `roc_auc`.

| Model | Best CV AUC | Key Hyperparameters |
|-------|-------------|---------------------|
| **XGBoost** | **0.8269** | n_estimators=500, max_depth=3, lr=0.01 |
| LightGBM | 0.8250 | n_estimators=300, num_leaves=15, lr=0.01 |
| Logistic Regression | 0.8222 | C=0.01, penalty=L1 (SAGA solver) |
| Random Forest | 0.8212 | n_estimators=100, max_depth=5, min_samples_leaf=10 |

### PyCaret Screening (automated second opinion)
Top 3 models by cross-validated AUC from a full algorithm sweep:

1. RidgeClassifier
2. LinearDiscriminantAnalysis
3. LogisticRegression

---

## Inferential Analysis

Multivariable logistic regression on the complete-case subset (n = 3,882, tooth-loss prevalence = 20.3%).

**Adjusted Odds Ratios (aOR):**

| Variable | aOR | 95% CI | p-value |
|----------|-----|--------|---------|
| Diabetes (HbA1c ≥ 6.5%) | 1.48 | [1.18, 1.86] | **0.001** |
| Education level | 0.74 | [0.67, 0.82] | **< 0.001** |
| Income quartile | 0.91 | [0.83, 1.00] | 0.055 |
| eGFR (CKD marker) | 1.00 | [0.99, 1.01] | 0.688 |
| Age (per year) | 1.10 | [1.08, 1.11] | **< 0.001** |
| Female sex | 0.60 | [0.50, 0.73] | **< 0.001** |
| Alcohol experience | 0.96 | [0.75, 1.23] | 0.771 |

**McFadden pseudo-R² = 0.228** (within the "excellent fit" range of 0.20–0.40)

**VIF check:** All predictors < 2.5 — no multicollinearity. The eGFR–age correlation (expected given the CKD-EPI formula) does not inflate variance.

**Key findings:**
- Diabetes is independently associated with ~48% higher odds of tooth loss (p = 0.001)
- Higher education is a protective factor (aOR = 0.74 per level, p < 0.001)
- eGFR is **not** an independent predictor after adjustment (p = 0.688)

---

## Requirements

```bash
pip install pandas numpy matplotlib scikit-learn imbalanced-learn xgboost lightgbm statsmodels pycaret
```

Python 3.11+ recommended.

---

## File Structure

```
├── Main/
│   └── 김용한_과제2.ipynb   # full analysis notebook
├── csv/
│   └── KNHANES9.csv         # raw survey data (not tracked)
└── README.md
```
