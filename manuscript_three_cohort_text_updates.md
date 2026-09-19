# Manuscript text updates for adding the 50–64 cohort

This report lists every place in the main narrative text (not the tables/figures,
which you've already updated) that needs rewording now that the study has **three**
age cohorts (≥50, ≥65, 50–64) instead of two. For each item you get:

- **Location** – which section it's in
- **Find this** (a few words before/after included so you can locate it with
  Ctrl/Cmd+F) – the *current* text
- **Replace with** – the *proposed* new text
- **Why** – what changed and whether it's a pure wording fix or also a numeric/
  correctness fix

Design decisions already confirmed with you and baked into the wording below:

1. **Design framing:** the three cohorts are a nested + stratified hybrid — ≥50 is
   the parent cohort; ≥65 and 50–64 are its two **mutually exclusive** strata (they
   partition ≥50 between them). Comparisons involving ≥50 are not independent
   (overlap); comparisons between ≥65 and 50–64 directly are not confounded by
   overlap with each other.
2. **DCA in 50–64:** explicitly call out that the 50–64 CatBoost model loses net
   benefit over treat-all at the 20%/30% thresholds (unlike the other two cohorts).
3. **Calibration in 50–64:** explicitly flag its much worse raw ECE (0.232 vs.
   0.017 / 0.038).
4. **Shared-SHAP-feature significance:** headline stat is "significant in all
   three cohorts" (5 of the 9 features shared across all three cohorts' top-15
   rankings qualify: age, self-rated oral health, education, current smoking,
   toothache history).

Numbers used below (50–64 cohort) came from Table 1–4 as you've already updated
them, plus two notebook cells:

- `Main/CB_50-64.ipynb`, cells 38/43/49 (Optuna leaderboard): 50–64 out-of-fold
  AUPRC winner is **XGBoost** (OOF AUPRC 0.3492); CatBoost is third (OOF AUPRC
  0.3393, i.e. 0.0099 lower); DeLong test of CatBoost vs. XGBoost on test-set
  AUC is **not** significant (p = 0.17).
- `Main/CB_50-64.ipynb`, cell 57 ("Adjusted odds ratios (survey::svyglm, Taylor
  linearization)") — this is the full-candidate-set regression that produces
  Table 4's aORs (confirmed by matching its BMI aOR, 1.037, exactly against
  Table 4). **Complete-case n = 5,905** out of 7,167 eligible (**17.6%
  excluded**), complete-case prevalence **10.2%** vs. 10.9% in the full
  eligible sample (a **0.7 percentage point** drop). Note: `OG_50-64.ipynb`
  only contains a different, smaller sub-model (the top-15 SHAP-informed
  regression, n=6,164) — that one is *not* the source of Table 4.

---

## Abstract

### A1. Objectives sentence

**Find** (starts right after "Objectives."):
> "This study developed explainable machine-learning models to classify
> functional tooth loss in two pre-specified nested age cohorts and examined
> whether features identified as important for prediction by SHAP also showed
> substantial adjusted associations in a prespecified survey-weighted
> multivariable logistic regression using the full candidate predictor set."

**Replace with:**
> "This study developed explainable machine-learning models to classify
> functional tooth loss in three pre-specified age cohorts — a combined nested
> and stratified design spanning adults aged ≥50, its ≥65 subset, and the
> mutually exclusive 50–64 stratum — and examined whether features identified
> as important for prediction by SHAP also showed substantial adjusted
> associations in a prespecified survey-weighted multivariable logistic
> regression using the full candidate predictor set."

*Why:* pure wording — cohort count and design description.

---

### A2. Methods sentence (sample sizes)

**Find** (in "Methods."):
> "Five pooled KNHANES waves (2020–2024) were analyzed in two cohorts: adults
> aged ≥50 (n=14,871) and ≥65 (n=7,704), with 2020–2023 as the training set and
> 2024 as the test set."

**Replace with:**
> "Five pooled KNHANES waves (2020–2024) were analyzed in three age cohorts:
> adults aged ≥50 (n=14,871), of whom the ≥65 (n=7,704) and 50–64 (n=7,167)
> strata are mutually exclusive subsets, with 2020–2023 as the training set and
> 2024 as the test set."

*Why:* wording + adds the 50–64 n (7,167 = 14,871 − 7,704, matches Table 1).

---

### A3. Results sentence (AUPRC/prevalence)

**Find** (in "Results."):
> "AUPRC was higher in the ≥65 cohort (CatBoost; 0.69) compared to the ≥50
> cohort (CatBoost; 0.62), with functional tooth loss prevalence of 27.8% (≥50)
> and 43.6% (≥65)."

