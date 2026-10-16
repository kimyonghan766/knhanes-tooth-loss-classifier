# Environment for the current CB notebooks

This environment reproduces the manuscript-authoritative analyses in:

- [`Main/CB_50+.ipynb`](Main/CB_50+.ipynb)
- [`Main/CB_50-64.ipynb`](Main/CB_50-64.ipynb)
- [`Main/CB_65+.ipynb`](Main/CB_65+.ipynb)

All three notebooks call R through `rpy2` for complex-survey analyses, so a Python-only environment is not sufficient for a complete run. The `OG_` notebooks are archived earlier versions and are not part of the current environment target.

## Verified versions

| Component | Version |
|---|---|
| Python | 3.11.9 (pyenv) |
| Jupyter kernel | Display name `3.11.9` |
| R | 4.5.1 (2025-06-13) |
| R package `survey` | 4.4.8 |
| rpy2 | 3.6.7 |

The complete Python environment is pinned in [`requirements.txt`](requirements.txt), which contains 154 packages. Key analysis dependencies are:

```text
numpy==2.4.6          pandas==2.3.3         scipy==1.17.1
scikit-learn==1.8.0   statsmodels==0.14.6   matplotlib==3.10.9
xgboost==3.2.0        lightgbm==4.6.0       catboost==1.2.10
optuna==4.9.0         shap==0.51.0          dcurves==1.1.7
rpy2==3.6.7
```

## Restore the environment

```bash
pyenv install 3.11.9
pyenv virtualenv 3.11.9 teethcount
pyenv activate teethcount
python -m pip install -r requirements.txt
```

R and the `survey` package must be available before importing `rpy2`:

```r
install.packages("survey")
```

Verify the R bridge and installed `survey` version:

```bash
python -c "import rpy2.robjects as ro; from rpy2.robjects.packages import importr; survey = importr('survey'); print(ro.r('R.version.string')[0]); print(ro.r(\"as.character(packageVersion('survey'))\")[0])"
```

## Run the notebooks

The notebooks resolve `../csv/` relative to `Main/`, so start Jupyter from that directory:

```bash
cd Main
jupyter lab
```

Restart the kernel and run all cells in each current notebook:

1. `CB_50+.ipynb`
2. `CB_50-64.ipynb`
3. `CB_65+.ipynb`

The notebooks are analytically independent; this order is suggested only for easier cross-cohort review. Do not reuse a kernel between notebooks, and do not run only downstream cells after changing cohort construction, preprocessing, or model settings.

At the documentation update on 2026-10-16, each notebook contained 34 code cells with sequential execution counts 1–34 and no saved exception outputs. A new manuscript run should reproduce that clean execution state rather than relying on these stored counts.

## Regenerate the cross-cohort figures

Run each builder with the same Python 3.11.9 environment after rerunning the notebooks:

```bash
python diagrams/3_cohorts/forest_plot/build_cross_cohort_forest_plot.py
python diagrams/3_cohorts/shap_summary/build_cross_cohort_shap_summary_overlay.py
python diagrams/3_cohorts/roc_pr_overlay/build_roc_pr_overlay.py
python diagrams/3_cohorts/calibration_dca_overlay/build_calibration_dca_overlay.py
```

The builders contain assertions that stop rendering if expected notebook outputs, feature labels, cohort metrics, or saved DCA values have drifted.

## Version-sensitive behavior

- **scikit-learn:** Elastic-net logistic regression uses the scikit-learn 1.8 API, in which the penalty is inferred from `l1_ratio`. The unpenalized Platt mapping uses `LogisticRegression(C=np.inf)`. Use the pinned version when reproducing manuscript results.
- **SHAP:** `TreeExplainer.shap_values` has returned different binary-class shapes across releases. The notebooks include compatibility handling for a 3D array, a list of class arrays, or a 2D array.
- **rpy2:** It must be built against the installed R version. Changing R may require reinstalling `rpy2`.
- **R `survey`:** The regression sections extract coefficients and confidence intervals from `survey` objects. Retain the pinned version and inspect table labels after any upgrade.
- **pandas:** The encoded schema depends on the `<prefix>_nan` columns produced by `pd.get_dummies(..., dummy_na=True)`.
- **Tree learners:** Fixed seeds are used where supported, but multithreaded learners can still show small platform-dependent numerical differences.

The saved notebooks contain two recurring nonfatal warnings: LightGBM can warn that prediction input lacks feature names after pipeline transformation, and scikit-learn can note that an unpenalized logistic model ignores regularization parameters. Neither warning stopped the recorded runs, but any new or different warning should be reviewed.

## Data and paths

The notebooks expect these files:

```text
csv/HN20_all.csv
csv/HN21_all.csv
csv/HN22_all.csv
csv/HN23_all.csv
csv/HN24_all.csv
```

All five files are currently tracked in Git. Confirm KNHANES redistribution permissions before publishing the repository or creating a public archive. The analysis uses paths relative to `Main/`; running notebooks from a different working directory without adjusting those paths will fail.

## Reproducibility record

For any run used in a manuscript submission or release, archive these items together:

- the exact Git commit;
- the fully executed three `CB_` notebooks;
- the regenerated cross-cohort PNGs and SHAP `.npz` files;
- `requirements.txt` and the R/`survey` versions; and
- a record of the source KNHANES files and their checksums.

The ancillary `webapp/` has its own exported model artifacts and currently uses older 79- and 77-column schemas. Passing `webapp/verify_app.py` confirms those artifacts are internally consistent; it does not establish that they match the current 88-column manuscript pipeline.
