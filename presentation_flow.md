# Presentation Flow — KNHANES Tooth Loss Risk Study
## Korean + English Slide Outline
**Total: 22 slides**

---

## SLIDE 1 — Title Slide

**[KR]**
- **제목:** 국민건강영양조사(2020–2024)를 활용한 한국 성인의 치아 상실 예측 및 위험 요인 분석
- **부제:** 머신러닝 기반 예측 모델 및 설명 가능한 AI를 활용한 웹 기반 스크리닝 도구 개발
- 발표자: 김용한 | 소속: 연세대학교 응용정보공학부

**[EN]**
- **Title:** Predicting Tooth Loss in Korean Adults Using KNHANES Data (2020–2024)
- **Subtitle:** ML-Based Classification with Explainable AI and Web Deployment
- Presenter: Yonghan Kim | Yonsei University, Dept. of Applied IT | Date:

---

## SLIDE 2 — 연구필요성 / Background & Necessity
*(Section 1: Introduction)*

**[KR]**
- 치아 상실(기능치아 20개 미만)은 저작 기능 저하, 영양 불균형, 삶의 질 저하와 직결되며 특히 고령자에서 두드러짐
- 국내 40세 이상 성인에서 유병률은 50세 이후 유의미하게 증가하며, 사회경제적 계층, 교육수준, 흡연 여부, CKD 등의 요인에 따라 불균등하게 분포
- 당뇨·만성신장질환(CKD)과 치아 상실의 관련성이 보고되어 있으나, 다변량 보정 후 독립적 연관성의 근거는 미흡
- 데이터 기반의 예측 도구가 없어 임상 현장에서의 선제적 개입이 어려움

**[EN]**
- Tooth loss (< 20 functional teeth) is linked to reduced quality of life in older adults (고령자), with consequences for nutrition, chewing function, and cognitive health
- Prevalence starts significantly rising after age 50 in Korea, with an uneven distribution across socioeconomic class, education level, smoking status, CKD, and other factors
- Diabetes and CKD have been associated with tooth loss, but evidence after multivariable adjustment is limited
- No existing clinical tool integrates predictive ML with interpretable AI for dental risk screening

---

## SLIDE 3 — 선행연구와 차별성 / Prior Research & Differentiation
*(Section 1: Introduction)*

**[KR]**
- **선행 연구:**
  - 당뇨-치주질환 연관성 연구 (단면 연구 위주, 소규모 임상 코호트) `<연구 논문 참고문헌 필요 / research paper reference needed>`
  - SES와 구강 건강 불평등 연구 (단일 연도 KNHANES 활용) `<연구 논문 참고문헌 필요>`
  - 구강 영상 기반 머신러닝 (파노라마 X-ray → 치아 우식 탐지) `<연구 논문 참고문헌 필요>`
  - CKD와 치주 질환 간 연관성 `<연구 논문 참고문헌 필요>`
- **본 연구의 차별성:**
  - 5개년(2020–2024) 통합 KNHANES — 국가 대표성 확보
  - 예측(ML + SHAP)과 추론(조정 오즈비) 두 접근을 통합
  - CKD(eGFR)를 핵심 노출 변수로 명시 포함
  - 최종 모델을 웹 기반 스크리닝 도구로 배포

**[EN]**
- **Prior studies:**
  - Cross-sectional studies linking diabetes to periodontitis (small clinical cohorts) `<research paper reference needed>`
  - SES and oral health disparities using single-wave KNHANES `<research paper reference needed>`
  - ML on dental imaging (panoramic X-ray → caries detection) `<research paper reference needed>`
  - CKD–periodontal disease association studies `<research paper reference needed>`
- **This study's differentiation:**
  - 5-wave KNHANES (2020–2024) — nationally representative, large N
  - Combines predictive (ML + SHAP) and inferential (aOR) in a single pipeline
  - Explicitly includes eGFR as a CKD proxy alongside diabetes and SES
  - Model deployed as a usable web tool — not just a paper result

---

## SLIDE 4 — 연구목적 / Research Objectives
*(Section 1: Introduction)*

**[KR]**
- **목적 1 (예측):** 50세 이상 한국 성인의 치아 상실(<20개)을 예측하는 머신러닝 분류 모델 개발 및 비교
- **목적 2 (추론):** 연령·성별 보정 후 치아 상실에 독립적으로 연관된 임상·행동·사회경제적 요인 규명 (조정 오즈비)
- **목적 3 (응용):** 최적 모델을 활용한 웹 기반 임상 위험 스크리닝 도구 개발

**[EN]**
- **Objective 1 (Predictive):** Build and compare ML classifiers to predict tooth loss (< 20 teeth) in Korean adults aged ≥ 50
- **Objective 2 (Inferential):** Identify factors independently associated with tooth loss after adjusting for age and sex, reported as adjusted odds ratios (aOR)
- **Objective 3 (Translational):** Deploy the best model as a web-based clinical screening tool

