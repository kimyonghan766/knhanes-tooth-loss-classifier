# Tooth Loss Risk Predictor — Web App

Single-page Streamlit screening tool for the KNHANES 2020–2024 tooth-loss study.
Predicts having **fewer than 20 functional teeth**, trained on 2020–2023 and evaluated
on the held-out 2024 wave.

The app serves **two cohort models**, and age selects between them.

| Cohort | Model | Test AUC | Test AUPRC | Threshold (MCC, OOF) | Features |
|---|---|---|---|---|---|
| **≥ 50** | CatBoost | 0.8339 | 0.6230 | 0.5571 | 79 |
| **≥ 65** | Logistic Regression | 0.7524 | 0.6891 | 0.5378 | 77 |

Test metrics are **survey-weighted** (`wt_itvex`) population estimates; model selection
and threshold selection are unweighted, as in the notebooks.

## Files

| File | Purpose |
|---|---|
| `export_cohort_models.py` | Reproduces the notebook preprocessing, refits each cohort's winning model, writes `artifacts/`. Run once. |
| `features.py` | Field spec, derived features, and the row builder. Drives both the form and the model schema. |
| `explain.py` | Per-prediction SHAP contributions — TreeExplainer for CatBoost, closed-form linear SHAP for Logistic Regression. |
| `app.py` | Streamlit UI. |
| `verify_app.py` | Headless checks, including a round trip of real 2024 test respondents through the form. |
| `artifacts/` | Generated: `model_{50,65}plus.pkl` + `meta_{50,65}plus.json`. |

## Run locally

```bash
pip install -r webapp/requirements.txt

python webapp/export_cohort_models.py    # regenerate artifacts (needs ../csv/)
python webapp/verify_app.py              # optional: 23 headless checks
streamlit run webapp/app.py
```

Opens at http://localhost:8501.

## How it works

**Age selects the cohort.** The age slider sits above the form. At 65 and above the app
loads the ≥65 artifacts, and the model, decision threshold, headline metrics, dropdown
option sets and SHAP chart all switch together.

**36 fields.** Every modelled variable is user-supplied except the seven dietary columns
(`N_CA`, `N_NA`, `N_PROT`, `N_TDF`, `LS_VEG1`, `LS_FRUIT`, `N_SUGAR`), which are grams/day
from a 24-hour recall and cannot be self-reported. Those are left blank, imputed to the
cohort's training median, and disclosed in the result panel.

**Derived in-app, matching training exactly:** eGFR (CKD-EPI 2021) from serum creatinine,
diabetes (HbA1c ≥ 6.5% OR diagnosed), and brushing frequency + "brushed yesterday".

**Categorical options are derived from each cohort's `feature_cols`, never hardcoded.**
The notebooks drop a reference level per nominal variable and apply a rare-dummy guard at
20 training positives, and that guard drops different levels in each cohort — `fam_rela`
"Child" and "Sibling" survive at ≥50 but not at ≥65. Offering a level the cohort cannot
represent would silently encode it as the reference category instead.

**Probabilities are Platt-recalibrated** (§10.3), fitted on training out-of-fold
predictions so no test data leaks into deployment. This improves weighted Brier from
0.1518 → 0.1310 (≥50) and 0.1975 → 0.1939 (≥65). Because Platt scaling is monotone, the
HIGH/LOW decision is bit-identical to the notebook's raw-score comparison; only the
displayed number changes. The recalibrated threshold is shown next to it (0.557 → 34.1%
at ≥50), which is why the displayed HIGH cutoff reads lower than the raw threshold.

## Verification

`export_cohort_models.py` asserts itself against `Main/shap_importance_{50,65}plus.npz`,
which the notebooks wrote. The build fails rather than shipping a drifted model if the
feature schema, the selected model, the survey-weighted test AUC/AUPRC or the OOF
thresholds do not reproduce. All ten currently match to 4 decimal places.

`verify_app.py` additionally round-trips 600 real 2024 test respondents through
`features.build_row()` and requires the encoding back exactly — covering reference levels,
explicit `*_nan` unknowns, the cohort-specific rare-dummy guard, and every direct field.

## Deploy

Push to GitHub → connect at [streamlit.io/cloud](https://streamlit.io/cloud), main file
`webapp/app.py`. The raw CSVs are **not** needed at runtime — only `artifacts/`. Display
labels are baked into the meta files at build time, so `codebook.md` is not needed either.

> For research use only — not medical advice.
