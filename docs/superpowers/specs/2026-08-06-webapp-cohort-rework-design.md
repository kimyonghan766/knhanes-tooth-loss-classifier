# Webapp Cohort Rework — Design

**Date:** 2026-08-06
**Scope:** Rebuild `webapp/` so it matches the current `Main/final.ipynb` (≥50) and
`Main/final(65+).ipynb` (≥65) notebooks, and switch cohorts automatically at age 65.

---

## 1. Motivation

The shipped app is trained and configured from a pipeline the notebooks no longer use.
Six concrete defects:

| # | Defect | Location |
|---|---|---|
| 1 | `BD1` recode inverted — `{1:1, 2:0}`, but `BD1` is *lifetime drinking experience* with `1 = Never`. Never-drinkers are trained and scored as drinkers. | `export_model.py:142` |
| 2 | `OR1` (self-rated oral health) absent — now the **#1 non-age SHAP feature in both cohorts** (0.421 / 0.329, ~2× the next). | `app.py` form |
| 3 | Other modelled features absent: `marri_2`, `genertn`, `fam_rela`, `BS12_1`, `HE_chol`, `HE_HDL_st2`, `cfam`, `L_BR_FQ`, `HE_Upro`, `HE_Ucrea`. Dropped upstream but still present: `marri_1`, `N_EN`. | `export_model.py`, `app.py` |
| 4 | One-hot fill is wrong. Notebook §6 drops reference levels and adds explicit `*_nan` "unknown" columns (`dummy_na=True`); the app fills every un-asked dummy with `0`, which now silently means the *reference level* (`region_1` = Seoul, `house_1`, `live_t_1`, `occp_1` = Manager/professional). | `app.py:69` |
| 5 | SHAP will crash on the ≥65 model — `TreeExplainer` is hardcoded against `named_steps["model"]` after only the imputer, but the ≥65 winner is Logistic Regression behind an imputer→**scaler**→model pipeline. | `app.py:101-114` |
| 6 | Displayed probability is uncalibrated. §10.3 Platt scaling improves weighted Brier 0.1518 → 0.1310 (≥50). | `app.py:186` |

Model selection also flipped in both cohorts once §9 began ranking by OOF AUPRC instead of
Test AUPRC:

| Cohort | Best model | Weighted Test AUC | Weighted Test AUPRC | MCC thresh (OOF) | Youden (OOF) | Features |
|---|---|---|---|---|---|---|
| ≥50 | **CatBoost** | 0.8339 | 0.6230 | 0.5571 | 0.5245 | 79 |
| ≥65 | **Logistic Regression** | 0.7524 | 0.6891 | 0.5378 | 0.4757 | 77 |

The shipped `meta.json` claims XGBoost / AUC 0.8025 / threshold 0.5501 / 66 features.

---

## 2. Architecture

```
webapp/
  export_cohort_models.py   offline build; emits both cohorts' artifacts
  features.py               field spec, row builder, derived features
  explain.py                SHAP dispatch (Tree vs Linear)
  app.py                    Streamlit UI only
  artifacts/
    model_50plus.pkl   meta_50plus.json
    model_65plus.pkl   meta_65plus.json
  requirements.txt
  README.md
```

`export_model.py`, `model.pkl` and `meta.json` are removed and replaced. Nothing outside
`webapp/` and this spec file is modified — the notebooks, `csv/`, `diagrams/` and
`Main/codebook_labels.py` are read-only inputs.

Four units, each independently understandable:

- **`export_cohort_models.py`** — reads `csv/`, writes `artifacts/`. Never imported by the app.
- **`features.py`** — pure functions: user inputs + a cohort's meta → a one-row DataFrame
  in that cohort's exact training schema. No Streamlit import, no model import.
- **`explain.py`** — pure function: fitted pipeline + meta + one row → a labelled Series
  of feature contributions. No Streamlit import.
- **`app.py`** — Streamlit only. Renders the field spec, calls the two modules, plots.