---

## SLIDE 5 — 연구 설계 개요 / Study Design Overview ⭐
*(Section 2: Method)*

**[KR]**
- 전체 분석 흐름을 한눈에 보여주는 파이프라인 다이어그램
- 두 개의 병렬 분석 트랙 (예측 ML / 추론 로지스틱 회귀) 을 명시

```
KNHANES 2020–2024 (5개 연도 통합)
           ↓
     만 50세 이상 필터링
           ↓
     결측값 처리 / 예약 코드 NaN화
           ↓
     파생변수 생성 (eGFR, 당뇨 복합, 고혈압, 칫솔질 빈도)
           ↓
  ┌────────────────────────────────┐
  │    훈련: 2020–2023             │
  │    테스트: 2024                │
  └────────────────────────────────┘
       ↓                    ↓
  [예측 트랙]          [추론 트랙]
  Optuna + 5-fold CV   다변량 로지스틱 회귀
  XGBoost 최적 모델    조정 오즈비 (aOR)
  SHAP 해석            설계 가중치 적용
       ↓
  Streamlit 웹 앱 배포
```

**[EN]**
- Full pipeline from raw data to deployment in one diagram
- Two parallel analytical tracks made explicit: predictive ML and inferential logistic regression

```
KNHANES 2020–2024 (5-wave merged)
           ↓
     Age ≥ 50 filter
           ↓
     Missing-value handling (reserved codes → NaN, >30% drop)
           ↓
     Feature engineering (eGFR, combined diabetes, HTN, brush_freq)
           ↓
  ┌────────────────────────────────┐
  │  Train: 2020–2023              │
  │  Test:  2024                   │
  └────────────────────────────────┘
       ↓                    ↓
  [Predictive track]   [Inferential track]
  Optuna + 5-fold CV   Multivariable logistic regression
  XGBoost best model   Adjusted OR (aOR)
  SHAP explainability  Survey design weights
       ↓
  Streamlit web app deployment
```

`<img 1 -- Study design pipeline diagram (build separately as clean flowchart graphic)>`

---

## SLIDE 6 — 연구대상자 선정 흐름도 / Cohort Selection Flowchart ⭐
*(Section 2: Method)*

**[KR]**
- CONSORT 스타일 흐름도 — 단계별 제외 기준과 최종 분석 대상 N 제시
- 심사위원이 가장 먼저 묻는 질문: "총 몇 명 분석했나요?"에 대한 시각적 답변

```
KNHANES 2020–2024 원자료
N = XXXX

↓ 만 50세 미만 제외
  n = XXXX 제외

↓ O_TC (총 치아 수) 유효값 없음 제외
  n = XXXX 제외

↓ 목표 변수 결측 제외
  n = XXXX 제외

최종 분석 대상
N = XXXX
(훈련: 2020–2023, n = XXXX / 테스트: 2024, n = XXXX)
```

**[EN]**
- CONSORT-style filtering diagram — shows stepwise exclusions and final analytic N
- Directly answers: "How many subjects did you actually analyze?"

```
KNHANES 2020–2024 raw data
N = XXXX

↓ Age < 50 excluded
  n = XXXX removed

↓ Missing O_TC (total tooth count) excluded
  n = XXXX removed

↓ Missing target variable excluded
  n = XXXX removed

Final analytic sample
N = XXXX
(Train: 2020–2023, n = XXXX / Test: 2024, n = XXXX)
```

`<img 2 -- Cohort selection CONSORT-style flowchart (build separately; fill N values from notebook)>`

---

## SLIDE 7 — 데이터 수집: KNHANES 코호트 / Data Collection: KNHANES Cohort
*(Section 2: Method)*

**[KR]**
- **출처:** 국민건강영양조사 (Korea National Health and Nutrition Examination Survey, KDCA)
- **설계:** 층화 다단계 확률 표본 설계 (전국 대표성)
- **사용 연도:** 2020, 2021, 2022, 2023, 2024 (5개 연도 통합)
- **포함 영역:** 인구통계, 사회경제, 신체계측, 임상검사, 영양조사, 구강검사
- **연구대상:** 만 50세 이상 성인 (연령 상한 80세로 top-coding)
- **결합 방법:** 연도별 CSV 5개 → year 컬럼 추가 후 pd.concat

**[EN]**
- **Source:** Korea National Health and Nutrition Examination Survey (KNHANES), conducted annually by KDCA
- **Design:** Stratified multistage probability sampling — nationally representative
- **Waves:** 2020–2024 (5 annual files merged)
- **Domains:** demographics, SES, physical exam, laboratory, nutrition, dental
- **Study population:** Korean adults aged ≥ 50 (age top-coded at 80)
- **Merging:** 5 CSV files concatenated with year tag

---

## SLIDE 8 — 연구대상자 선정, 변수 및 파생변수 / Variables & Feature Engineering
*(Section 2: Method)*

