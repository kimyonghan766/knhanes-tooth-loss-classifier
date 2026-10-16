# KNHANES tooth-loss methods/code audit

Audit date: 2026-10-15 (Asia/Seoul)

Scope: current working-tree versions of `Main/CB_50+.ipynb`, `Main/CB_50-64.ipynb`, and `Main/CB_65+.ipynb`; current raw CSVs; cross-cohort figure builders; README/environment files; and local Git history. Archived `OG_` notebooks and the ancillary web application were not treated as sources of manuscript results.

This is a code audit, not confirmation that the selected KNHANES weight or annual variable definitions are correct under KNHANES documentation. No new sensitivity model was run.

## Executive conclusions

1. All population-oriented 2024 discrimination and calibration point estimates use `wt_itvex`. The pooled descriptive and regression analyses use `wt_itvex / number_of_years_present` with year-specific strata and PSU identifiers. Because nutrition variables are included, the substantive choice of `wt_itvex` rather than a nutrition/integrated weight must be checked against the 2020–2024 KNHANES manuals.
2. The 2024 PR chance lines are the survey-weighted outcome prevalences: 0.2362 (≥50), 0.1058 (50–64), and 0.4023 (≥65). The cross-cohort plot deliberately draws three gray dashed horizontal lines—one per cohort—but gives them one shared legend entry.
3. Imputation, scaling, class-weight calculation, and hyperparameter tuning are fitted within training folds. Candidate-variable screening and the fixed rare-level/schema decisions occur before outer CV, on complete development cohorts rather than within each outer fold. The untouched 2024 outcomes are not used for these decisions.
4. Platt calibration and MCC/Youden threshold selection use nested OOF predictions from 2020–2023, not 2024. The calibration map is fitted once on all nested OOF predictions and then applied to 2024. Model code does not use 2024 to choose the OOF leaderboard winner, while Git history cannot prove the CatBoost pin was chosen before inspecting earlier 2024 results.
5. SHAP is computed for all 88 encoded columns, ranked by unweighted mean absolute SHAP, with no aggregation back to original predictor concepts. `TreeExplainer` uses its default raw model output; for binary CatBoost this is the raw margin/log-odds scale. SHAP explains the original CatBoost output, not the Platt-recalibrated probability.
6. Complete-case restriction is selective. Weighted prevalence falls from 23.88% to 21.42% in ≥50, 10.64% to 9.94% in 50–64, and 42.34% to 38.88% in ≥65. A sensitivity model was not run because its statistical method requires author approval.
7. Cross-year harmonization is assumed rather than demonstrated: the same source column names and recodes are applied after concatenation, with no year-specific variable map. Annual wording, protocol, unit, and codebook equivalence remain unverified.
8. “Prespecified” is not supported by the repository history. The repository has no dated protocol/preregistration, immutable configuration, release tag, or DOI; relevant choices continued to change after saved model-output commits.
9. The ≥50 notebook is not currently a clean executed source of truth: cells through preprocessing have execution counts 1–15, while downstream model/evaluation cells have `execution_count: null` despite retained outputs. The ≥50 notebook and all derived figures/tables should be cleanly rerun after the current uncommitted notebook edits.

## 4. Survey weights and design

The same policy is implemented in all three current notebooks. Representative source locations are the ≥50 notebook’s survey-design helper at `Main/CB_50+.ipynb:1022`, ML test-weight assignment at `Main/CB_50+.ipynb:1743`, and regression design at `Main/CB_50+.ipynb:3337` and `Main/CB_50+.ipynb:3423`.