**Replace with:**
> "AUPRC was highest in the ≥65 cohort (CatBoost; 0.69), intermediate in the
> ≥50 cohort (CatBoost; 0.62), and lowest in the 50–64 cohort (CatBoost; 0.33),
> broadly tracking functional tooth loss prevalence of 43.6% (≥65), 27.8% (≥50),
> and 10.9% (50–64)."

*Why:* wording + numeric addition (50–64 AUPRC/prevalence from Tables 1–2).

---

### A4. Results sentence (top SHAP predictors)

**Find:**
> "Age, education level, household income, current smoking status, and
> self-rated oral health ranked among the top SHAP predictors and also showed
> substantial adjusted associations with tooth loss in both cohorts."

**Replace with:**
> "Age, education level, current smoking status, self-rated oral health, and
> toothache history ranked among the top SHAP predictors and also showed
> substantial adjusted associations with tooth loss in all three cohorts,
> whereas household income showed a substantial adjusted association only in
> the ≥65 cohort."

*Why:* **correctness fix, not just wording.** Household income (p = 0.23 in ≥50,
0.91 in 50–64) is only significant in ≥65 — it should not be grouped with the
features that are significant in all cohorts. Toothache history was added since
it *is* significant in all three and belongs in this list; per your decision,
the headline is "significant in all three cohorts."

---

### A5. Conclusions sentence (abstract)

**Find** (last sentence of "Conclusions."):
> "Features identified as highly important for prediction by SHAP generally
> also showed substantial adjusted associations in the prespecified
> multivariable logistic regression across both cohorts, although a subset of
> top-ranked features showed little evidence of a strong adjusted association."

**Replace with:**
> "Features identified as highly important for prediction by SHAP generally
> also showed substantial adjusted associations in the prespecified
> multivariable logistic regression across all three cohorts, although this
> consistency was weaker in the 50–64 cohort, and a subset of top-ranked
> features showed little evidence of a strong adjusted association in any
> cohort."

*Why:* wording + reflects that 50–64 shows weaker agreement (per your decision
on the shared-feature stats).

---

## 1. Introduction

### I1. Study aim sentence

**Find** (second-to-last sentence of Introduction):
> "Therefore, this study developed and temporally evaluated explainable
> machine-learning models for functional tooth loss in two nested age cohorts
> (≥50 and ≥65 years), alongside a prespecified survey-weighted multivariable
> logistic regression using the full candidate predictor set."

**Replace with:**
> "Therefore, this study developed and temporally evaluated explainable
> machine-learning models for functional tooth loss in three age cohorts (≥50
> years, its ≥65-year subset, and the mutually exclusive 50–64-year stratum),
> alongside a prespecified survey-weighted multivariable logistic regression
> using the full candidate predictor set."

*Why:* pure wording.

*(No other Introduction sentences need changing — the final sentence already
says "whether these patterns differed by age cohort," which generalizes fine
to three cohorts.)*

---

## 2. Materials and methods

### M1. Cohort-definition paragraph (major rewrite)