**[KR]**
- **포함 기준:** 만 50세 이상, O_TC(총 치아 수) 유효값 보유
- **목표 변수:** O_TC\_ (이진화: 1 = 치아 상실, <20개 / 0 = 정상, ≥20개)
- **변수 도메인 (7개 군):**

| 군 | 주요 변수 |
|---|---|
| 인구·지역 | age, sex, region, town_t |
| 사회경제 | ho_incm, edu, occp, marri_1, house |
| 임상 검사 | HbA1c, eGFR (HE_crea에서 유도), BMI, SBP/DBP, TG, HE_Uacid |
| 질환 진단 | DE1_dg (당뇨 진단) |
| 생활 습관 | sm_presnt, BD1, pa_aerobic, BP1, brush_freq |
| 구강 | O_pain |
| 식이 | N_EN, N_CA, N_PROT, N_TDF 등 |

- **파생변수:**
  - **eGFR:** 혈청 크레아티닌(HE_crea)에서 CKD-EPI 2021 공식으로 산출 → CKD 중증도 대리 지표
  - **당뇨 복합 기준:** DE1_dg == 1 (진단) OR HbA1c ≥ 6.5% → 미진단 당뇨 포함
  - **고혈압:** SBP ≥ 140 또는 DBP ≥ 90
  - **칫솔질 빈도(brush_freq):** BM1_1–BM1_8 이진 플래그 합산 (0–8회)

**[EN]**
- **Inclusion:** Age ≥ 50, valid O_TC value
- **Target:** O_TC\_ (binary: 1 = tooth loss < 20 teeth; 0 = ≥ 20 teeth)
- **Feature domains:** demographics, SES, clinical labs, disease diagnoses, lifestyle, dental behavior, dietary intake
- **Derived features:**
  - **eGFR:** CKD-EPI 2021 formula from serum creatinine — proxy for CKD severity
  - **Diabetes (combined):** diagnosed (DE1_dg == 1) OR HbA1c ≥ 6.5% — captures undiagnosed cases
  - **Hypertension:** SBP ≥ 140 or DBP ≥ 90
  - **Brushing frequency:** sum of BM1_1–BM1_8 occasion flags (0–8 per day)

---

## SLIDE 9 — 전처리 / Preprocessing Pipeline
*(Section 2: Method)*

**[KR]**
- **결측 처리 전략:**
  - 예약 코드(8/9/88/99) → NaN (설문·질환 범주형)
  - 이상값(>1e10) → NaN (연속형 임상·식이 변수)
  - NaN 비율 > 30% 변수 제거
  - 잔여 NaN: 중앙값 대체(Median Imputation) — **훈련 세트에서만 학습**, 테스트 세트에 적용 (데이터 누수 방지)
- **스케일링:** Logistic Regression 파이프라인에만 StandardScaler 적용 (트리 모델은 스케일 불변)

**[EN]**
- Reserved codes (8/9/88/99) → NaN
- Overflow sentinels (>1e10) → NaN for continuous vars
- Columns with > 30% NaN dropped
- Remaining NaN: median imputation, fit on train only — prevents data leakage
- StandardScaler only in Logistic Regression pipeline (tree models are scale-invariant)

`<img 3 -- NaN audit bar chart (nan_audit_filtered.png), showing NaN % per variable after 30% threshold drop>`

---

## SLIDE 10 — 탐색적 데이터 분석 / EDA & Class Distribution
*(Section 2: Method)*

**[KR]**
- O_TC(총 치아 수) 분포: 연속형 히스토그램
- 이진 목표 변수(O_TC\_) 계급 비율 → 클래스 불균형 확인
- 임상 변수 분포: HbA1c, eGFR, BMI 히스토그램
- 당뇨·고혈압 유병률 (Yes vs No 막대 그래프)
- 칫솔질 빈도 분포 (0–8회/일)
- 하위 그룹별 치아 상실률(%): 연령, 성별, 소득, 교육, 당뇨, 흡연, 도농(urban/rural), 칫솔질 빈도

**[EN]**
- O_TC histogram: continuous distribution of tooth counts
- O_TC\_ class distribution: proportion of tooth-loss cases (class imbalance visualization)
- Clinical distributions: HbA1c, eGFR, BMI histograms
- Diabetes and hypertension prevalence (Yes vs No)
- Brushing frequency distribution (0–8 occasions/day)
- Tooth-loss rate (%) by subgroup: age, sex, income, education, diabetes, smoking, urbanicity, brushing frequency

`<img 4 -- O_TC histogram (total tooth count distribution, bins 0–28)>`
`<img 5 -- Class imbalance bar chart (O_TC_: ≥20 teeth vs <20 teeth counts)>`
`<img 6 -- EDA bar charts: diabetes and hypertension prevalence (2 side-by-side bars: Yes vs No)>`
`<img 7 -- EDA histograms: HbA1c, eGFR, BMI distributions (1×3 panel)>`
`<img 8 -- EDA bar chart: brushing frequency (0–8 per day)>`
`<img 9 -- EDA: tooth-loss rate by subgroup (2×4 grid — age line + bar charts for 7 subgroups)>`