| Analysis | Sample | Weight | Strata | PSU / variance handling | Additional processing |
|---|---|---|---|---|---|
| Descriptive estimates/tests | Eligible 2020–2024, variable-specific complete cases | `wt_itvex / d['year'].nunique()` | Integer factor of `year + kstrata` | Integer factor of `year + kstrata + psu`; `survey.lonely.psu="adjust"` | Normally `/5`, but the denominator is dynamically the number of years remaining for that variable |
| Exploratory regression | 2020–2024 complete cases for the full model | `wt_itvex / m['year'].nunique()` | Integer factor of `year + kstrata` | Integer factor of `year + kstrata + psu`; R `survey::svyglm`, Taylor linearization; lonely PSU adjustment | Five years are present in current frames, so this is `/5` |
| Nested CV / Optuna / OOF ranking | 2020–2023 development sample | No survey weight | Not used | Not used | Outcome class weights are used by the learners; these are not survey weights |
| 2024 AUROC, AUPRC, accuracy, recall, precision, F1, Brier, ECE, calibration bins | Full eligible 2024 test sample | Raw annual `wt_itvex` | Used only for CI resampling | PSU-within-`kstrata` cluster bootstrap, 2,000 draws | No pooling division; multiplying every weight by a constant would not change point metrics |
| 2024 sex-stratified discrimination/calibration | 2024 subgroup rows | Raw `wt_itvex` within sex | `kstrata` in subgroup bootstrap | PSU-within-stratum bootstrap | No pooling division |
| SHAP | 2024 test rows | Unweighted | Not used | Not used | Unweighted mean absolute SHAP |
| MCC/Youden thresholds | Nested OOF development predictions | Unweighted | Not used | Not used | Threshold learned without 2024; `roc_curve` uses its default threshold reduction |
| Confusion matrices, DeLong, DCA | 2024 test sample | Unweighted | Not used | Not used | Explicitly sample-level in notebook comments/README |

Important methodological check: predictors include dietary recall variables (`N_CA`, `N_NA`, `N_PROT`, `N_TDF`, `N_SUGAR`, etc.), yet every survey-weighted analysis uses `wt_itvex`. The code contains `wt_ntr`, `wt_tot`, and `wt_oent` in the source files but does not compare or select among them. KNHANES documentation must determine the proper weight for a combined examination-plus-nutrition analysis.

## 5. Weighted 2024 prevalence and PR baselines

The test sample is every age-eligible 2024 record with usable `O_TC`; predictor missingness does not remove ML test rows because predictors are imputed. `y_test = 1` means `O_TC < 20`. The values below were recomputed directly from `csv/HN24_all.csv` using the notebook outcome rule and raw `wt_itvex`.

| Cohort | 2024 n | Cases | Unweighted prevalence | Survey-weighted prevalence | PR chance baseline | Exact estimand |
|---|---:|---:|---:|---:|---:|---|
| ≥50 | 3,335 | 894 | 26.8066% | 23.6194% | 0.236194 | `np.average(y_test, weights=wt_itvex)` on all 3,335 test rows |
| 50–64 | 1,577 | 169 | 10.7166% | 10.5822% | 0.105822 | Same, on the 1,577-row age-restricted test set |
| ≥65 | 1,758 | 725 | 41.2400% | 40.2349% | 0.402349 | Same, on the 1,758-row age-restricted test set |

Each notebook sets `baseline = np.average(y_test, weights=w_test_arr)` and passes the same weights to both `precision_recall_curve` and `average_precision_score` (`Main/CB_50+.ipynb:3809`). Thus the baseline and plotted curve target the same weighted test population.

The cross-cohort figure builder recomputes the same baseline at `diagrams/3_cohorts/roc_pr_overlay/build_roc_pr_overlay.py:209`. It then draws one horizontal line for each cohort at lines 306–311, while adding a single empty proxy labeled “Chance” to the legend. Therefore the several gray dashed lines in Figure 2 represent the three different cohort prevalences, not alternative models or confidence limits. The current legend does not print their numeric levels; the caption should name the three baselines.

## 6. Validation-fold containment

