# Tooth Loss Risk Predictor — Web App

Single-page Streamlit screening tool for the KNHANES 2020–2024 tooth-loss study.
Wraps the tuned **XGBoost** model from `Main/test(age).ipynb` (Test AUC 0.8025).

## Files
| File | Purpose |
|---|---|
| `export_model.py` | Reproduces the notebook preprocessing, refits XGBoost with the tuned params, dumps `model.pkl` + `meta.json`. Run once. |
| `app.py` | Streamlit form → prediction + SHAP. Loads the two artifacts. |
| `model.pkl` / `meta.json` | Generated artifacts (model pipeline + feature schema + MCC threshold). |
| `requirements.txt` | Pinned deps matching the project `.venv`. |

## Run locally
```bash
# from repo root, using the project venv
.venv/bin/python webapp/export_model.py      # regenerate artifacts (only if data/params change)
.venv/bin/streamlit run webapp/app.py
```
Opens at http://localhost:8501.

## How it works
- The form exposes ~22 friendly fields; raw KNHANES encodings are hidden behind dropdowns.
- **eGFR** (CKD-EPI 2021), **diabetes** (HbA1c ≥ 6.5% OR diagnosed), and **brushing frequency** are computed in-app to match training.
- Fields not on the form (diet, urinalysis, region/occupation dummies) are left blank and auto-imputed by the pipeline's trained median/mode — so predictions still run.
- **HIGH / LOW** label uses the MCC-optimised threshold (~0.55) selected from out-of-fold probabilities.

## Deploy (optional)
Push the repo to GitHub → connect at [streamlit.io/cloud](https://streamlit.io/cloud), main file `webapp/app.py`. The CSVs are **not** needed at runtime — only `model.pkl` + `meta.json`.

> For research use only — not medical advice.