---

## 3. `export_cohort_models.py`

A single `build(age_threshold)` reproducing notebook §2.1 → §4 → §6 verbatim, invoked at
50 and 65. It refits **only the winning model for that cohort**, using the Optuna
parameters printed in notebook cell 49 (seeded TPE, reproducible — Optuna is not re-run).

**≥50 — CatBoost**
```
iterations=500, depth=4, learning_rate=0.02251362873975811,
l2_leaf_reg=3.114641923909002, auto_class_weights="Balanced",
random_seed=42, verbose=0
```
Pipeline: `imputer → model`.

**≥65 — Logistic Regression**
```
C=0.22694567397762977, l1_ratio=0.8629273218532529,
solver="saga", max_iter=1000, class_weight="balanced", random_state=42
```
Pipeline: `imputer → scaler → model`, where `scaler` is notebook §6's `make_scaler()`
(standardise the ordinal block, pass the binary block through unchanged in place,
standardise the continuous block).

Preprocessing reproduced exactly, including the parts the old script lacked:

- reference levels dropped per `nominal_ref = {tins:10, region:1, occp:1, house:1, live_t:1, marri_2:1, genertn:1, fam_rela:1}`
- `dummy_na=True`, then all-zero `*_nan` columns dropped
- `MIN_DUMMY_COUNT = 20` rare-dummy guard, **counted on train rows only**
- `BD1 → {1:0, 2:1}`, `BP1 → 5 - BP1`, `BS12_1 → {1:1, 2:0}`
- role lists ordered `[ordinal_scaled | binary | continuous]` — `make_scaler()` addresses
  them as contiguous index ranges, so the order is load-bearing

Temporal split unchanged: train 2020–2023, test 2024. Test metrics survey-weighted by
`wt_itvex`; fitting and threshold selection stay unweighted.

### Artifacts per cohort

`model_<cohort>.pkl` — the fitted pipeline.

`meta_<cohort>.json`:

| Key | Purpose |
|---|---|
| `cohort`, `age_threshold` | 50 or 65 |
| `model_name` | drives the explainer branch in `explain.py` |
| `feature_cols` | derived, post rare-dummy guard — the exact column order |
| `ordinal_scaled_cols`, `binary_cols`, `continuous_cols` | role lists |
| `mcc_threshold`, `youden_threshold` | OOF-derived, raw-probability scale |
| `platt_slope`, `platt_intercept` | §10.3 recalibration, fit on **train OOF** |
| `test_auc`, `test_auprc`, `brier_raw`, `brier_recal` | survey-weighted, for the caption |
| `train_positive_rate`, `n_train`, `n_test` | display |
| `labels` | `{feature_col: plain-English label}`, pre-baked |
| `linear_background_mean` | ≥65 only — train-set column means on the scaled scale |

**Labels are baked at build time** via `Main/codebook_labels.label_for()`, so the app never
reads `codebook.md` at runtime and the deploy footprint stays two files per cohort.

**Platt is fit on train OOF probabilities, not the test set** (notebook cell 86), so it
carries no test leakage and exports cleanly.

### Build-time assertions

`Main/shap_importance_50plus.npz` and `shap_importance_65plus.npz` are a hard oracle
written by the notebooks themselves. The build fails loudly rather than shipping a drifted
model if any of these do not hold:

1. `feature_cols == npz["feature_names"]` element-wise — 79 (≥50), 77 (≥65)
2. `model_name == npz["model_name"]` — `CatBoost`, `Logistic Regression`
3. weighted Test AUC / AUPRC reproduce `0.8339 / 0.6230` and `0.7524 / 0.6891` to 4 dp
4. MCC threshold reproduces `0.5571` and `0.5378` to 4 dp
5. (≥65) the closed-form linear contributions in §5 match `shap.LinearExplainer` on a
   sample of train rows to within 1e-9

---

## 4. `features.py`

One declarative `FIELDS` spec drives both the form rendering and the row builder, so a
schema change is one edit rather than two that can disagree.