| Operation | Where fitted/decided | Fold-contained? | Audit conclusion |
|---|---|---|---|
| Missingness screen | Entire cohort’s 2020–2023 development data (`Main/CB_50+.ipynb:645`) | No | 2024 is now excluded, but each outer validation fold informs the screen. Nested OOF estimates condition on a development-wide feature policy. |
| Redundancy exclusions | Fixed list plus diagnostics on complete 2020–2023 development cohort | No | `HE_obe`, `HE_wc`, `HE_glu`, and `N_EN` are removed before outer CV. |
| Rare-level pooling | Hard-coded policy described as derived from the ≥50 development cohort (`Main/CB_50+.ipynb:1611`) | No | The derivation is not executable in the current notebook; it is a fixed shared policy applied before outer CV. |
| One-hot encoding | `pd.get_dummies` before temporal split (`Main/CB_50+.ipynb:1618`) | No, strictly | The expected 88-column schema is hard-coded, absent columns are added, and unexpected levels fail. This limits leakage, but the transformation is not fitted separately in outer folds. |
| Sparse-dummy check | Full 2020–2023 cohort | No; diagnostic only | Sparse columns are retained and do not alter the feature set. |
| Imputation | `Pipeline(make_imputer(), model)` | Yes | Mode/median imputers are fitted by each inner/outer training fit (`Main/CB_50+.ipynb:1766`, `:2209`). |
| Scaling | LR pipeline after imputation | Yes | Standardization is fitted within the applicable training fit (`Main/CB_50+.ipynb:1774`). |
| Class weights | Learner training fold; XGBoost ratio explicitly recomputed | Yes | No full-data class ratio is used inside fold validation. |
| Feature selection | No model-based selection; development-wide screen/schema only | Not applicable beyond above | No test-set-driven feature selection was found in current source. |
| Hyperparameter optimization | Five-fold inner CV within each of five outer training partitions | Yes | Current source is genuinely nested (`Main/CB_50+.ipynb:2157`, `:2203`). A separate full-development search supplies final-refit parameters. |
| OOF predictions | Outer validation folds only | Yes | Each row is predicted by a model whose hyperparameters were selected without that row (`Main/CB_50+.ipynb:2211`). |
| Platt calibration | One unweighted logistic map fitted to all nested OOF development predictions | Development-only, not cross-fitted as a calibrator | Appropriate for mapping the final model before untouched 2024 evaluation; it does not use 2024 (`Main/CB_50+.ipynb:3947`). |
| MCC/Youden threshold | Nested OOF development predictions | Development-only | 2024 is not used. For exact MCC maximization, evaluate all unique prediction thresholds or call `roc_curve(..., drop_intermediate=False)`; the present default can omit an MCC optimum. |
| Final 2024 probabilities | Model refit on all 2020–2023 with full-development tuned parameters | Yes with respect to outcomes | No 2024 outcomes are used for fitting. The fixed pre-split encoding/schema caveat remains. |
| Model selection | OOF ranking; CatBoost explicitly pinned for common SHAP | Code: development-only | Git history does not establish that the human decision to pin CatBoost preceded inspection of 2024 results. |

Suggested manuscript wording: “Imputation, scaling, class weighting, and hyperparameter tuning were performed within training folds. Candidate screening and a fixed cross-cohort category schema were defined from the complete 2020–2023 development data and therefore were not re-estimated inside each outer fold.” Do not describe all preprocessing as fully nested.

## 7. SHAP aggregation and scale

| Question | Finding | Evidence |
|---|---|---|
| Number of columns explained | 88 in each cohort | All three `shap_importance_*_catboost.npz` files contain 88 feature names and 88 importances; notebooks assert the common 88-column schema |
| Model | Separately fitted CatBoost model in each cohort | `pinned_model_name='CatBoost'`; figure builder refits each cohort separately |
| Participant-level encoded-column aggregation | None | `TreeExplainer` returns one value per encoded column (`Main/CB_50+.ipynb:2979`) |
| Global ranking | Unweighted `mean(abs(SHAP), axis=0)` | `Main/CB_50+.ipynb:3117`; cross-cohort builder lines 205–213 |
| Concept-level grouping | None | Dummy columns such as region/occupation levels compete individually; signed dummy contributions are not summed back to concepts |
| Output scale | Raw model output (binary CatBoost margin/log-odds) | `TreeExplainer(pinned_classifier)` does not set `model_output`; the default is raw |
| Before/after calibration | Before Platt calibration | SHAP is computed from `pinned_model` directly; the recalibrator is created later and is not passed to SHAP |
| Plot meaning | Original CatBoost attribution, not change in recalibrated probability | Axis text “impact on model output” should specify raw margin/log-odds |

The current implementation is internally coherent as an encoded-column SHAP analysis, but it cannot support statements such as “the 43 predictor concepts were ranked” without a defined concept aggregation. A defensible concept-level alternative would need to be prespecified and regenerated; it should not be silently substituted during manuscript editing.

## 8. Complete-case missingness

This diagnostic reconstructed the current cleaned frames using the notebooks’ own cleaning, screening, and derivation cells, then applied the exact full-regression `dropna` specification. It did not fit an alternative model.

### Selection and prevalence