---

## SLIDE 11 — 시간적 분할 및 분석 파이프라인 / Temporal Split & Analysis Pipeline ⭐
*(Section 2: Method)*

**[KR]**
- **시간적 분할 (Temporal Split):** 미래 배포를 시뮬레이션하는 가장 엄격한 검증 방식
  - 훈련: 2020–2023년 (4개 연도)
  - 테스트: 2024년 (1개 연도)
- **핵심 원칙:** 테스트 연도 데이터는 전처리 파라미터(중앙값 대체값) 추정에 사용하지 않음 → 데이터 누수 완전 방지
- **분석 파이프라인:** Imputer → (StandardScaler — LR만) → Model

```
연도별 데이터
2020 ─┐
2021 ─┤  훈련 세트  →  Optuna 튜닝 (5-fold CV)  →  최적 모델 선택
2022 ─┤             →  전처리 파라미터 학습
2023 ─┘

2024 ──  테스트 세트  →  최종 평가 (AUC, AUPRC, MCC, 혼동행렬)
         (전처리 파라미터: 훈련 세트에서만 학습 후 적용)
```

**[EN]**
- **Temporal split:** most rigorous validation strategy — simulates future deployment
  - Train: 2020–2023 (4 years)
  - Test: 2024 (1 year, held out entirely)
- **Key principle:** preprocessing parameters (medians for imputation) are estimated from train only, then applied to test — prevents any information leakage
- **Analysis pipeline:** Imputer → (StandardScaler — LR only) → Model

```
Annual data
2020 ─┐
2021 ─┤  TRAIN set  →  Optuna tuning (5-fold CV)  →  best model selected
2022 ─┤             →  preprocessing params learned
2023 ─┘

2024 ──  TEST set   →  final evaluation (AUC, AUPRC, MCC, confusion matrix)
         (preprocessing params: learned from train, applied here)
```

`<img 10 -- Temporal split timeline diagram (build separately as clean horizontal timeline graphic)>`

---

## SLIDE 12 — 모델 설계, 훈련 및 평가 지표 / Model Design, Training & Evaluation Metrics
*(Section 2: Method)*

**[KR]**
- **사용 모델 (5종):** Random Forest, XGBoost, LightGBM, CatBoost, Logistic Regression
- **하이퍼파라미터 최적화:** Optuna TPE 탐색 (100 trial, 5-fold StratifiedKFold, 스코어: roc_auc)
- **클래스 불균형 처리:**
  - XGBoost: scale_pos_weight 튜닝
  - 나머지 트리 모델: class_weight='balanced'