Each entry declares: the raw KNHANES column, widget kind, label, option codes, bounds,
default, and which section it belongs to.

### Derived features (computed in-app, matching training)

| Feature | Rule |
|---|---|
| `eGFR` | CKD-EPI 2021, race-free, from serum creatinine + age + sex |
| `diabetes` | `HbA1c ≥ 6.5` OR diagnosed |
| `brush_freq` | brushing count; `BM1_0 = 1 if brush_freq > 0 else 0` |

### Recodes

| Column | Rule |
|---|---|
| `BD1` | `{1: 0, 2: 1}` — **the fix**; raw `1 = Never` |
| `BP1` | `5 - raw`, so higher = more stressed |
| `BS12_1` | `{1: 1, 2: 0}` |

### One-hot expansion

Nominal answers expand against the cohort's own `feature_cols`:

- the selected level sets its dummy to `1.0`
- a level that is the **reference** sets no dummy — all zeros is its correct encoding
- "Unknown / prefer not to say" sets `<parent>_nan = 1.0` **where that column exists in
  this cohort** (only `occp_nan` does, in both cohorts); otherwise the option is not offered
- **Dropdown options are derived from `feature_cols`, never hardcoded.** `fam_rela_3.0`
  (Child) and `fam_rela_8.0` (Sibling) survive the rare-dummy guard at ≥50 but not at ≥65,
  so those two options must disappear when the ≥65 cohort is active — otherwise selecting
  them would silently fall back to the reference level `fam_rela_1` (Self).

### Left to the imputer

The dietary block — `N_CA`, `N_NA`, `N_PROT`, `N_TDF`, `LS_VEG1`, `LS_FRUIT`, `N_SUGAR` —
is grams/day from a 24-hour recall and cannot be meaningfully self-reported. These stay
`NaN` and the pipeline imputes the training median. The result panel says so explicitly.

Every other modelled feature is user-supplied.

---

## 5. `explain.py`

```python
contributions(model, meta, row_df, top_n=10) -> pd.Series  # labelled, sorted by |value|
```

Branches on `meta["model_name"]`:

**Logistic Regression** — impute, scale, then

```
phi_j = coef_j * (x_j - background_mean_j)
```

That is exactly what `shap.LinearExplainer` reduces to with a train-set background
(notebook cell 68 states this), so only the mean vector is stored rather than a
~4000 × 77 background matrix. Equivalence is asserted at build time (§3, assertion 5).

**CatBoost** — `shap.TreeExplainer` over the imputed matrix, carrying the notebook's
compatibility shim:

```python
sv = sv_raw[..., 1] if getattr(sv_raw, "ndim", 0) == 3 else (sv_raw[1] if isinstance(sv_raw, list) else sv_raw)
```