| Cohort | Full n | Complete-case n | Retained | Weighted prevalence, full | Weighted prevalence, complete case | Weighted prevalence, excluded |
|---|---:|---:|---:|---:|---:|---:|
| ≥50 | 14,871 | 11,695 | 78.64% | 23.88% | 21.42% | 32.95% |
| 50–64 | 7,167 | 5,905 | 82.39% | 10.64% | 9.94% | 13.74% |
| ≥65 | 7,704 | 5,790 | 75.16% | 42.34% | 38.88% | 52.53% |

Complete-case retention was also outcome-dependent: 81.80% versus 70.47% for non-cases versus cases in ≥50; 83.05% versus 77.01% in 50–64; and 79.96% versus 68.94% in ≥65. This is evidence that the regression complete cases are not a simple random subset.

### Main sources and patterns

- In ≥50, the largest individual missingness rates were physical activity (`pa_aerobic`, 8.98%), occupation (8.82%), and the linked nutrition variables (8.55–8.62%).
- In 50–64, the linked nutrition variables were highest (9.39–9.42%), followed by occupation and physical activity (about 6.1%).
- In ≥65, physical activity (11.68%), occupation (11.36%), education (8.79%), and nutrition (7.74–7.88%) dominated.
- The most common joint pattern was simultaneous absence of breakfast frequency and the nutrition block: 974 rows in ≥50, 568 in 50–64, and 406 in ≥65.
- Other common blocks were occupation plus physical activity; laboratory panels (`eGFR`, uric acid, cholesterol, HDL, triglycerides); urine protein plus urine creatinine; and older-participant questionnaire blocks.
- BMI was the largest single-variable-only exclusion: allowing BMI to be missing while all other model variables remained observed would recover 205 ≥50 rows, 25 rows aged 50–64, and 180 rows aged ≥65.

### Differences by year, sex, and age

Complete-case retention improved over waves: in ≥50 it rose from 66.86% in 2020 to 83.99% in 2024; in 50–64, from 70.62% to 88.27%; and in ≥65, from 63.14% to 80.15%. Sex differences were small in ≥50 (male 78.46%, female 78.78%), but diverged by age: females had higher retention in 50–64 (84.50% versus 79.56%) and lower retention in ≥65 (73.39% versus 77.46%). Age-group retention itself was 82.39% for 50–64 versus 75.16% for ≥65.

No multiple-imputation, inverse-probability, or reduced-core-predictor sensitivity analysis exists in the audited current pipeline. Choosing and running one would be a new analysis requiring author/statistical approval.

## 9. Evidence for prespecification

The local Git repository begins on 2026-05-20. It contains many result-dependent changes through 2026-10-14, including commits labeled “logistic platt scaling for calibration” (2026-08-09), “added catboost pinned model metrics” (2026-09-09), “changed weights etc.” (2026-09-17), SHAP-weighting changes (2026-09-19 and 2026-10-01), and “fixed diagrams and missingness” (2026-10-12). The current three notebook modifications are uncommitted.

No analysis-plan/protocol file, preregistration, immutable configuration, release tag, or contemporaneous decision log was found. The word “prespecified” appears in later notebook history, but current code comments are not proof of prospective specification. Safe wording is “specified in the analysis pipeline” or a direct description of the rule. Reserve “prespecified” for choices supported by a dated external protocol or other immutable record.

## 10. Cross-year harmonization

No year-indexed mapping object exists. All five CSVs are concatenated and the same names and recodes are applied. The audited columns below exist under the same names in all five local files; observed `sex` codes are 1 and 2 in every year.

| Concept | 2020 | 2021 | 2022 | 2023 | 2024 | Implemented recoding |
|---|---|---|---|---|---|---|
| Natural tooth count | `O_TC` | `O_TC` | `O_TC` | `O_TC` | `O_TC` | Numeric coercion, infinities to missing; outcome is `<20`. The code does not reconstruct tooth count from tooth-level fields. |
| Sex | `sex` | `sex` | `sex` | `sex` | `sex` | 1 male, 2 female; used directly in ML and converted to female indicator for regression |
| Education | `edu` | `edu` | `edu` | `edu` | `edu` | Common invalid-code replacement; otherwise treated as a shared ordinal code |
| Toothache | `O_pain` | `O_pain` | `O_pain` | `O_pain` | `O_pain` | Common invalid-code replacement; retained as binary |
| Examination/interview weight | `wt_itvex` | `wt_itvex` | `wt_itvex` | `wt_itvex` | `wt_itvex` | Annual raw weight for 2024; divided by years present for pooled design analyses |
| Stratum / PSU | `kstrata` / `psu` | same | same | same | same | Prefixed with year for pooled designs |
| Nutrition | `N_CA`, `N_NA`, `N_PROT`, `N_TDF`, `N_SUGAR` | same | same | same | same | Numeric coercion and common overflow handling; calcium/sodium rescaled only for regression reporting |
| Brushing | `BM1_0`–`BM1_8` | same | same | same | same | Common invalid-code handling; occasions summed, non-brushers forced to frequency 0 |