**Find** (full paragraph, right after "candidate features examined in this study
are summarized in Supplementary Table S1"):
> "Two pre-specified nested age cohorts were defined: adults aged 50 years and
> older, and older adults aged 65 years and older. From the pooled records
> retained after variable screening, respondents missing the tooth-count
> outcome were excluded, yielding analytic samples of 14,871 participants in
> the ≥50 cohort and 7,704 in the ≥65 cohort (Figure 1). Because the ≥65 cohort
> is a subset of the ≥50 cohort, the two cohorts are not independent samples,
> and comparisons between them should be interpreted with this overlap in mind.
> The outcome was functional tooth loss, defined as fewer than 20 natural
> teeth, based on the KNHANES total natural tooth count. Twenty natural teeth
> is widely accepted as a threshold for satisfactory masticatory function and
> dietary diversity [13]. Prevalence was 27.8% in the ≥50 cohort and 43.6% in
> the ≥65 cohort."

**Replace with:**
> "Three pre-specified age cohorts were defined, combining a nested and a
> stratified design: adults aged 50 years and older (the parent cohort), and
> its two mutually exclusive age strata — adults aged 65 years and older, and
> adults aged 50–64 years. From the pooled records retained after variable
> screening, respondents missing the tooth-count outcome were excluded,
> yielding analytic samples of 14,871 participants in the ≥50 cohort, 7,704 in
> the ≥65 cohort, and 7,167 in the 50–64 cohort (Figure 1). Because the ≥65 and
> 50–64 cohorts are both subsets of the ≥50 cohort, none of the three samples
> are fully independent of one another; however, the ≥65 and 50–64 cohorts are
> mutually exclusive of each other, so comparisons made directly between them
> are not confounded by the sample overlap that affects comparisons involving
> the ≥50 cohort. This overlap structure should be kept in mind when
> interpreting cross-cohort comparisons. The outcome was functional tooth loss,
> defined as fewer than 20 natural teeth, based on the KNHANES total natural
> tooth count. Twenty natural teeth is widely accepted as a threshold for
> satisfactory masticatory function and dietary diversity [13]. Prevalence was
> 27.8% in the ≥50 cohort, 43.6% in the ≥65 cohort, and 10.9% in the 50–64
> cohort."

*Why:* major wording rewrite reflecting the confirmed nested+stratified hybrid
design (your decision #1), plus added n/prevalence numbers.

---

### M2. Complete-case exclusion sentence

**Find:**
> "However, complete-case restriction excluded 21.3% and 24.8% of eligible
> respondents in the ≥50 and ≥65 cohorts respectively, with tooth-loss
> prevalence 2.9–3.6 percentage points lower in each complete-case sample than
> in its full eligible sample. This suggests missingness is not strictly
> random with respect to the outcome, particularly in the older cohort. After
> complete-case restriction, the regression analytic samples comprised 11,695
> participants in the ≥50 cohort and 5,790 participants in the ≥65 cohort."

**Replace with:**
> "However, complete-case restriction excluded 21.3%, 24.8%, and 17.6% of
> eligible respondents in the ≥50, ≥65, and 50–64 cohorts respectively, with
> tooth-loss prevalence lower in each complete-case sample than in its full
> eligible sample (2.9–3.6 percentage points in the ≥50 and ≥65 cohorts, and
> 0.7 percentage points in the 50–64 cohort). This suggests missingness is not
> strictly random with respect to the outcome, particularly in the older
> cohorts, though the smaller prevalence shift in the 50–64 cohort suggests its
> complete-case sample is comparatively less affected. After complete-case
> restriction, the regression analytic samples comprised 11,695 participants in
> the ≥50 cohort, 5,790 participants in the ≥65 cohort, and 5,905 participants
> in the 50–64 cohort."

*Why:* wording + numbers now confirmed from `CB_50-64.ipynb` cell 57 (see the
notes at the top of this report): n=5,905, exclusion 17.6%, prevalence drop 0.7
points (10.9% → 10.2%). Note the 50–64 prevalence shift is much smaller than in
the other two cohorts — I added a clause reflecting that rather than lumping it
in with "particularly in the older cohort," since the data don't actually
support the older cohorts (plural) being uniformly more affected than 50–64.

---

### M3. Model-selection / SHAP common-model justification (§2.1)

**Find** (in "Machine learning model development and evaluation," discussing
CatBoost as the common model):
> "In the unconstrained model-selection procedure based on out-of-fold AUPRC
> (Supplementary Table S3), CatBoost ranked first in the ≥50 cohort, whereas
> elastic-net logistic regression ranked first in the ≥65 cohort; CatBoost
> ranked second in the ≥65 cohort, with an out-of-fold AUPRC only 0.0006 lower
> than elastic-net logistic regression (Table S3). CatBoost was therefore used
> as the common model for SHAP comparison despite not being the top-ranked
> classifier in the ≥65 cohort."

**Replace with:**
> "In the unconstrained model-selection procedure based on out-of-fold AUPRC
> (Supplementary Table S3), CatBoost ranked first in the ≥50 cohort; elastic-net
> logistic regression ranked first in the ≥65 cohort, with CatBoost second
> (out-of-fold AUPRC only 0.0006 lower); and XGBoost ranked first in the 50–64
> cohort, with CatBoost third (out-of-fold AUPRC 0.3393 vs. 0.3492, a gap of
> 0.0099; DeLong test on test-set AUC, CatBoost vs. XGBoost, p=0.17, not
> significant). CatBoost was therefore used as the common model for SHAP
> comparison across all three cohorts, despite not being the top-ranked
> classifier by out-of-fold AUPRC in the ≥65 or 50–64 cohorts."

*Why:* wording + adds the 50–64 leaderboard result (from `CB_50-64.ipynb` cells
43/49 — XGBoost wins OOF AUPRC, CatBoost third but not significantly worse on
test AUC).

---

### M4. Sex-stratified fairness sentence (§2.1)

**Find:**
> "To assess fairness under TRIPOD+AI checklist item 23 (Table S5), model
> performance was evaluated separately across sex within each nested age
> cohort."

**Replace with:**
> "To assess fairness under TRIPOD+AI checklist item 23 (Table S5), model
> performance was evaluated separately across sex within each of the three age
> cohorts."

*Why:* pure wording ("nested" no longer accurately describes all three
cohorts as a set).

---

## 3. Results

### R1. Table 1 narrative paragraph

**Find** (paragraph right after Table 1, starting "Participants with
functional tooth loss..."):
> "Participants with functional tooth loss were older and had lower education
> and household income than participants retaining ≥20 teeth in both cohorts.
> They also reported poorer self-rated oral health, lower brushing frequency,
> lower rates of brushing on the previous day, and lower dental-visit
> frequency, while current smoking status, diabetes, hypertension, and rural
> residence were more common among those with tooth loss (Table 1). Dietary
> intakes of fibre, calcium, sodium, and protein were generally lower among
> participants with tooth loss, whereas fresh fruit intake was higher; several
> characteristics, including urine creatinine, breakfast frequency, sex, and
> secondhand smoke exposure, showed little or no difference in at least one
> cohort."

**Replace with:**
> "Participants with functional tooth loss were older and had lower education,
> household income, and self-rated oral health than participants retaining
> ≥20 teeth in all three cohorts. They also reported lower brushing frequency
> and lower rates of brushing on the previous day in all three cohorts.
> Current smoking status, diabetes, and urban/rural residence were more common
> among those with tooth loss in all three cohorts, whereas hypertension and
> past-year dental-visit frequency differed by tooth-loss status in the ≥50 and
> ≥65 cohorts but not in the 50–64 cohort (P=0.23 and P=0.42, respectively).
> Dietary intakes of fibre and calcium were generally lower among participants
> with tooth loss across all three cohorts, while sodium, protein, and
> urine-creatinine differences reached significance in some but not all
> cohorts (Table 1); fresh fruit intake differed by tooth-loss status in all
> three cohorts. Several characteristics, including breakfast frequency, sex,
> and secondhand smoke exposure, showed little or no difference in at least
> one cohort."

*Why:* **correctness fix, not just wording.** With three cohorts, "both
cohorts" phrasing breaks down variable-by-variable — hypertension (P=0.23) and
dental-visit frequency (P=0.42) are *not* significant in the 50–64 cohort, so
they can't be folded into an "all three" claim. I kept the diet-related
sentence intentionally general rather than adjudicating every nutrient
(sodium/protein/urine-creatinine significance patterns differ by cohort in
non-uniform ways) — please sanity-check this sentence against Table 1
yourself if you want more precision.

---

## 3.1 Predictive performance

### R2. Model-selection / leaderboard sentence

**Find:**
> "The unconstrained model-selection procedure ranked CatBoost first in the
> ≥50 cohort and elastic-net logistic regression first in the ≥65 cohort by
> out-of-fold AUPRC (Supplementary Table S3). CatBoost was retained as the
> common model for cross-cohort SHAP comparisons given its comparable
> out-of-fold performance. In the ≥65 cohort, the 2024 test-set AUROC did not
> differ significantly between CatBoost and elastic-net logistic regression by
> the DeLong test (Supplementary Table S4). In the ≥50 cohort, CatBoost
> achieved an AUROC of 0.83 and an AUPRC of 0.62. In the ≥65 cohort, CatBoost
> achieved an AUROC of 0.76 and an AUPRC of 0.69. At the MCC-derived
> operational thresholds, sensitivity was 0.63 (95% CI 0.59–0.67) and
> specificity was 0.84 (95% CI 0.82–0.85) in the ≥50 cohort, compared with 0.62
> (95% CI 0.58–0.66) and 0.75 (95% CI 0.72–0.78), respectively, in the ≥65
> cohort (Table 2)."

**Replace with:**
> "The unconstrained model-selection procedure ranked CatBoost first in the
> ≥50 cohort, elastic-net logistic regression first in the ≥65 cohort, and
> XGBoost first in the 50–64 cohort, by out-of-fold AUPRC (Supplementary Table
> S3). CatBoost was retained as the common model for cross-cohort SHAP
> comparisons given its comparable out-of-fold performance in the ≥50 and ≥65
> cohorts, and its statistically indistinguishable test-set performance
> relative to the leaderboard winner in the 50–64 cohort despite ranking
> third. In the ≥65 cohort, the 2024 test-set AUROC did not differ
> significantly between CatBoost and elastic-net logistic regression by the
> DeLong test (Supplementary Table S4); similarly, in the 50–64 cohort,
> CatBoost's test-set AUROC did not differ significantly from XGBoost's
> (DeLong p=0.17). In the ≥50 cohort, CatBoost achieved an AUROC of 0.83 and an
> AUPRC of 0.62. In the ≥65 cohort, CatBoost achieved an AUROC of 0.76 and an
> AUPRC of 0.69. In the 50–64 cohort, CatBoost achieved an AUROC of 0.81 and an
> AUPRC of 0.33. At the MCC-derived operational thresholds, sensitivity was
> 0.63 (95% CI 0.59–0.67) and specificity was 0.84 (95% CI 0.82–0.85) in the
> ≥50 cohort, 0.62 (95% CI 0.58–0.66) and 0.75 (95% CI 0.72–0.78) in the ≥65
> cohort, and 0.54 (95% CI 0.46–0.61) and 0.88 (95% CI 0.86–0.90) in the 50–64
> cohort (Table 2)."

*Why:* wording + adds the 50–64 model-selection result and performance
figures (all from your updated Table 2 and the `CB_50-64.ipynb` leaderboard).

---

### R3. Calibration & DCA paragraph

**Find** (paragraph right after Table 3):
> "Calibration curves for the common CatBoost model in each cohort, following
> Platt recalibration, closely tracked the diagonal of perfect calibration
> across most of the probability range, with a modest overprediction of the
> probability of functional tooth loss in the 0.4–0.5 predicted-probability
> band (Figure 3). DCA was performed on the held-out 2024 test set; therefore,
> treat-all net benefit was determined by the outcome prevalence in the
> corresponding test set. Both cohort-specific CatBoost models provided net
> benefit exceeding treat-none and treat-all strategies across the threshold
> probabilities examined (10%, 20%, and 30%), with the net benefit advantage
> widening at higher threshold probabilities in both cohorts (Table 3)."

**Replace with:**
> "Calibration curves for the common CatBoost model in the ≥50 and ≥65
> cohorts, following Platt recalibration, closely tracked the diagonal of
> perfect calibration across most of the probability range, with a modest
> overprediction of the probability of functional tooth loss in the 0.4–0.5
> predicted-probability band (Figure 3). Calibration in the 50–64 cohort was
> markedly worse (raw ECE 0.232, versus 0.017 in the ≥50 cohort and 0.038 in
> the ≥65 cohort; Table 3), consistent with this cohort's much lower outcome
> prevalence and correspondingly sparser positive-class information. DCA was
> performed on the held-out 2024 test set; therefore, treat-all net benefit was
> determined by the outcome prevalence in the corresponding test set. The ≥50
> and ≥65 cohort-specific CatBoost models provided net benefit exceeding
> treat-none and treat-all strategies across the threshold probabilities
> examined (10%, 20%, and 30%), with the net benefit advantage widening at
> higher threshold probabilities in both cohorts. The 50–64 cohort model
> provided net benefit over treat-all only at the 10% threshold (0.048 vs.
> 0.008); at the higher 20% and 30% thresholds its net benefit fell below
> treat-all (0.027 vs. -0.116, and 0.009 vs. -0.276, respectively), unlike the
> other two cohorts (Table 3)."

*Why:* **correctness fix, not just wording** — per your decisions #2 and #3.
The blanket "both cohort-specific CatBoost models provided net benefit... at
all three thresholds" claim is false for the 50–64 cohort at 20%/30%, and the
calibration sentence needed to flag the much worse ECE rather than implying
uniformly good calibration across all three cohorts.

---

## 3.2 Cross-method comparison of predictive importance and adjusted associations

### R4. "Two highest-ranked SHAP features" sentence

**Find** (first sentence of this subsection):
> "Age and self-rated oral health were the two highest-ranked SHAP features in
> both cohorts, with education, income, and toothache also ranking highly."

**Replace with:**
> "Age and self-rated oral health were the two highest-ranked SHAP features in
> all three cohorts, with education, income, and toothache also ranking
> highly."

*Why:* pure wording (assumes the rank order still holds with three cohorts —
please double-check this against your updated Figure 4 beeswarm plots, since I
only have p-values, not SHAP rank order, for the 50–64 cohort).

---

### R5. Shared-feature-count paragraph (major rewrite)

**Find** (full paragraph, right before Figure 4):
> "Eleven features were shared across the cohort-specific top-15 SHAP
> rankings, and nine of these 11 features had 95% confidence intervals
> excluding the null in both cohorts. Income quartiles showed evidence of an
> adjusted association only in the ≥65 cohort, whereas daily brushing
> frequency did not have a confidence interval excluding the null in either
> cohort. Among the four cohort-specific SHAP features in each cohort, one had
> a 95% confidence interval excluding the null in each cohort: region
> (Gyeongbuk) in the ≥50 cohort and brushing yesterday in the ≥65 cohort (Table
> 4)."

**Replace with:**
> "Nine features were shared across all three cohorts' top-15 SHAP rankings,
> and five of these nine features — age, self-rated oral health, education
> level, current smoking status, and toothache history — had 95% confidence
> intervals excluding the null in all three cohorts. Diabetes and
> city/countryside residence had confidence intervals excluding the null in
> the ≥50 and ≥65 cohorts but not in the 50–64 cohort. Income quartile showed
> evidence of an adjusted association only in the ≥65 cohort, and daily
> brushing frequency did not have a confidence interval excluding the null in
> any of the three cohorts. A further four features (dietary fiber, uric acid,
> triglycerides, and calcium intake) were each shared between only two of the
> three cohorts' top-15 rankings rather than all three. Among the
> cohort-specific SHAP features (three in the ≥50 cohort, four in the ≥65
> cohort, and three in the 50–64 cohort), one of three reached significance in
> the ≥50 cohort (frequency of fruit intake), two of four in the ≥65 cohort
> (brushing yesterday and daily total sugar), and two of three in the 50–64
> cohort (sex and BMI) (Table 4)."

*Why:* **correctness fix, not just wording**, for two reasons:
1. The shared-feature count and significance breakdown had to be recomputed for
   three cohorts (per your decision #4: headline = "significant in all three").
2. The old text's ≥50-cohort-specific example, **"region (Gyeongbuk)"**, no
   longer matches your updated Table 4, which lists the ≥50-only predictors as
   Housing Type: Apartment, eGFR, and Frequency of Fruit Intake (of which only
   fruit intake, P=0.012, is significant). This mismatch exists independently
   of the cohort-count change — it looks like Table 4 was regenerated with a
   different candidate-variable set than when this sentence was originally
   written, so this needed fixing regardless.

---

## 4. Discussion

### D1. Age/SHAP opening sentence

**Find** (second sentence of Discussion):
> "Age is well known to be associated with tooth loss [35,36,8], and was the
> highest-ranked SHAP feature in both cohorts and showed a positive adjusted
> association with tooth loss (aOR 1.09–1.11)."

**Replace with:**
> "Age is well known to be associated with tooth loss [35,36,8], and was the
> highest-ranked SHAP feature in all three cohorts and showed a positive
> adjusted association with tooth loss (aOR 1.09–1.11)."

*Why:* pure wording (aOR range 1.091–1.114 across all three cohorts still
rounds to the same 1.09–1.11 range, so no numeric change needed here).

---

## 4.1 Model performance by age cohort

### D2. AUPRC/AUROC/prevalence paragraph (major rewrite)

**Find** (the whole subsection):
> "The ≥65 cohort achieved higher AUPRC compared to the ≥50 cohort, whereas its
> AUROC was lower (Table 2). The lower AUROC may partly reflect the narrower
> age distribution in the ≥65 cohort, which could reduce the discriminatory
> contribution of age. Conversely, the higher AUPRC is consistent with the
> higher prevalence of functional tooth loss in this cohort, underscoring the
> importance of interpreting AUROC and AUPRC together."

**Replace with:**
> "AUPRC and prevalence tracked each other closely across the three cohorts:
> AUPRC was highest in the ≥65 cohort (0.69, prevalence 43.6%), intermediate in
> the ≥50 cohort (0.62, prevalence 27.8%), and lowest in the 50–64 cohort
> (0.33, prevalence 10.9%), whereas AUROC showed the opposite ordering —
> highest in the ≥50 cohort (0.83), lowest in the ≥65 cohort (0.76), and
> intermediate in the 50–64 cohort (0.81) (Table 2). The lower AUROC in the
> ≥65 cohort may partly reflect its narrower age distribution, which could
> reduce the discriminatory contribution of age; conversely, its higher AUPRC
> is consistent with its higher prevalence of functional tooth loss. The 50–64
> cohort illustrates the same principle from the opposite direction: its low
> prevalence yields the lowest AUPRC of the three cohorts despite reasonable
> discrimination (AUROC 0.81), and its calibration was also markedly worse
> than the other two cohorts (raw ECE 0.232 vs. 0.017 in the ≥50 cohort and
> 0.038 in the ≥65 cohort; Table 3), consistent with sparser positive-class
> information at this lower prevalence. Together, these patterns underscore
> the importance of interpreting AUROC, AUPRC, and calibration jointly,
> particularly in lower-prevalence strata."

*Why:* wording + substantive extension of the existing AUROC/AUPRC-tradeoff
argument to the 50–64 cohort, plus the calibration flag (your decision #3).

---

## 4.2 Prediction, inference, and comparison with prior work

### D3. Shared-feature paragraph (major rewrite)

**Find** (first paragraph of §4.2):
> "The cross-method comparison showed that predictive importance and adjusted
> statistical association were related but not interchangeable. Among the 11
> features shared between the two cohort-specific top-15 SHAP rankings, nine
> showed 95% confidence intervals excluding the null in both cohorts,
> suggesting that high predictive importance frequently coincided with
> evidence of an adjusted association among the most consistently ranked
> features. Age, self-rated oral health, education level, current smoking
> status, diabetes, city/countryside residence, dietary fiber intake, and
> toothache history showed directionally consistent adjusted associations
> across both cohorts, while income quartile showed an adjusted association in
> the ≥65 cohort but not the ≥50 cohort. These findings suggest that many
> features that were highly useful for CatBoost prediction also exhibited
> substantial adjusted associations when all prespecified predictors were
> considered simultaneously."

**Replace with:**
> "The cross-method comparison showed that predictive importance and adjusted
> statistical association were related but not interchangeable. Nine features
> were shared across all three cohorts' top-15 SHAP rankings; of these, five —
> age, self-rated oral health, education level, current smoking status, and
> toothache history — showed 95% confidence intervals excluding the null in
> all three cohorts, suggesting that high predictive importance coincided with
> a consistent adjusted association for this subset of features regardless of
> age stratum. Diabetes and city/countryside residence showed adjusted
> associations excluding the null in the ≥50 and ≥65 cohorts but not in the
> 50–64 cohort, income quartile showed an adjusted association only in the ≥65
> cohort, and daily brushing frequency did not reach significance in any of
> the three cohorts. A further four features (dietary fiber, uric acid,
> triglycerides, and calcium intake) were each shared between only two of the
> three cohorts' top-15 rankings, reflecting some divergence in SHAP-ranked
> importance between mid-life and older adulthood. These findings suggest that
> many features that were highly useful for CatBoost prediction also exhibited
> substantial adjusted associations when all prespecified predictors were
> considered simultaneously, though this correspondence was weaker in the
> lower-prevalence 50–64 cohort."

*Why:* **correctness fix, not just wording** — mirrors the Results §3.2 fix
(R5 above) so the Discussion's summary numbers match the recomputed
three-cohort statistics rather than repeating the old two-cohort framing.

---

### D4. Brushing-frequency example sentence

**Find:**
> "Similarly, daily brushing frequency was among the highly ranked predictive
> features but showed little evidence of an adjusted association in either
> cohort (aOR 0.976, 95% CI 0.922–1.034; P=0.411 in ≥50; aOR 0.970, 95% CI
> 0.907–1.038; P=0.377 in ≥65)."

**Replace with:**
> "Similarly, daily brushing frequency was among the highly ranked predictive
> features but showed little evidence of an adjusted association in any
> cohort (aOR 0.976, 95% CI 0.922–1.034, P=0.41 in ≥50; aOR 0.970, 95% CI
> 0.907–1.038, P=0.38 in ≥65; aOR 0.967, 95% CI 0.866–1.079, P=0.55 in
> 50–64)."

*Why:* wording ("either" → "any") + adds the 50–64 statistics (from Table 4).
Also tidied the P-value rounding (0.41/0.38) to match Table 4 exactly instead
of the slightly more precise 0.411/0.377 in the original text — flagging this
as a minor pre-existing rounding inconsistency you may want either way.

---

### D5. "Extends prior work" nested-design paragraph (major rewrite)

**Find** (paragraph beginning "Where this study extends prior work is
twofold."):
> "Where this study extends prior work is twofold. Most existing
> machine-learning studies of tooth loss pool participants across the full
> adult age range into a single model and evaluate performance within a single
> cross-sectional sample [8]. By contrast, the present study reports two
> nested age cohorts in parallel, which makes differences in predictor
> rankings between the ≥50 and ≥65 cohorts visible rather than averaged away,
> and evaluates each cohort's classifiers under a strict temporal split rather
> than a single in-sample evaluation. Because the ≥65 cohort is nested within
> the ≥50 cohort rather than a demographically independent sample, findings
> that are consistent between cohorts should not be interpreted as independent
> replication; the nested design is informative for detecting age-related
> differences in predictor behavior, but agreement between cohorts should not
> be read as external validation."

**Replace with:**
> "Where this study extends prior work is twofold. Most existing
> machine-learning studies of tooth loss pool participants across the full
> adult age range into a single model and evaluate performance within a single
> cross-sectional sample [8]. By contrast, the present study reports three age
> cohorts in parallel — the ≥50 cohort and its two mutually exclusive age
> strata, ≥65 and 50–64 — which makes differences in predictor rankings across
> mid-life and older adulthood visible rather than averaged away, and
> evaluates each cohort's classifiers under a strict temporal split rather
> than a single in-sample evaluation. This combined nested-and-stratified
> design has different implications for interpreting agreement across
> cohorts. Because the ≥65 and 50–64 cohorts are both subsets of the ≥50
> cohort, findings that are consistent between the ≥50 cohort and either of
> its component strata should not be interpreted as independent replication.
> However, because the ≥65 and 50–64 strata are mutually exclusive of each
> other, consistent findings between these two non-overlapping cohorts are not
> subject to this same overlap-driven non-independence, and so offer a
> somewhat stronger — though still not fully external — check on the
> generalizability of predictor behavior across age. Overall, the design is
> informative for detecting age-related differences in predictor behavior, but
> agreement across cohorts should not be read as external validation."

*Why:* major rewrite implementing your decision #1 (nested + stratified
hybrid framing) — this is the paragraph that most needed the design
explanation, since it previously described only a single nesting relationship.

---

## 4.3 Implications, limitations, and future work

### D6. Limitations sentence (optional addition)

**Find:**
> "SHAP comparisons used a common CatBoost model across cohorts rather than
> each cohort's top-ranked classifier, prioritizing interpretability
> comparability over strict cohort-specific model selection."

**Replace with:**
> "SHAP comparisons used a common CatBoost model across all three cohorts
> rather than each cohort's top-ranked classifier, prioritizing
> interpretability comparability over strict cohort-specific model selection;
> this trade-off was most pronounced in the 50–64 cohort, where CatBoost
> ranked third rather than first by out-of-fold AUPRC."

*Why:* wording + optional strengthening of the limitations statement, since
the model-selection gap is now largest in the newly added cohort. Feel free to
skip the added clause if you'd rather keep this sentence short.

---

## 5. Conclusions

### C1. Conclusions paragraph (major rewrite)

**Find** (full first paragraph of §5):
> "This study identified features that contributed to prediction in each of
> two nested age cohorts and compared their predictive importance with
> adjusted associations from a prespecified survey-weighted multivariable
> logistic regression. Most features shared between the cohort-specific top-15
> SHAP rankings showed directionally consistent adjusted associations, with
> nine of the 11 shared features having confidence intervals excluding the
> null in both cohorts. However, several highly predictive features showed
> little evidence of a strong adjusted association, demonstrating that
> predictive importance and conventional adjusted association are related but
> distinct constructs. Performance and predictor rankings were described
> separately for each cohort, most notably differences in the contribution of
> oral-hygiene measures and a subset of socioeconomic covariates between the
> ≥50 and ≥65 cohorts, supporting consideration of age-specific approaches to
> identifying prevalent functional tooth loss. The generalizability of the
> model needs to be further validated in non-Korean populations."

**Replace with:**
> "This study identified features that contributed to prediction in each of
> three age cohorts — the ≥50 cohort and its two mutually exclusive strata,
> ≥65 and 50–64 — and compared their predictive importance with adjusted
> associations from a prespecified survey-weighted multivariable logistic
> regression. Many features shared across the three cohort-specific top-15
> SHAP rankings showed directionally consistent adjusted associations, with
> five of the nine features shared across all three cohorts having confidence
> intervals excluding the null in all three. However, several highly
> predictive features showed little evidence of a strong adjusted
> association, and this pattern was more pronounced in the 50–64 cohort than
> in the other two, demonstrating that predictive importance and conventional
> adjusted association are related but distinct constructs. Performance and
> predictor rankings were described separately for each cohort, most notably
> a markedly lower AUPRC and poorer calibration in the low-prevalence 50–64
> cohort, together with differences in the contribution of oral-hygiene
> measures and a subset of socioeconomic covariates across the three cohorts,
> supporting consideration of age-specific approaches to identifying prevalent
> functional tooth loss. The generalizability of the model needs to be
> further validated in non-Korean populations."

*Why:* wording + correctness fix mirroring D3/R5's recomputed shared-feature
statistics, plus adds the 50–64 cohort's distinct performance profile.

---

## Figure/table captions

### F1. Figure 4 caption

**Find:**
> "Figure 4. SHAP beeswarm plot of the top-ranked predictors in each nested
> age cohort."

**Replace with:**
> "Figure 4. SHAP beeswarm plot of the top-ranked predictors in each age
> cohort."

*Why:* pure wording (drop "nested" since it no longer describes the full set
of three cohorts).

*(Table/Figure captions for Tables 1–4, Figure 1, 2, 3, and 5 already read
generically — e.g. "across age cohorts," "in each nested age cohort" is not
used elsewhere — so no other caption changes are needed. Table 2's "Table 2.
Performance of the common CatBoost model across age cohorts" is already fine.)*

---

## Summary checklist

| # | Section | Type | Needs your input? |
|---|---------|------|---|
| A1–A5 | Abstract | wording (+1 correctness fix, A4) | No |
| I1 | Introduction | wording | No |
| M1 | Methods §2 cohort definitions | wording | No |
| M2 | Methods §2 complete-case exclusion | wording + numbers now resolved | No |
| M3 | Methods §2.1 model selection | wording | No |
| M4 | Methods §2.1 fairness sentence | wording | No |
| R1 | Results Table 1 paragraph | correctness fix | No (but sanity-check diet clause) |
| R2 | Results §3.1 leaderboard/performance | wording | No |
| R3 | Results §3.1 calibration/DCA | correctness fix | No |
| R4 | Results §3.2 opening sentence | wording | Yes — confirm against Fig. 4 rank order |
| R5 | Results §3.2 shared-feature paragraph | correctness fix (incl. stale "region" reference) | No |
| D1 | Discussion opening | wording | No |
| D2 | Discussion §4.1 | correctness fix | No |
| D3 | Discussion §4.2 shared-feature paragraph | correctness fix | No |
| D4 | Discussion §4.2 brushing example | wording | No |
| D5 | Discussion §4.2 "extends prior work" | major rewrite (design framing) | No |
| D6 | Discussion §4.3 limitations | optional wording | No |
| C1 | Conclusions | correctness fix | No |
| F1 | Figure 4 caption | wording | No |