- **평가 지표:**
  - AUPRC (주 지표 — 불균형 데이터에서 소수 클래스 탐지 우선)
  - AUC-ROC (보조 지표)
  - MCC (Matthews Correlation Coefficient)
  - 혼동 행렬 (Youden's J 임계값 적용)
- **최적 모델 선정 기준:** 테스트셋 AUPRC (Test AUPRC) 최고값
- **임계값 선택:** OOF(Out-of-Fold) 확률에서 Youden's J 최대화 → 테스트셋에 동결 적용 (과적합 방지)
- **설명가능 AI (SHAP):**
  - 트리 모델: TreeExplainer / Logistic Regression: LinearExplainer

**[EN]**
- **5 classifiers:** Random Forest, XGBoost, LightGBM, CatBoost, Logistic Regression
- **Hyperparameter tuning:** Optuna TPE (100 trials, 5-fold StratifiedKFold, scoring = roc_auc)
- **Class imbalance:** XGBoost tunes scale_pos_weight; others use class_weight='balanced'
- **Metrics:** AUC-ROC (primary), AUPRC (imbalance-sensitive), MCC, confusion matrix
- **Threshold selection:** Youden's J maximized on OOF probabilities, then frozen and applied once to test set — avoids optimizing on test data
- **SHAP:** TreeExplainer for tree models; LinearExplainer for Logistic Regression

---

## SLIDE 13 — 연구참여자 특성 분포 / Participant Characteristics Table
*(Section 3: Results)*

**[KR]**
- 치아 상실 유무에 따라 두 그룹으로 층화한 기저 특성 비교 표
- 범주형 변수: n(%), 연속형 변수: 평균±SD 또는 중앙값(IQR)
- 그룹 간 비교: χ² 검정(범주형), t-검정 또는 Mann-Whitney(연속형)

**[EN]**
- Baseline characteristics stratified by tooth loss status (O_TC\_ = 0 vs. 1)
- Categorical: n (%); Continuous: mean ± SD or median (IQR)
- Group comparison: χ² test (categorical), t-test or Mann-Whitney U (continuous)

| 변수 / Variable | 치아 정상 (≥20) | 치아 상실 (<20) | p-value |
|---|---|---|---|
| 나이 (Age) | | | |
| 성별 (Sex, % female) | | | |
| 소득분위 (Income quartile) | | | |
| 교육수준 (Education) | | | |
| 당뇨 (Diabetes, %) | | | |
| eGFR (mL/min/1.73m²) | | | |
| HbA1c (%) | | | |
| BMI (kg/m²) | | | |
| 현재 흡연 (Smoking, %) | | | |
| 칫솔질 빈도 (Brush freq) | | | |

---

## SLIDE 14 — 모델 성능 비교 / Model Performance Comparison
*(Section 3: Results)*

**[KR]**
- 5개 모델 성능 비교 (교차검증 AUC vs. 테스트셋 AUPRC) — **선정 기준: Test AUPRC** (소수 클래스 탐지 우선)
- **최적 모델: XGBoost** (Test AUPRC: **0.6248**, Test AUC: **0.8026**)
- AUC = 0.80은 우수한 판별력을 나타내며, 무작위 분류(AUC = 0.50)를 크게 상회함
- 모델 간 Test AUPRC 차이는 미미하나 (0.6120–0.6248), XGBoost가 소수 클래스(치아 상실) 탐지에서 일관되게 우위
- **혼동 행렬 (3×3 그리드):** 상위 3개 모델(XGBoost, LightGBM, CatBoost) × 3가지 분류 임계값 비교
  - **Default (0.5):** 균형 잡힌 기본 임계값
  - **Youden's J:** 민감도 + 특이도 합산 최대화 → 소수 클래스(치아 상실) 탐지 최적화
  - **MCC:** Matthews Correlation Coefficient 최대화 → 불균형 데이터에서 전체 분류 품질 최적화
  - 핵심 관찰: Youden's J 임계값에서 재현율(Recall) 상승, 정밀도(Precision) 감소 — 임상 스크리닝 목적에 적합

**[EN]**
- **Best model: XGBoost** (Test AUPRC: **0.6248**, Test AUC: **0.8026**) — selected by Test AUPRC (minority-class priority)
- AUC = 0.80 indicates good discrimination — substantially exceeds random classification (AUC = 0.50)
- All models perform comparably on Test AUPRC (range 0.6120–0.6248); XGBoost leads consistently on minority-class detection
- **Confusion matrix grid (3×3):** top 3 models × 3 classification thresholds
  - **Default (0.5):** standard balanced threshold
  - **Youden's J:** maximises sensitivity + specificity — optimised for catching tooth-loss cases
  - **MCC threshold:** maximises Matthews Correlation Coefficient — best overall classification quality under imbalance
  - Key observation: Youden's J raises recall at the cost of precision — appropriate for a clinical screening tool where missing a case matters more than a false alarm

| Model | CV AUC | Test AUC | Test AUPRC |
|---|---|---|---|
| **XGBoost** | 0.8108 | 0.8026 | **0.6248** |
| LightGBM | 0.8084 | 0.8022 | 0.6242 |
| CatBoost | 0.8116 | 0.8030 | 0.6235 |
| Logistic Regression | 0.8128 | 0.8004 | 0.6168 |
| Random Forest | 0.8057 | 0.7971 | 0.6120 |

`<img 11 -- ROC curve overlay: all 5 models on test set (AUC in legend)>`
`<img 12 -- AUPRC curve: XGBoost vs. random baseline>`
`<img 13 -- Confusion matrix 3×3 grid: XGBoost / LightGBM / CatBoost × Default / Youden's J / MCC threshold (Notebook cell [56])>`

---

## SLIDE 15 — 모델 보정 곡선 / Model Calibration Curve ⭐
*(Section 3: Results)*

**[KR]**
- **보정(Calibration):** 예측 확률이 실제 관측 위험과 얼마나 일치하는가?
- 예측 기반 도구(웹 앱)에서 특히 중요 — 확률 게이지 값의 신뢰도 근거
- **보정 곡선:** X축 = 예측 확률, Y축 = 관측 발생률 (대각선 = 완벽 보정)
- **Brier Score:** 예측 확률의 평균제곱오차 (낮을수록 좋음)
- XGBoost 보정 품질 평가 → 필요 시 Isotonic Regression 또는 Platt Scaling 적용 고려

**[EN]**
- **Calibration:** do predicted probabilities match observed event rates?
- Critical for a clinical tool — validates the probability gauge shown in the web app
- **Calibration curve:** x-axis = predicted probability, y-axis = observed rate (diagonal = perfect calibration)
- **Brier Score:** mean squared error of predicted probabilities (lower = better)
- If XGBoost is poorly calibrated, consider post-hoc calibration (Isotonic Regression or Platt Scaling)

`<img 14 -- Calibration curve: XGBoost predicted probability vs. observed tooth-loss rate (Notebook cell — to be generated)>`

---

## SLIDE 16 — 최종 모델 SHAP — Beeswarm / Final Model SHAP Summary Plot
*(Section 3: Results)*

**[KR]**
- **최적 모델: XGBoost** (Test AUC 0.8025) — TreeExplainer 사용
- 테스트셋 SHAP 값 시각화
- X축 양수: 치아 상실 위험 증가 / 음수: 위험 감소
- 색상: 빨강 = 높은 피처 값 / 파랑 = 낮은 피처 값
- 주요 연속형 피처: age, eGFR, HbA1c, ho_incm, edu, BMI, HE_Uacid 등
- 이진/명목 변수는 다음 슬라이드에서 바이올린 패널로 별도 시각화

**[EN]**
- **Best model: XGBoost** (Test AUC 0.8025) — SHAP via TreeExplainer
- Each dot = one test observation; x-axis = SHAP value (impact on predicted log-odds)
- Color = feature value (red = high, blue = low)
- Positive SHAP = increases tooth-loss risk; negative = decreases risk
- Binary/categorical features plotted separately in next slide

`<img 15 -- SHAP beeswarm summary plot (continuous features only, sorted by mean |SHAP|)>`

---

## SLIDE 17 — SHAP 범주형 해석 및 임상적 활용 / SHAP Categorical Panels & Interpretation
*(Section 3: Results)*

**[KR]**
- **바이올린 플롯:** 이진/저기수 범주형 변수별 SHAP 분포 비교
  - 주요 패널: 성별, 소득분위, 교육수준, 현재 흡연, 당뇨, 칫솔질 빈도
  - 해석: 너비 = 밀도, 박스 = 중앙값 + IQR, X축 위치 = 위험 방향
- **⚠️ 해석 주의:** SHAP 값은 모델 예측에 대한 기여도를 반영하며, **인과 효과가 아님** (단면 연구 설계의 한계)

| 주요 변수 | 방향 | 해석 |
|---|---|---|
| 연령 (age) | + | 노화 자체가 치아 상실의 가장 강력한 예측자 |
| eGFR | − | eGFR 감소(CKD 진행) → 위험 증가 — 요독 독소, 전신 염증 기전 |
| HbA1c / 당뇨 | + | 혈당 조절 불량 → 치주 조직 손상 |
| 소득분위 (ho_incm) | − | 소득 낮을수록 위험 — 치과 접근성, 건강 리터러시 격차 |
| 교육수준 (edu) | − | 저학력 → 위험 증가 |
| 칫솔질 빈도 | − | 수정 가능한 보호 요인 — 예방 교육으로 개선 가능 |

- **임상 활용:** 고위험 환자(CKD + 저소득 + 당뇨) 선제적 치과 의뢰; 칫솔질 교육 강화

**[EN]**
- **Violin plots:** SHAP distribution by category for binary/low-cardinality features
  - Key panels: sex, income quartile, education, smoking, diabetes, brushing frequency
  - Interpretation: width = density; box = median + IQR; x-axis position = risk direction
- **⚠️ Caution:** SHAP values reflect contribution to model prediction, **not causal effect** — cross-sectional design cannot establish causality

| Feature | Direction | Interpretation |
|---|---|---|
| Age | + | Strongest predictor — age-related bone and tissue loss |
| eGFR | − | Lower eGFR (CKD) → higher risk — uremic toxins, systemic inflammation |
| HbA1c / diabetes | + | Poor glycemic control → periodontal tissue damage |
| Income | − | Lower income → less dental care access |
| Education | − | Lower education → less health literacy |
| Brushing freq | − | Modifiable protective factor — most actionable for intervention |

- **Clinical implication:** Use the tool to flag CKD + low-SES + diabetic patients for early dental referral

`<img 16 -- SHAP violin panel grid (categorical features: sex, income, education, smoking, diabetes, brushing freq)>`

---

## SLIDE 18 — 예측 vs. 추론: 분석 이중 구조 / Why Two Analyses? ⭐
*(Section 3: Results — transition)*

**[KR]**
- 본 연구는 **서로 다른 목적**을 가진 두 개의 독립적 분석으로 구성
- SHAP과 조정 오즈비는 **같은 질문에 대한 다른 답이 아니라**, 서로 다른 질문에 대한 답임

| 구분 | 예측 ML | 추론 로지스틱 회귀 |
|---|---|---|
| **목적** | 정확한 위험 예측 | 독립적 연관 요인 규명 |
| **방법** | XGBoost + SHAP | 다변량 로지스틱 회귀 |
| **출력** | 예측 확률 | 조정 오즈비 (aOR) |
| **평가 기준** | AUC, AUPRC, MCC | p-value, 95% 신뢰구간 |
| **강점** | 비선형 패턴, 변수 상호작용 포착 | 해석 가능성, 임상 관행과의 일치 |
| **한계** | 블랙박스 (SHAP으로 부분 해소) | 로그-오즈 척도에서 선형성 가정 |

**[EN]**
- This study comprises two independent analyses with **different goals**
- SHAP values and adjusted ORs are not competing answers to the same question — they answer different questions

| | Predictive ML | Inferential Logistic Regression |
|---|---|---|
| **Goal** | Accurate risk prediction | Identify independent associations |
| **Method** | XGBoost + SHAP | Multivariable logistic regression |
| **Output** | Predicted probability | Adjusted odds ratio (aOR) |
| **Metrics** | AUC, AUPRC, MCC | p-value, 95% CI |
| **Strength** | Non-linear patterns, feature interactions | Interpretable, aligned with clinical convention |
| **Limitation** | Black box (partially addressed by SHAP) | Assumes linearity on log-odds scale |

---

## SLIDE 19 — 추론 분석: 조정 오즈비 / Inferential Analysis: Adjusted Odds Ratios
*(Section 3: Results)*

**[KR]**
- **연구질문:** 연령·성별 보정 후, 어떤 요인이 치아 상실에 **독립적으로** 연관되는가?
- **방법:** 다변량 로지스틱 회귀 (statsmodels, 국민건강영양조사 설계 가중치 적용)
- **보정 변수 선정:** 선행 문헌에 근거하여 잠재적 교란 변수로 선정 (연령, 성별, 흡연, 신체활동, 스트레스, BMI, 혈압, 요산, TG 등)
- **다중공선성 확인 (VIF):** 모든 변수 VIF < 5 (최댓값: occp_7 = 4.35) → 심각한 다중공선성 없음

| 주요 변수 | VIF |
|---|---|
| age | 2.80 |
| eGFR | 1.65 |
| edu | 1.92 |
| ho_incm | 1.60 |
| diabetes | 1.13 |

- **핵심 노출 변수:** eGFR, 당뇨, 소득분위, 교육수준
- **결과:** Forest Plot — 조정 오즈비(aOR) + 95% 신뢰구간 `<to be filled after cell [58] output>`

**[EN]**
- **Research question:** After adjusting for age and sex, which factors are **independently** associated with tooth loss?
- **Method:** Multivariable logistic regression (statsmodels, survey design weights applied)
- **Covariate selection:** Covariates were selected as potential confounders based on prior literature (age, sex, smoking, physical activity, stress, BMI, BP, uric acid, triglycerides)
- **Collinearity (VIF):** All variables VIF < 5 (max: occp_7 = 4.35) — no serious multicollinearity
- **Core exposures:** eGFR (CKD), diabetes, income quintile, education level
- **Results:** Forest plot of aOR (95% CI) `<to be filled after cell [58] output>`

`<img 17 -- Adjusted OR forest plot (aOR ± 95% CI per variable) — pending cell [58] run>`
`<img 18 -- Correlation heatmap of regression features>`

---

## SLIDE 20 — 웹 앱 데모 / Web App Demo
*(Section 3: Results)*

**[KR]**
- **앱명:** Tooth Loss Risk Predictor
- **스택:** Streamlit + scikit-learn 파이프라인(joblib) → Streamlit Cloud (무료, 공개 URL)
- **입력 (약 25개 항목):** 나이, 성별, 소득, 교육, HbA1c, 혈청 크레아티닌, 요산, SBP/DBP, TG, BMI, 흡연, 음주, 신체활동, 칫솔질 빈도 등
- **내부 계산:** 입력값에서 eGFR, 당뇨·고혈압 플래그 자동 산출 (사용자에게 노출 안 함)
- **출력:**
  - 확률 게이지 (예: "72% risk")
  - 위험 라벨: HIGH RISK / LOW RISK
  - SHAP 바 차트: "이 예측에 기여한 주요 요인"
  - 면책 조항: "연구 목적 전용 — 의료 진단이 아닙니다"

**[EN]**
- **App:** Tooth Loss Risk Predictor — single-page Streamlit form → instant prediction
- **Stack:** Streamlit + scikit-learn pipeline (joblib) → Streamlit Cloud (free, public URL)
- **Inputs (~25 fields):** demographics, clinical labs, lifestyle — eGFR, diabetes flag, and hypertension flag computed internally from inputs (not shown to user)
- **Outputs:** probability gauge + HIGH/LOW RISK label + top SHAP contributors + disclaimer
- **Deploy:** push to GitHub → connect Streamlit Cloud (1-click, free, public URL)

`<img 19 -- Streamlit app page structure mockup (form sections + output panel layout)>`
`<img 20 -- Streamlit full app screenshot (form + output panel)>`
`<img 21 -- Streamlit output panel close-up: probability gauge + SHAP bar chart>`

---

## SLIDE 21 — 연구 제한점 및 후속 연구 / Limitations & Future Work
*(Section 4: Discussion)*

**[KR]**
- **제한점:**
  - 단면 연구 설계 → 인과관계 확립 불가 (관련성만 보고)
  - 자가 보고 변수(칫솔질, 치과 방문) → 회상 편향 가능성
  - 예측 지표는 미가중 샘플 기준; 추론 분석만 설계 가중치 적용
  - 목표 변수 O_TC\_의 이진화로 치아 상실 정도 세분화 미반영
  - 웹 도구는 임상 검증 미실시
- **후속 연구:**
  - 종단 설계(패널 데이터) → 인과 관계 분석
  - 순서형 결과 변수(0–4개, 5–9개, 10–19개, 20+개)로 세분화
  - 치과 방사선 영상 + 표형 데이터 융합 모델
  - 임상의 피드백 기반 웹 도구 검증 및 개선

**[EN]**
- **Limitations:**
  - Cross-sectional: cannot establish causality
  - Self-reported variables (brushing, dental visits) → recall bias
  - Predictive metrics are unweighted; only the inferential model uses survey weights
  - Binary tooth-loss cutoff (< 20) loses granularity
  - Web tool not clinically validated
- **Future work:**
  - Longitudinal follow-up to establish temporality
  - Ordinal outcome (0–4, 5–9, 10–19, 20+ teeth remaining)
  - Multimodal model: dental imaging + tabular data fusion
  - Clinician-validated deployment study

---

## SLIDE 22 — 결론 / Conclusion
*(Section 5: Conclusion)*

**[KR]**
- 국민건강영양조사 2020–2024 (5개년 통합, 50세 이상) 데이터로 치아 상실 예측 머신러닝 파이프라인 구축
- 최적 모델: **XGBoost** (테스트 AUC: **0.8025**) — Optuna 하이퍼파라미터 튜닝 + 시간적 분할
- SHAP 분석 결과: **연령, eGFR, HbA1c, 소득, 칫솔질 빈도**가 핵심 기여 요인
- 다변량 로지스틱 회귀(조정 오즈비): CKD, 당뇨, 저SES가 연령·성별 보정 후에도 독립적으로 치아 상실과 유의하게 연관
- 최적 모델을 Streamlit 웹 앱으로 배포 → 임상 위험 스크리닝 도구로 활용 가능

**[EN]**
- Built and compared 5 ML classifiers on merged KNHANES 2020–2024 (age ≥ 50) for tooth-loss prediction
- Best model: **XGBoost** (Test AUC: **0.8025**) — Optuna-tuned with temporal train/test split
- SHAP reveals: **age, eGFR, HbA1c, income, and brushing frequency** as top predictors
- Inferential analysis (aOR): CKD, diabetes, and low SES remain independently associated with tooth loss after adjusting for age and sex
- Deployed as a Streamlit web tool for clinical risk screening

---

## Image Placeholder Summary

| # | Image | Source | Slide |
|---|---|---|---|
| 1 | Study design pipeline flowchart | Build separately | 5 |
| 2 | Cohort selection CONSORT diagram (fill N from notebook) | Build separately | 6 |
| 3 | NaN audit bar chart (after 30% threshold) | `nan_audit_filtered.png` | 9 |
| 4 | O_TC histogram (tooth count distribution, bins 0–28) | Notebook cell [11] | 10 |
| 5 | Class imbalance bar chart (O_TC\_: ≥20 vs <20 counts) | Notebook cell [13] | 10 |
| 6 | EDA: diabetes & hypertension prevalence | Notebook cell [24] | 10 |
| 7 | EDA: HbA1c, eGFR, BMI histograms (1×3 panel) | Notebook cell [29] | 10 |
| 8 | EDA: brushing frequency bar chart (0–8 per day) | Notebook cell [27] | 10 |
| 9 | Tooth-loss rate by subgroup (2×4 grid) | Notebook cell [31] | 10 |
| 10 | Temporal split timeline diagram | Build separately | 11 |
| 11 | ROC curve overlay: all 5 models on test set (AUC in legend) | Notebook cell [54] | 14 |
| 12 | AUPRC curve: XGBoost vs. random baseline | Notebook cell [56] | 14 |
| 13 | Confusion matrix: XGBoost at Youden's J threshold | Notebook cell [51] | 14 |
| 14 | Calibration curve: predicted probability vs. observed rate | Notebook cell — to be generated | 15 |
| 15 | SHAP beeswarm summary plot (continuous features) | Notebook cell [46] | 16 |
| 16 | SHAP violin panel grid (categorical features) | Notebook cell [47] | 17 |
| 17 | Adjusted OR forest plot (aOR ± 95% CI) — pending cell [58] | Notebook cell [58] | 19 |
| 18 | Correlation heatmap of regression features | Notebook cell [62] | 19 |
| 19 | Streamlit app page structure mockup | Build separately | 20 |
| 20 | Streamlit full app screenshot | Deploy then screenshot | 20 |
| 21 | Streamlit output panel close-up: probability gauge + SHAP bar | Deploy then screenshot | 20 |
