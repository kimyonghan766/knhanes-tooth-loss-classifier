# Environment

Exact versions the analysis in `Main/final.ipynb` and `Main/final(65+).ipynb` was run under.
Both notebooks call into R through `rpy2`, so a Python-only setup is **not** sufficient.

## Versions

| Component | Version |
|---|---|
| Python | 3.11.9 (pyenv) |
| Jupyter kernel | `python3` — display name `3.11.9` |
| R | 4.5.1 (2025-06-13) |
| R package `survey` | 4.4.8 |
| rpy2 | 3.6.7 |

Full Python dependency set: [`requirements.txt`](requirements.txt) (`pip freeze`, 154 packages).

Key direct dependencies:

```
numpy==2.4.6          pandas==2.3.3         scipy==1.17.1
scikit-learn==1.8.0   statsmodels==0.14.6   matplotlib==3.10.9
xgboost==3.2.0        lightgbm==4.6.0       catboost==1.2.10
optuna==4.9.0         shap==0.51.0          dcurves==1.1.7
rpy2==3.6.7
```

## Restore

```bash
pyenv install 3.11.9              # if not already present
pyenv virtualenv 3.11.9 teethcount
pyenv activate teethcount
pip install -r requirements.txt
```

R side (must exist before `rpy2` is imported):

```r
install.packages("survey")        # 4.4.8
```

Verify:

```bash
python -c "import rpy2.robjects as ro; from rpy2.robjects.packages import importr; \
importr('survey'); print(ro.r('R.version.string')[0])"
```

## Why the pins matter here

These are not cautionary — each has already or will imminently break the notebooks:

- **scikit-learn** — `LogisticRegression(penalty=...)` was deprecated in 1.8 and is
  **removed in 1.10**. The notebooks have been migrated (`l1_ratio` for elastic net,
  `C=np.inf` for unpenalised Platt scaling), so they run on 1.8 *and* 1.10. Versions
  below 1.8 will not accept the new spelling.
- **shap** — the return shape of `TreeExplainer.shap_values` changed across releases.
  §8 carries a compatibility shim (`sv_raw.ndim == 3` / `isinstance(sv_raw, list)`) for
  exactly this reason.
- **rpy2** — must be built against the installed R. A different R major version generally
  requires reinstalling `rpy2` from source.
- **R `survey`** — §8, §10, and §10.3 index `summary(svyfit)$coefficients` and
  `confint(svyfit)` **positionally**. Column ordering is not part of the package's public
  API, so a different `survey` version can silently mislabel the odds-ratio tables.
- **pandas** — `pd.get_dummies(..., dummy_na=True)` names the missing-value column
  `<prefix>_nan`; §5 drops the all-zero ones by that exact suffix.

## Data

The `csv/` directory holds the KNHANES raw files (`HN20_all.csv` … `HN24_all.csv`) and is
not redistributed here. Both notebooks read from `../csv/` relative to `Main/`.