Contributions are labelled from `meta["labels"]` and returned as a plain Series. Unlike the
current implementation, one-hot dummies are **not** dropped from the chart — `live_t_2.0`,
`region_15.0`, `region_16.0`, `occp_nan`, `marri_2_3.0` and `fam_rela_2.0` all rank inside
the top 20, and their labels are now readable ("Housing type: Apartment", "Region:
Gyeongbuk", "Occupation: Missing/not reported").

---

## 6. `app.py` — UI and the age switch

### Cohort selection

Age moves to the **top of the page, above the form columns**, because it selects the
cohort. `age >= 65` loads the ≥65 artifacts; otherwise the ≥50 artifacts. Model,
threshold, headline metrics, dropdown option sets and SHAP all switch together — one
`load_cohort(age)` call returns `(model, meta)` and everything downstream keys off it.

A banner makes the active cohort explicit:

```
Age 67 → ≥65 cohort · Logistic Regression · Test AUC 0.752 · threshold 0.538
Age 58 → ≥50 cohort · CatBoost            · Test AUC 0.834 · threshold 0.557
```

Age slider stays 50–80. KNHANES top-codes age at 80.

### Form sections

**1 · Demographics & household** — age, sex, income quartile, education, marital status
(`marri_2`), household member count (`cfam`), generation composition (`genertn`),
relationship to householder (`fam_rela`), housing type (`live_t`), home ownership
(`house`), occupation (`occp`), health insurance (`tins`), region, urban/rural (`town_t`)

**2 · Clinical labs** — HbA1c, diagnosed diabetes, BMI, serum creatinine, uric acid,
systolic BP, diastolic BP, triglycerides, total cholesterol (`HE_chol`), HDL
(`HE_HDL_st2`), urine protein (`HE_Upro`, 0–5 dipstick), urine creatinine (`HE_Ucrea`)

**3 · Lifestyle** — current smoker, e-cigarette ever used (`BS12_1`), lifetime drinking
(`BD1`), aerobic activity, perceived stress (`BP1`), breakfast frequency (`L_BR_FQ`)

**4 · Oral health** — self-rated oral health (`OR1`), toothache past year (`O_pain`),
dental visit past year (`MO4_00`), brushings per day

### Result panel

- **Headline:** the Platt-recalibrated probability as a percentage.
- **HIGH / LOW:** compares the raw score against the raw MCC threshold, displayed as the
  Platt-transformed threshold alongside the recalibrated percentage. Platt scaling is
  monotone increasing (slope > 0 in every fitted model), so
  `raw >= t ⟺ platt(raw) >= platt(t)` — the decision is bit-identical to the notebook's
  while the displayed number becomes calibrated.
- **Caption:** raw score, computed eGFR, diabetes flag, cohort, and an explicit note that
  the dietary block was defaulted to the cohort's training median.
- **SHAP chart:** horizontal bars, red = increases risk, blue = decreases, top 10.
- Research-use-only disclaimer retained.

---

## 7. Dependencies

`webapp/requirements.txt` is realigned to the versions the notebooks actually ran under
(`ENVIRONMENT.md`), and gains `catboost`:

```
streamlit>=1.40
scikit-learn==1.8.0
catboost==1.2.10
shap==0.51.0
pandas==2.3.3
numpy==2.4.6
joblib==1.3.2
matplotlib==3.10.9
```

`xgboost` is dropped — neither cohort's winning model needs it. The current
`pandas==3.0.3` pin contradicts `ENVIRONMENT.md`'s `pandas==2.3.3`; the notebook value wins.

---

## 8. Verification

1. `python webapp/export_cohort_models.py` runs clean — all five build assertions in §3 pass
   for both cohorts.
2. `streamlit run webapp/app.py` starts; a prediction renders at age 58 and at age 67.
3. Crossing age 60 → 67 visibly flips the banner, threshold, and SHAP chart, and the
   `fam_rela` dropdown loses its "Child" and "Sibling" options.
4. A row assembled from the ≥50 test set through `features.py` scores within 1e-9 of the
   same row taken straight from the notebook's `X_test` — confirms the form-to-schema
   mapping introduces no drift.
5. The ≥65 SHAP path returns finite values and does not raise (the current code path
   raises).

---

## 9. Out of scope

- Retuning, re-running Optuna, or re-running any notebook.
- Any change to `Main/`, `csv/`, `diagrams/`, or the root `README.md`.
- Survey-weighted inference, decision curve analysis, and the forest plot — these are
  reporting artifacts of the paper, not the screening tool.
- Persisting or transmitting user-entered values. The app stays stateless.

## 10. Note, not actioned

`Main/final.ipynb` cell 6 comments `BS12_1` as "Secondhand smoke exposure, indoor
workplace". `codebook.md:340` defines it as *"Ever used nicotine e-cigarette (vape)"*. The
recode `{1:1, 2:0}` is correct either way and the feature's mean |SHAP| is 0.000 in both
cohorts, so nothing is broken — but the notebook comment is wrong and the webapp label
follows the codebook, not the comment. Flagged for the notebook author to fix separately.