Code-level consistency does not establish that question wording, field protocols, units, universe/skip logic, or the meaning of a shared code stayed constant. Those items require annual KNHANES codebook review. One known availability break is explicitly handled by exclusion: `BM2_1`/`BM2_3` are absent in 2023–2024. A manuscript-ready harmonization appendix should cite annual codebook pages for every retained concept, not merely list matching column names.

## 3. Technical contribution versus prior work

The repository can substantiate these technical distinctions: three age-defined cohorts (one nested overall cohort plus two mutually exclusive strata), five candidate algorithms, nested CV with Optuna, temporally held-out 2024 evaluation, weighted test metrics and calibration, decision-curve analysis, a common CatBoost SHAP comparison, parallel exploratory survey-weighted regression, and sex-stratified performance calculations.

Code cannot establish novelty relative to Elani et al. or other literature. A defensible candidate contribution is the parallel age-stratified comparison of prediction importance and survey-weighted adjusted associations with temporally held-out evaluation, but this wording requires a literature review before being claimed as an advance.

## 11. Repository and reproducibility readiness

| Item | Finding |
|---|---|
| Remote | `https://github.com/kimyonghan766/knhanes-tooth-loss-classifier.git` |
| Persistent identifier | None found; a GitHub URL is not a DOI |
| Releases/tags | No Git tags |
| License | No `LICENSE` file found |
| Dependencies | `requirements.txt` and `ENVIRONMENT.md` exist |
| Environment drift | `ENVIRONMENT.md` still names obsolete `Main/final.ipynb` and `Main/final(65+).ipynb` rather than the three current CB notebooks |
| Raw-data boundary | Contrary to README’s statement that raw files are not redistributed, all five `csv/HN*_all.csv` files are tracked by Git. Confirm KNHANES redistribution rights before public archiving and remove them from future public history if required. |
| Executed provenance | 50–64 and ≥65 currently have sequential execution counts; ≥50 has downstream `null` counts with retained outputs and needs a clean rerun |
| DOI readiness | Create a versioned release only after the notebooks, figures, README, environment record, license/data-access boundary, and outputs are synchronized; then archive the release (for example through an institutional repository or Zenodo) |

Git/code cannot determine author CRediT roles, corresponding-author contact details, or the final generative-AI disclosure. Those require author agreement.

## Required actions before manuscript submission

1. Confirm the correct KNHANES weight for analyses combining oral examination, laboratory, interview, and nutrition variables; revise code and rerun if `wt_itvex` is not the documented integrated weight.
2. Decide whether development-wide screening/schema construction is acceptable. If retained, describe it accurately and avoid claiming all preprocessing was nested.
3. Cleanly rerun all three CB notebooks from fresh kernels, beginning with ≥50, then regenerate every cross-cohort figure and artifact.
4. Add the three numerical PR baselines to the Figure 2 caption or legend.
5. Clarify that SHAP ranks encoded columns on the CatBoost raw margin/log-odds scale; do not claim concept-level aggregation.
6. Report complete-case selection and the weighted prevalence shift. Obtain approval before selecting a sensitivity-analysis method.
7. Replace unsupported “prespecified” wording unless a dated external plan exists.
8. Build and cite an annual-codebook harmonization appendix.
9. Correct the repository’s environment documentation, data-redistribution boundary, license, and release/DOI metadata.

## Questions the repository still cannot answer

The code cannot provide a formal ethics exemption, choose the intended clinical/public-health user and action, establish novelty without literature comparison, assign named authorship/CRediT roles, supply author contact details, determine the complete AI-use disclosure, or determine the professor’s preferred revision/tracked-change format.
