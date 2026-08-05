# KNHANES 9th Cycle (2022–2024) Variable Codebook

Translated/structured reference from _국민건강영양조사 원시자료 이용지침서 제9기(2022-2024)_, Section IV (변수설명서), pp. 93–236.

**Variable type key:** `C(n)` = character, length n · `N(n)` = numeric, n digits · `N(n.d)` = numeric, n digits with d decimal places.

---

## 1. Basic Variables (기본 변수)

| Variable    | Type    | Description                                                                                                                             | Codes / Values                                                                                                                                                                                                             |
| ----------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mod_d`     | C(12)   | Last DB modification date                                                                                                               | —                                                                                                                                                                                                                          |
| `ID`        | C(10)   | Individual ID                                                                                                                           | Survey district no. + housing unit no. + household member no.                                                                                                                                                              |
| `ID_fam`    | C(8)    | Household ID                                                                                                                            | Survey district no. + housing unit no.                                                                                                                                                                                     |
| `year`      | N(4)    | Survey year                                                                                                                             | —                                                                                                                                                                                                                          |
| `region`    | N(2)    | 17 metro/provincial regions                                                                                                             | 1 Seoul · 2 Busan · 3 Daegu · 4 Incheon · 5 Gwangju · 6 Daejeon · 7 Ulsan · 8 Sejong · 9 Gyeonggi · 10 Gangwon · 11 Chungbuk · 12 Chungnam · 13 Jeonbuk · 14 Jeonnam · 15 Gyeongbuk · 16 Gyeongnam · 17 Jeju               |
| `town_t`    | N(1)    | Dong/Eup-Myeon classification                                                                                                           | 1 Dong (urban) · 2 Eup·Myeon (rural)                                                                                                                                                                                       |
| `apt_t`     | N(1)    | Apartment classification                                                                                                                | 1 General housing · 2 Apartment                                                                                                                                                                                            |
| `psu`       | C(4)    | Primary sampling unit (survey district no.)                                                                                             | —                                                                                                                                                                                                                          |
| `sex`       | N(1)    | Sex                                                                                                                                     | 1 Male · 2 Female                                                                                                                                                                                                          |
| `age`       | N(3)    | Age (top-coded¹)                                                                                                                        | 1–79 = age in years · 80 = 80 years or older                                                                                                                                                                               |
| `age_month` | N(2)    | Age in months (ages 1–6)                                                                                                                | —                                                                                                                                                                                                                          |
| `incm`      | N(1)    | Income quartile (individual)                                                                                                            | 1 Low · 2 Mid-low · 3 Mid-high · 4 High (see threshold table in source)                                                                                                                                                    |
| `ho_incm`   | N(1)    | Income quartile (household)                                                                                                             | 1 Low · 2 Mid-low · 3 Mid-high · 4 High                                                                                                                                                                                    |
| `incm5`     | N(1)    | Income quintile (individual)                                                                                                            | 1 Low · 2 Mid-low · 3 Mid · 4 Mid-high · 5 High                                                                                                                                                                            |
| `ho_incm5`  | N(1)    | Income quintile (household)                                                                                                             | 1 Low · 2 Mid-low · 3 Mid · 4 Mid-high · 5 High                                                                                                                                                                            |
| `edu`       | N(1)    | Education level (recoded) — graduated classified by current level; completed/dropped-out/enrolled/on-leave classified by previous level | 1 ≤Elementary · 2 Middle school · 3 High school · 4 ≥College                                                                                                                                                               |
| `occp`      | N(1)    | Occupation (recoded) / unemployed–economically inactive status (excludes military)                                                      | 1 Manager/professional & related · 2 Office worker · 3 Service & sales · 4 Skilled agriculture/forestry/fishery · 5 Craft/machine operation/assembly · 6 Elementary occupation · 7 Not employed (homemaker, student, etc.) |
| `wt_hs`     | N(10.2) | Household survey weight                                                                                                                 | —                                                                                                                                                                                                                          |
| `wt_itvex`  | N(10.2) | Health interview + examination survey weight                                                                                            | —                                                                                                                                                                                                                          |
| `wt_oe`     | N(10.2) | Oral exam weight                                                                                                                        | —                                                                                                                                                                                                                          |
| `wt_bia`    | N(10.2) | Body composition exam weight (age 10+; 2022 only)                                                                                       | —                                                                                                                                                                                                                          |
| `wt_pft`    | N(10.2) | Pulmonary function exam weight (2024 only)                                                                                              | —                                                                                                                                                                                                                          |
| `wt_ntr`    | N(10.2) | Nutrition survey weight                                                                                                                 | —                                                                                                                                                                                                                          |
| `wt_tot`    | N(10.2) | Health interview–exam & nutrition combined weight                                                                                       | —                                                                                                                                                                                                                          |
| `wt_oent`   | N(10.2) | Oral exam & nutrition combined weight                                                                                                   | —                                                                                                                                                                                                                          |
| `wt_biant`  | N(10.2) | Body composition & nutrition combined weight (age 10+; 2022 only)                                                                       | —                                                                                                                                                                                                                          |
| `wt_pfnt`   | N(10.2) | Pulmonary function & nutrition combined weight (2024 only)                                                                              | —                                                                                                                                                                                                                          |
| `kstrata`   | N(3)    | Variance estimation stratum                                                                                                             | —                                                                                                                                                                                                                          |

¹ Top-coding de-identification applied. Income quartile/quintile threshold tables (by sex/age, in 만원) are in the source document but omitted here as they're reference tables, not variable codes.

_Basic variables are included in all HNYR_ALL / HNYR_24RC DBs._

---

## 2. Health Interview Survey (건강설문조사)

### 2-1. Household Survey (가구조사)

**Common household questions**

| Variable     | Type  | Description                                                | Codes / Values                                                                                                                                                                                                             |
| ------------ | ----- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cfam`       | N(1)  | Household member count¹                                    | 1–5 = 1–5 people · 6 = 6+ people · 9 = Unknown/no response                                                                                                                                                                 |
| `genertn`    | N(1)  | Household generation-composition code¹                     | 1 One-gen: single person · 2 One-gen: couple · 3 One-gen: other · 4 Two-gen: couple + unmarried children · 5 Two-gen: single parent + unmarried children · 6 Two-gen: other · 7 Three+ generations · 9 Unknown/no response |
| `allownc`    | N(2)  | Basic Livelihood Security recipient status¹                | 10 Has received (past or present) · 20 Never received · 99 Unknown/no response                                                                                                                                             |
| `house`      | N(1)  | Home ownership                                             | 1 No · 2 Owns 1 · 3 Owns 2+ · 9 Unknown/no response                                                                                                                                                                        |
| `live_t`     | N(1)  | Housing type                                               | 1 Single-family house · 2 Apartment · 3 Row house/multi-family dwelling · 4 Other · 9 Unknown/no response                                                                                                                  |
| `ainc_unit1` | N(1)  | Household total income (open-ended): unit                  | 1 Annual · 2 Monthly · 9 Unknown/no response                                                                                                                                                                               |
| `ainc_1`     | N(6)  | Household total income (open-ended): amount¹               | If annual: 200 = ≤2M KRW, 200–18000 continuous, 18000 = ≥180M KRW. If monthly: 17 = ≤170K KRW, 17–1500 continuous, 1500 = ≥15M KRW. 999999 = Unknown/no response                                                           |
| `ainc`       | N(6)* | Average monthly household total income¹ (derived variable) | 17 = ≤170K KRW, 17–1500 continuous, 1500 = ≥15M KRW                                                                                                                                                                        |

¹ De-identification applied: `cfam`, `genertn`, `allownc` are re-categorized; `ainc_1`/`ainc` use bottom- and top-coding. `*` = derived variable.

**Household-member questions**

| Variable   | Type   | Description                                        | Codes / Values                                                                                                                                                                                                                                    |
| ---------- | ------ | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `marri_1`  | N(1)   | Ever married                                       | 1 Married · 2 Never married · 9 Unknown/no response                                                                                                                                                                                               |
| `marri_2`  | N(2)   | Current marital status (asked only if `marri_1`=1) | 1 Has spouse, living together (incl. common-law) · 2 Has spouse, living apart (excl. temporary e.g. business travel) · 3 Widowed · 4 Divorced · 8 Refused · 9 Unknown · 88 Not applicable (i.e. answered "never married" to Q10) · 99 No response |
| `fam_rela` | N(2)   | Relationship to householder                        | 1 Self · 2 Spouse · 3 Child · 4 Child's spouse · 5 Grandchild · 6 Parent · 7 Grandparent · 8 Sibling · 9 Other relative · 10 Non-relative · 99 Unknown/no response                                                                                |
| `tins`     | N(2)   | Health insurance type                              | 10 National Health Insurance (regional) · 20 National Health Insurance (employer) · 30 Medical Aid · 99 Uninsured/unknown/no response                                                                                                             |
| `npins`    | N(1)   | Private health insurance enrollment                | 1 Yes · 2 No · 9 Unknown/no response                                                                                                                                                                                                              |
| `ID_F`     | C(10)* | Father's ID (derived)                              | —                                                                                                                                                                                                                                                 |
| `ID_M`     | C(10)* | Mother's ID (derived)                              | —                                                                                                                                                                                                                                                 |

> **Note for your research:** `marri_2` is only valid (non-missing/non-88) for respondents who answered "married" (`marri_1`=1). Values 3 (widowed) and 4 (divorced) are the two dissolution types; 1 vs 2 separates cohabiting from non-cohabiting spouse-present respondents. Codes 8/9/88/99 should be treated as missing/NA in modeling.

---

### 2-2. Morbidity / Chronic Disease History (이환)

**2-2-1. Self-rated health**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`D_1_1`|N(1)|Self-rated health status|1 Very good · 2 Good · 3 Fair · 4 Poor · 5 Very poor · 9 Unknown/no response|
|`D_2_1`|N(1)|Felt unwell in past 2 weeks|1 Yes · 2 No · 9 Unknown/no response|
|`D_2_wk`|N(2)|Days felt unwell in past 2 weeks|Days (00–14) · 88 N/A (`D_2_1`=No) · 99 Unknown/no response|

**2-2-2 through 2-2-16: Standard chronic-disease module pattern**

Most disease modules repeat the same 4 core variables (suffixes `_dg`, `_ag`, `_pr`, `_pt`) with the same code scheme:

| Suffix meaning                       | Standard codes                                                                           |
| ------------------------------------ | ---------------------------------------------------------------------------------------- |
| `_dg` = Ever diagnosed by a doctor   | 0 No · 1 Yes · 8 N/A (child/adolescent) · 9 Unknown/no response                          |
| `_ag` = Age at diagnosis (top-coded) | 0–79 = age in years · 80 = 80+ · 888 N/A (child/not diagnosed) · 999 Unknown/no response |
| `_pr` = Currently has the condition  | 0 No · 1 Yes · 8 N/A · 9 Unknown/no response                                             |
| `_pt` = Currently under treatment    | 0 No · 1 Yes · 8 N/A · 9 Unknown/no response                                             |

Disease-specific variable prefixes and deviations from the standard pattern:

| Disease (Korean)                     | Prefix | Variables present                                                                     | Notes / extra variables                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------ | ------ | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hypertension (고혈압)                   | `DI1`  | `DI1_dg, DI1_ag, DI1_pr, DI1_pt`                                                      | + `DI1_2` medication adherence: 1 Daily · 2 ≥20 days/mo · 3 ≥15 days/mo · 4 <15 days/mo · 5 Not taking · 8 N/A · 9 Unknown                                                                                                                                                                                                                                                      |
| Dyslipidemia (이상지질혈증)                | `DI2`  | `DI2_dg, DI2_ag, DI2_pr, DI2_pt`                                                      | + `DI2_2` medication adherence (same 5-point scale as `DI1_2`)                                                                                                                                                                                                                                                                                                                  |
| Diabetes (당뇨병)                       | `DE1`  | `DE1_dg, DE1_ag, DE1_pr, DE1_pt`                                                      | No `_pt`→simple; instead: `DE1_3` currently treating blood glucose (1 Yes·2 No·8 N/A·9 Unk); if yes, multi-select `DE1_31` insulin injection, `DE1_32` oral medication, `DE1_33` non-drug therapy, `DE1_34` other (0 No·1 Yes·8 N/A·9 Unk each), `DE1_35` (C50) other-specify text; `DE1_4` had eye exam (fundus) for diabetic complications in past year: 1 Yes·2 No·9 Unknown |
| Kidney disease (콩팥병/신장질환)            | `DN1`  | `DN1_dg, DN1_ag, DN1_pt`                                                              | No `_pr` variable. `DN1_ag`: 2022–2023 only. `DN1_pt`: 2024 only                                                                                                                                                                                                                                                                                                                |
| Stroke (뇌졸중)                         | `DI3`  | `DI3_dg, DI3_ag`                                                                      | 2024 only. + `DI3_2` sequelae: 1 Currently has sequelae · 2 Had sequelae, now recovered · 3 No notable sequelae · 8 N/A · 9 Unknown                                                                                                                                                                                                                                             |
| MI or angina combined (심근경색증 또는 협심증) | `DI4`  | `DI4_dg`* (derived combination variable)                                              | 0 No · 1 Yes · 8 N/A. 2024 only                                                                                                                                                                                                                                                                                                                                                 |
| Myocardial infarction (심근경색증)        | `DI5`  | `DI5_dg, DI5_ag`                                                                      | 2024 only                                                                                                                                                                                                                                                                                                                                                                       |
| Angina (협심증)                         | `DI6`  | `DI6_dg, DI6_ag`                                                                      | 2024 only                                                                                                                                                                                                                                                                                                                                                                       |
| Pulmonary TB (폐결핵)                   | `DJ2`  | `DJ2_dg, DJ2_ag`                                                                      | 2024 only                                                                                                                                                                                                                                                                                                                                                                       |
| Cancer (암)                           | `DC01` | `DC01_dg` (ever diagnosed), `DC01` (cancer type, multi-select), `DC01_tp1`, `DC01_ag` | Cancer type codes: 1 Stomach · 2 Liver · 3 Colorectal · 4 Breast · 5 Cervical · 6 Lung · 7 Thyroid (list continues — see full PDF p.109–111 for complete cancer type list beyond 7)                                                                                                                                                                                             |

| Disease (Korean)                    | Prefix    | Variables present                  | Notes / extra variables                                                                                                                                                                                                                                       |
| ----------------------------------- | --------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cancer type detail                  | —         | `DC01` (cancer type, multi-select) | 1 Stomach · 2 Liver · 3 Colorectal · 4 Breast · 5 Cervical · 6 Lung · 7 Thyroid · 8 Other · 9 Unknown/no response · 88 N/A (child/adolescent/not diagnosed). `DC01_tp1` C(50) = other cancer type free text. `DC01_ag` = diagnosis age (top-coded). 2024 only |
| Asthma (천식)                         | `DJ4`     | `DJ4_dg, DJ4_ag` (2022–2023 only)  | + `DJ4_3` medication/inhaler use for symptom control: 1 Regular treatment to prevent worsening · 2 Treatment only when symptomatic · 3 No treatment · 8 N/A · 9 Unknown (2022–2023 only)                                                                      |
| Atopic dermatitis (아토피피부염)          | `DL1`     | `DL1_dg, DL1_ag`                   | 2022–2023 only                                                                                                                                                                                                                                                |
| Allergic rhinitis (알레르기비염)          | `DJ8`     | `DJ8_dg, DJ8_ag`                   | 2022–2023 only                                                                                                                                                                                                                                                |
| Osteoporosis (골다공증)                 | `DM4`     | `DM4_dg, DM4_ag, DM4_pt`           | 2024 only                                                                                                                                                                                                                                                     |
| Sinusitis (부비동염)                    | `DJ6`     | `DJ6_dg, DJ6_ag`                   | 2022–2023 only                                                                                                                                                                                                                                                |
| Otitis media (중이염)                  | `DH4`     | `DH4_dg, DH4_ag`                   | 2022–2023 only                                                                                                                                                                                                                                                |
| Obstructive sleep apnea (폐쇄성수면무호흡증) | `BP17_dg` | `BP17_dg` only                     | 1 Yes · 0 No · 8 N/A (age <40) · 9 Unknown. Asked only of age 40+. 2022–2023 only                                                                                                                                                                             |

### 2-3. Healthcare Utilization (의료이용)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`M_2_yr`|N(1)|Unmet medical need in past year|1 Yes · 2 No · 3 Never needed care · 9 Unknown/no response|
|`M_2_rs`|N(2)|Reason for unmet need|1 No time · 2 Symptom seemed mild · 3 Financial reason · 4 Transportation/distance · 5 Didn't want to wait · 6 Hard to book appointment · 7 Afraid of treatment · 8 Other · 88 N/A · 99 Unknown/no response|
|`M_2_et`|C(50)|Unmet need reason: other, free text|—|
|`mt_nontrt`|N(1)*|Annual unmet-need rate indicator (derived)|0 Received care when needed · 1 Needed but did not receive|
|`M_HL_1`–`M_HL_10`|N(1)|Health literacy items 1–10 (2023–2024 only)|1 Not at all · 2 Not really · 3 Somewhat · 4 Very much · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`M_HL_S`|N(2)*|Health literacy total score (derived; sum of 10 items, "unknown"=9 recoded to 1 pt)|—|
|`M_HL_11`|N(1)|Health literacy: knowledge-type item (2023–2024 only)|1 Incorrect · 2 Incorrect · 3 Correct · 4 Incorrect · 8 N/A · 9 Unknown/no response|

### 2-4. Vaccination & Health Checkups (예방접종 및 건강검진)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BH9_11`|N(1)|Flu vaccination in past year|1 Yes · 2 No · 9 Unknown/no response|
|`BH1`|N(1)|Health checkup in past 2 years|1 Yes · 2 No · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`BH2_61`|N(1)|Cancer screening in past 2 years|1 Yes · 2 No · 8 N/A (child/adolescent) · 9 Unknown/no response|

---

### 2-5. Activity Limitation & Quality of Life (활동제한 및 삶의 질)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`LQ4_00`|N(1)|Activity limitation due to health problem/disability|1 Yes · 2 No · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`LQ4_01`–`LQ4_29`, `LQ4_23`|N(1)|Reason for activity limitation, multi-select (2022 & 2024 only). Reasons include: `_01` fracture/joint injury · `_02` other injury · `_03` arthritis/rheumatism · `_04` heart disease · `_05` respiratory/lung disease/asthma · `_06` stroke · `_07` diabetes · `_08` hypertension · `_09` back/neck problem · `_10` cancer · `_11` dental/oral disease · `_12` vision problem · `_13` hearing problem · `_14` dementia · `_15` depression/anxiety/emotional problem · `_16` intellectual disability · `_21` obesity · `_22` old age · `_25` kidney failure · `_26` dizziness · `_27` GI disorder · `_28` knee/leg pain (excl. arthritis) · `_29` headache · `_23` other|Each: 0 No · 1 Yes · 8 N/A (Q1=No or child) · 9 Unknown/no response|
|`LQ4_24`|C(70)|Activity limitation reason: other, free text|—|
|`LQ1_sb`|N(1)|Bedridden most of the day in past month|1 Yes · 2 No · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`LQ1_mn`|N(2)|Days bedridden in past month|Days · 88 N/A · 99 Unknown/no response|
|`LQ2_ab`|N(1)|Absent from work/school in past month due to illness/injury|1 Yes · 2 No · 8 N/A (not employed/enrolled) · 9 Unknown/no response|
|`LQ2_mn`|N(2)|Days absent in past month|Days · 88 N/A · 99 Unknown/no response|
|`LQ_1EQL`–`LQ_5EQL`|N(1)|EQ-5D dimensions (2022 & 2024 only): `_1` mobility · `_2` self-care · `_3` usual activities · `_4` pain/discomfort · `_5` anxiety/depression|1 No problem · 2 Some problem · 3 Severe problem/unable · 8 N/A · 9 Unknown/no response|
|`EQ5D`|N(4.3)*|EQ-5D health utility index (derived; weighted per KDCA 2007 valuation study)|Continuous index score|
|`LQ_1HT`–`LQ_8HT`|N(1)|HINT-8 quality-of-life items (2023 only): `_1` stairs · `_2` pain · `_3` energy · `_4` work ability · `_5` depression · `_6` memory · `_7` sleep · `_8` happiness|1 No difficulty / best · 2 Mild · 3 Severe · 4 Unable/worst · 8 N/A · 9 Unknown/no response|
|`LQ_LF1`–`LQ_LF10`|N(1)|LF-10 elderly functional scale items (2024 only, age 65+): `_1` rising from armless chair · `_2` standing on tiptoe · `_3` bending/crouching/kneeling · `_4` walking 400m · `_5` climbing one floor of stairs without rest · `_6` handling small objects · `_7` lifting ~5kg · `_8` bathing/showering · `_9` using public transit · `_10` participating in social activities|0 Cannot do at all · 1 Very difficult · 2 Moderately difficult · 3 Slightly difficult · 4 Not difficult at all · 8 N/A (age <65) · 9 Unknown/no response|
|`LQ_LF_S`|N(2)*|LF-10 total score (derived; sum of 10 items, scaled to 100)|—|

### 2-6. Injury (Accidents & Poisoning) (손상)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`AC1_yr`|N(1)|Injury requiring treatment in past year|1 Yes · 2 No · 9 Unknown/no response|
|`AC3`|N(2)|Number of injury episodes (max 3 in 2022–2023, max 6 in 2024)|Count · 88 N/A · 99 Unknown/no response|
|`AC3_1_01`–`_06`|N(4)|Injury 1–6 occurrence: year|Year · 9999 Unknown|
|`AC3_2_01`–`_06`|N(2)|Injury 1–6 occurrence: month|Month · 99 Unknown|
|`AC8_1_01`–`_06`|N(1)|Injury 1–6 treatment location|1 ER · 2 Outpatient only · 3 Hospitalized · 4 Other · 9 Unknown|
|`AC8_1e_01`–`_06`|C(50)|Injury 1–6 treatment: other, free text|—|
|`AC8_2w_01`–`_06`|N(1)|Injury 1–6 bedridden most of day|1 Yes · 2 No · 9 Unknown|
|`AC8_2_01`–`_06`|N(3)|Injury 1–6 days bedridden|Days · 888 N/A · 999 Unknown|
|`AC8_3w_01`–`_06`|N(1)|Injury 1–6 absent from work/school|1 Yes · 2 No · 8 Not employed/enrolled · 9 Unknown|
|`AC8_3_01`–`_06`|N(3)|Injury 1–6 days absent|Days · 888 N/A · 999 Unknown|
|`ij_expr`|N(1)*|Annual injury experience rate (derived)|0 No injury in past year · 1 Had injury in past year|

### 2-7. Hospitalization & Outpatient Use (입원 및 외래이용)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`MH1_yr`|N(1)|Hospitalized in past year|1 Yes · 2 No · 9 Unknown/no response|
|`MH1_1`|N(2)|Number of hospitalizations|Count · 88 N/A · 99 Unknown/no response|
|`MO1_wk`|N(1)|Outpatient visit (incl. dental) in past 2 weeks|1 Yes · 2 No · 9 Unknown/no response|
|`MO1_1`|N(2)|Number of outpatient visits in past 2 weeks|Count · 88 N/A · 99 Unknown/no response|

### 2-8. Education (교육)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`educ`|N(2)|Education level attained (adults/adolescents)|1 Seodang/classical study · 2 No formal education · 3 Elementary · 4 Middle school · 5 High school · 6 2–3yr college · 7 4yr university · 8 Graduate school · 88 N/A (child) · 99 Unknown/no response|
|`graduat`|N(1)|Completion status of that level|1 Graduated · 2 Completed · 3 Dropped out · 4 Currently enrolled/on leave · 8 N/A · 9 Unknown/no response|
|`EC_pedu_1`|N(2)|Childhood environment: father's education (asked of age 19–64)|1 None · 2 Seodang · 3 ≤Elementary · 4 ≤Middle school · 5 ≤High school · 6 ≤2-3yr college · 7 ≤4yr university · 8 ≥Graduate school · 88 N/A (age <19 or ≥65) · 99 Unknown/no response|
|`EC_pedu_2`|N(2)|Childhood environment: mother's education|Same coding as `EC_pedu_1`|
|`CH2_1`|N(1)|Education level (children)|1 Kindergarten/daycare · 2 Elementary · 3 Not yet enrolled/none · 8 N/A (adult/adolescent) · 9 Unknown/no response|
|`CH2_2`|N(1)|Completion status (children)|1 Graduated · 2 Completed · 3 Dropped out · 4 Enrolled/on leave · 8 N/A · 9 Unknown/no response|

### 2-9. Economic Activity (경제활동)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`EC1_1`|N(1)|Employment status|1 Yes (employed) · 2 No (unemployed/economically inactive) · 8 N/A (age <15) · 9 Unknown/no response|
|`EC_occp`|N(2)|Occupation, Korean Standard Classification (7th rev.) major category|1 Manager · 2 Professional/related · 3 Office worker · 4 Service worker · 5 Sales worker · 6 Skilled agriculture/forestry/fishery · 7 Craft/related trades · 8 Machine operator/assembler · 9 Elementary occupation · 10 Military · 88 N/A · 99 Unknown/no response|
|`EC_stt_1`|N(1)|Employment status type|1 Wage worker · 2 Self-employed, no employees · 3 Self-employed, with employees · 4 Unpaid family worker · 8 N/A · 9 Unknown/no response|
|`EC_stt_2`|N(1)|Wage worker detail|1 Regular/permanent · 2 Temporary · 3 Daily · 8 N/A · 9 Unknown/no response|
|`EC_wht_0`|N(1)|Regular vs. non-regular employment|1 Regular (tenured) · 2 Non-regular (fixed-term/atypical/dispatched/part-time/subcontract) · 8 N/A · 9 Unknown/no response|
|`EC_wht_23`|N(3)|Average weekly work hours|Hours · 888 N/A (did not work in past year) · 999 Unknown/no response|
|`EC_wht_5`|N(1)|Work shift/schedule type|1 Daytime · 2 Evening (14:00–24:00) · 3 Night (21:00–08:00) · 4 Regular day/night rotation · 5 24-hr rotation · 6 Split shift (2+ periods/day) · 7 Irregular rotation · 8 Other · 88 N/A · 99 Unknown/no response|
|`EC_wht_6`|C(50)|Shift type: other, free text|—|
|`EC_lgw_2`|N(2)|Longest-held job: occupation major category (+ unemployed/inactive status)|Same 10-category coding as `EC_occp`; 88 N/A (age <19 or unemployed/inactive) · 99 Unknown/no response|
|`EC_lgw_4`|N(1)|Longest-held job: employment status type|1 Wage worker · 2 Self-employed, no employees · 3 Self-employed, with employees · 4 Unpaid family worker · 8 N/A · 9 Unknown/no response|
|`EC_lgw_5`|N(1)|Longest-held job: wage worker detail|1 Regular · 2 Temporary · 3 Daily · 8 N/A · 9 Unknown/no response|

### 2-10. Obesity & Weight Control (비만 및 체중조절)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BO1`|N(1)|Self-perceived body shape|1 Very thin · 2 Somewhat thin · 3 Average · 4 Somewhat obese · 5 Very obese · 8 N/A (age <6) · 9 Unknown/no response|
|`BO1_1`|N(1)|Weight change in past year|1 No change · 2 Weight loss · 3 Weight gain · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`BO1_2`|N(1)|Amount of weight lost|1 3–<6 kg · 2 6–<10 kg · 3 ≥10 kg · 8 N/A · 9 Unknown/no response|
|`BO1_3`|N(1)|Amount of weight gained|1 3–<6 kg · 2 6–<10 kg · 3 ≥10 kg · 8 N/A · 9 Unknown/no response|
|`BO2_1`|N(1)|Weight control effort in past year|1 Tried to lose weight · 2 Tried to maintain weight · 3 Tried to gain weight · 4 No effort made · 8 N/A (age <6) · 9 Unknown/no response|
|`BO3_01, _02, _03, _14, _05, _04, _12, _07, _09, _10`|N(1)|Weight control methods used (multi-select, 2022 only): `_01` exercise · `_02` fasting ≥24h · `_03` reduced food intake · `_14` skipping meals · `_05` non-prescription weight-loss drugs · `_04` prescribed weight-loss drugs · `_12` herbal medicine · `_07` health functional foods · `_09` one-food diet · `_10` other|0 No · 1 Yes · 8 N/A · 9 Unknown/no response|
|`BO3_11`|C(50)|Weight control method: other, free text|—|

### 2-11. Alcohol (음주)

| Variable       | Type  | Description                                                                                                                                                                                      | Codes / Values                                                                                                                            |
| -------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `BD1`          | N(1)  | Lifetime drinking experience (≥1 full drink, excl. ceremonial sips)                                                                                                                              | 1 Never · 2 Yes · 8 N/A (child) · 9 Unknown/no response                                                                                   |
| `BD2`          | N(3)  | Age at first full drink¹                                                                                                                                                                         | 0–79 = age · 80 = 80+ · 888 N/A · 999 Unknown/no response                                                                                 |
| `BD1_11`       | N(1)  | Drinking frequency in past year                                                                                                                                                                  | 1 Not at all in past year · 2 <1×/month · 3 ~1×/month · 4 2–4×/month · 5 2–3×/week · 6 ≥4×/week · 8 N/A · 9 Unknown/no response           |
| `BD2_1`        | N(1)  | Amount per drinking occasion (standard drinks)                                                                                                                                                   | 1 1–2 · 2 3–4 · 3 5–6 · 4 7–9 · 5 ≥10 · 8 N/A · 9 Unknown/no response                                                                     |
| `BD2_14`       | N(3)  | Amount per occasion, exact count (if `BD2_1`=5)                                                                                                                                                  | Drinks · 888 N/A · 999 Unknown/no response                                                                                                |
| `BD2_31`       | N(1)  | Binge drinking frequency (≥7 drinks/occasion)                                                                                                                                                    | 1 Never · 2 <1×/month · 3 ~1×/month · 4 ~1×/week · 5 Almost daily · 8 N/A · 9 Unknown/no response                                         |
| `BD2_32`       | N(1)  | Binge drinking frequency, women only (≥5 drinks/occasion)                                                                                                                                        | 1 Never · 2 <1×/month · 3 ~1×/month · 4 ~1×/week · 5 Almost daily · 8 N/A (question 1=No, male, child/adolescent) · 9 Unknown/no response |
| `BD7_4`        | N(1)  | Family/doctor advised reducing drinking                                                                                                                                                          | 1 Never · 2 In the past but not in the last year · 3 Yes, in the past year · 8 N/A · 9 Unknown/no response                                |
| `BD7_5`        | N(1)  | Sought counseling for drinking problem in past year (adults)                                                                                                                                     | 1 Yes · 2 No · 8 N/A (child/adolescent) · 9 Unknown/no response                                                                           |
| `BD7_61`–`_66` | N(1)  | Harmed by others' drinking in past year, multi-select: `_61` disturbance · `_62` assault · `_63` sexual harassment · `_64` work/daily-life accident · `_65` drunk-driving accident · `_66` other | 0 No · 1 Yes · 8 N/A (child) · 9 Unknown/no response                                                                                      |
| `BD7_67`       | C(50) | Harm from others' drinking: other, free text                                                                                                                                                     | —                                                                                                                                         |
| `dr_month`     | N(1)* | Monthly drinking rate indicator (derived)                                                                                                                                                        | 0 Lifetime abstainer or <1×/month in past year · 1 ≥1×/month in past year                                                                 |

¹ Top-coding de-identification applied to `BD2`.

### 2-12. Safety Consciousness (안전의식)

**Adults**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BA2_12`|N(1)|Seatbelt use while driving|1 Never · 2 Rarely · 3 Sometimes · 4 Usually · 5 Always · 8 N/A (doesn't drive/child) · 9 Unknown/no response|
|`BA2_13`|N(1)|Seatbelt use, front passenger seat|1 Never · 2 Rarely · 3 Sometimes · 4 Usually · 5 Always · 8 N/A (never in front seat/child) · 9 Unknown/no response|
|`BA2_14`|N(1)|Seatbelt use, back seat|1 Never · 2 Rarely · 3 Sometimes · 4 Usually · 5 Always · 8 N/A (never in back seat/child) · 9 Unknown/no response|
|`BA2_2_1`|N(1)|Drunk driving in past year: bicycle|1 Yes · 2 No · 8 N/A (doesn't ride/child) · 9 Unknown/no response|
|`BA2_2_2`|N(3)|Drunk driving frequency: bicycle|Count · 888 N/A · 999 Unknown/no response|
|`BA2_2_3`|N(1)|Drunk driving in past year: motorcycle|Same codes as `BA2_2_1`|
|`BA2_2_4`|N(3)|Drunk driving frequency: motorcycle|Same codes as `BA2_2_2`|
|`BA2_2_5`|N(1)|Drunk driving in past year: car|Same codes as `BA2_2_1`|
|`BA2_2_6`|N(3)|Drunk driving frequency: car|Same codes as `BA2_2_2`|
|`BA2_22`|N(1)|Rode with a drunk driver in past year, frequency|1 None · 2 Once · 3 2–3× · 4 4–5× · 5 ≥6× · 8 N/A (child) · 9 Unknown/no response|

**Children**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BA1_1`|N(1)|Frequency riding in front car seat|1 Always · 2 Often · 3 Sometimes · 4 Rarely · 5 Never · 6 Rarely in cars · 8 N/A (adult/adolescent) · 9 Unknown/no response|
|`BA1_3`|N(1)|Bike helmet use in past year|1 Always · 2 Often · 3 Sometimes · 4 Rarely · 5 Never · 8 N/A (doesn't bike/adult/adolescent) · 9 Unknown/no response|
|`BA1_2`|N(1)|Car safety device use (car seat/booster), age <6 only|1 Always · 2 Often · 3 Sometimes · 4 Rarely · 5 Never · 6 Not put in car · 8 N/A (age 6+) · 9 Unknown/no response|
|`sc_seatblt`|N(1)*|Always-wear-seatbelt-while-driving rate (derived)|0 Not always · 1 Always|
|`sc_seatblt2`|N(1)*|Always-wear-seatbelt front-passenger rate (derived)|0 Not always · 1 Always|
|`sc_seatblt3`|N(1)*|Always-wear-seatbelt back-seat rate (derived)|0 Not always · 1 Always|

### 2-13. Sleep Health (수면건강)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BP16_1`|N(2)|Average sleep hours, weekday/workday (age 12+, 2022–2023 only)|Hours · 88 N/A (child) · 99 Unknown/no response|
|`BP16_2`|N(2)|Average sleep hours, weekend/non-workday (age 12+, 2022–2023 only)|Hours · 88 N/A · 99 Unknown/no response|
|`BP16_11` / `_12`|N(2)|Weekday bedtime: hour / minute (age 12+, 2024 only)|Value · 88 N/A · 99 Unknown/no response|
|`BP16_13` / `_14`|N(2)|Weekday wake time: hour / minute (2024 only)|Value · 88 N/A · 99 Unknown/no response|
|`BP16_21` / `_22`|N(2)|Weekend bedtime: hour / minute (2024 only)|Value · 88 N/A · 99 Unknown/no response|
|`BP16_23` / `_24`|N(2)|Weekend wake time: hour / minute (2024 only)|Value · 88 N/A · 99 Unknown/no response|
|`BP17_2`|N(1)|OSA risk factor: loud snoring (age 40+, 2022–2023 only)|1 Yes · 2 No · 8 N/A (age <40) · 9 Unknown/no response|
|`BP17_3`|N(1)|OSA risk factor: daytime fatigue/sleepiness|Same codes as `BP17_2`|
|`BP17_4`|N(1)|OSA risk factor: witnessed breathing pauses during sleep|Same codes as `BP17_2`|

### 2-14. Mental Health (정신건강)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BP_PHQ_1`–`_9`|N(1)|PHQ-9 depression screening items 1–9 (2022 & 2024 only)|0 Not at all · 1 Several days · 2 More than a week · 3 Nearly every day · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`mh_PHQ_S`|N(2)*|PHQ-9 total score (derived; sum of 9 items)|—|
|`BP_GAD_1`–`_7`|N(1)|GAD-7 anxiety screening items 1–7|0 Not at all · 1 Several days · 2 More than 7 days · 3 Nearly every day · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`mh_GAD_S`|N(2)*|GAD-7 total score (derived; sum of 7 items)|—|
|`BP1`|N(1)|Perceived stress level|1 Extremely high · 2 High · 3 A little · 4 Rarely/none · 8 N/A (child) · 9 Unknown/no response|
|`BP2`|N(2)|Main source of stress (2024 only)|1 Financial · 2 Work (incl. workplace relationships) · 3 Parent-child issues · 4 Spouse issues · 5 Living environment/housing · 6 Employment/career · 7 Own health · 8 Family health · 9 Other · 88 N/A · 99 Unknown/no response|
|`BP2_2`|C(50)|Stress source: other, free text (2024 only)|—|
|`BP5`|N(1)|≥2 consecutive weeks of sadness/hopelessness in past year|1 Yes · 2 No · 8 N/A (child; N/A for all adults too in 2022/2024) · 9 Unknown/no response|
|`BP6_10`|N(1)|Seriously considered suicide in past year|1 Yes · 2 No · 8 N/A (child; N/A for all in 2024) · 9 Unknown/no response|
|`BP6_2`|N(1)|Made a specific suicide plan in past year|1 Yes · 2 No · 8 N/A (child) · 9 Unknown/no response|
|`BP6_31`|N(1)|Attempted suicide in past year|1 Yes · 2 No · 8 N/A (child) · 9 Unknown/no response|
|`BP7`|N(1)|Sought counseling for mental health in past year|1 Yes · 2 No · 8 N/A (child) · 9 Unknown/no response|
|`mh_stress`|N(1)*|High-stress-perception rate indicator (derived)|0 Low stress (BP1=3 or 4) · 1 High stress (BP1=1 or 2)|

### 2-15. Smoking (흡연)

**Conventional cigarettes**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BS1_1`|N(1)|Lifetime cigarette smoking amount|1 <5 packs (100 sticks) · 2 ≥5 packs · 3 Never smoked · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`BS2_1`|N(3)|Age started smoking (top-coded)¹|0–79 age · 80 = 80+ · 888 N/A (never smoked) · 999 Unknown/no response|
|`BS2_2`|N(3)|Age started smoking daily (2024 only)¹|Same coding as `BS2_1`|
|`BS3_1`|N(1)|Current smoking status|1 Daily · 2 Occasionally · 3 Former smoker, quit · 8 N/A · 9 Unknown/no response|
|`BS3_2`|N(3)|Average daily cigarette count|Sticks · 888 N/A · 999 Unknown/no response|
|`BS3_3`|N(2)|Days smoked in past month (occasional smokers)|Days · 88 N/A · 99 Unknown/no response|
|`BS6_2`|N(4)*|Former smoker: total smoking duration in months (derived)|Months · 8888 N/A · 9999 Unknown/no response|
|`BS6_2_1` / `_2`|N(2)|Former smoker: smoking duration, years / months|Value · 88 N/A · 99 Unknown/no response|
|`BS6_3`|N(3)|Former smoker: average daily cigarette count|Sticks · 888 N/A · 999 Unknown/no response|
|`BS6_4`|N(4)*|Former smoker: time since quitting, months (derived)|Months · 8888 N/A · 9999 Unknown/no response|
|`BS6_4_1` / `_2`|N(2)|Former smoker: time since quitting, years / months|Value · 88 N/A · 99 Unknown/no response|

**Heated tobacco / e-cigarettes**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BS12_37`|N(1)|Ever used heated tobacco (IQOS, glo, lil, etc.)|1 Yes · 2 No · 8 N/A (child) · 9 Unknown/no response|
|`BS12_47`|N(1)|Current heated-tobacco use|1 Daily · 2 Occasionally · 3 Former user · 8 N/A · 9 Unknown/no response|
|`BS12_47_1`|N(3)|Average daily heated-tobacco sticks|Sticks · 888 N/A · 999 Unknown/no response|
|`BS12_47_2`|N(2)|Days used in past month (occasional users)|Days · 88 N/A · 99 Unknown/no response|
|`BS12_47_4`|N(1)|Reason for using heated tobacco (2023 only)|1 Seemed less harmful · 2 Thought it'd help quit smoking · 3 Can use indoors · 4 No cigarette smell · 5 Less secondhand smoke harm to others · 6 Can hide being a smoker · 7 No ash · 8 Curiosity · 9 Other · 88 N/A · 99 Unknown/no response|
|`BS12_47_5`|C(50)|Reason for heated tobacco use: other, free text|—|
|`BS12_1`|N(1)|Ever used nicotine e-cigarette (vape)|1 Yes · 2 No · 8 N/A (child) · 9 Unknown/no response|
|`BS12_2`|N(1)|Used vape in past month|1 Yes · 2 No · 8 N/A · 9 Unknown/no response|
|`BS12_31`–`_34`, `_36`|N(1)|Lifetime use of other tobacco types, multi-select: `_31` snus · `_32` hookah/waterpipe · `_33` cigar · `_34` other · `_36` never used|0 No · 1 Yes · 8 N/A (child) · 9 Unknown/no response|
|`BS12_35`|C(50)|Other tobacco type: free text|—|
|`BS12_41`–`_44`, `_46`|N(1)|Past-month use of other tobacco types (same categories as above)|0 No · 1 Yes · 8 N/A (child/never smoked) · 9 Unknown/no response|
|`BS12_45`|C(50)|Other tobacco type, current use: free text|—|

**Nicotine dependence & cessation (all tobacco types combined)**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BS5_4`|N(1)|Time to first cigarette after waking (nicotine dependence, 2022 only)|1 ≤5 min · 2 6–30 min · 3 31min–1hr · 4 >1hr · 8 N/A (never used any tobacco) · 9 Unknown/no response|
|`BS5`|N(1)|Attempted to quit for ≥24hrs in past year|1 Yes · 2 No · 8 N/A · 9 Unknown/no response|
|`BS5_1`|N(1)|Plan to quit within 1 month|1 Plan within 1 month · 2 Plan within 6 months · 3 Considering eventually, not within 6mo · 4 No intention to quit · 8 N/A · 9 Unknown/no response|
|`BS5_21, _28, _26, _33, _34, _32, _29, _30`|N(1)|Cessation method used, multi-select (2022 only): `_21` willpower alone · `_28` quitline · `_26` public health center clinic · `_33` self-purchased NRT at pharmacy · `_34` NRT via clinic/prescription · `_32` internet resources · `_29` other · `_30` never tried to quit|0 No · 1 Yes · 8 N/A · 9 Unknown/no response|
|`BS5_31`|C(50)|Cessation method: other, free text|—|

**Secondhand smoke exposure (all respondents)**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BS8_2`|N(1)|Secondhand smoke exposure at work (indoor, past week)|1 Yes · 2 No · 8 N/A (not employed/child) · 9 Unknown/no response|
|`BS9_2`|N(1)|Secondhand smoke exposure at home (indoor, past week)|1 Yes · 2 No · 3 No household smoker · 8 N/A (child) · 9 Unknown/no response|
|`BS13`|N(1)|Secondhand smoke exposure in public indoor spaces (past week)|1 Yes · 2 No · 8 N/A (child) · 9 Unknown/no response|

**Adolescents**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BS10_1`|N(1)|Ever tried even a puff of a cigarette|1 Never · 2 Yes · 8 N/A (adult/child) · 9 Unknown/no response|
|`BS2`|N(3)|Age of first puff|Age · 888 N/A · 999 Unknown/no response|
|`BS10_2`|N(2)|Days smoked in past month|Days (0 = none) · 88 N/A · 99 Unknown/no response|
|`BS10_3`|N(3)|Average daily cigarettes on smoking days, past month|Sticks · 888 N/A · 999 Unknown/no response|
|`sm_presnt`|N(1)*|Current smoking rate indicator (derived; ≥5 packs lifetime + currently smoking, age 19+)|0 Former/never smoker · 1 Current smoker|

### 2-16. Physical Activity (신체활동)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BE3_71`|N(1)|Work-related vigorous activity ≥10min|1 Yes · 2 No · 8 N/A (child) · 9 Unknown/no response|
|`BE3_72`|N(1)|Days/week: work vigorous activity|Days · 8 N/A · 9 Unknown/no response|
|`BE3_73` / `_74`|N(2)|Daily duration: work vigorous activity, hours/minutes|Value · 88 N/A · 99 Unknown/no response|
|`BE3_81`|N(1)|Work-related moderate activity ≥10min|1 Yes · 2 No · 8 N/A · 9 Unknown/no response|
|`BE3_82`|N(1)|Days/week: work moderate activity|Days · 8 N/A · 9 Unknown/no response|
|`BE3_83` / `_84`|N(2)|Daily duration: work moderate activity, hours/minutes|Value · 88 N/A · 99 Unknown/no response|
|`BE3_91`|N(1)|Active transport (walk/bike) ≥10min|1 Yes · 2 No · 8 N/A · 9 Unknown/no response|
|`BE3_92`|N(1)|Days/week: active transport|Days · 8 N/A · 9 Unknown/no response|
|`BE3_93` / `_94`|N(2)|Daily duration: active transport, hours/minutes|Value · 88 N/A · 99 Unknown/no response|
|`BE3_75`|N(1)|Leisure-time vigorous activity ≥10min|1 Yes · 2 No · 8 N/A · 9 Unknown/no response|
|`BE3_76`|N(1)|Days/week: leisure vigorous activity|Days · 8 N/A · 9 Unknown/no response|
|`BE3_77` / `_78`|N(2)|Daily duration: leisure vigorous activity, hours/minutes|Value · 88 N/A · 99 Unknown/no response|
|`BE3_85`|N(1)|Leisure-time moderate activity ≥10min|1 Yes · 2 No · 8 N/A · 9 Unknown/no response|
|`BE3_86`|N(1)|Days/week: leisure moderate activity|Days · 8 N/A · 9 Unknown/no response|
|`BE3_87` / `_88`|N(2)|Daily duration: leisure moderate activity, hours/minutes|Value · 88 N/A · 99 Unknown/no response|
|`BE8_1` / `_2`|N(2)|Average daily sedentary time, hours/minutes|Value · 88 N/A (child) · 99 Unknown/no response|
|`BE3_31`|N(2)|Days/week walked ≥10min continuously|1 Never · 2–8 = 1–7 days · 88 N/A (child) · 99 Unknown/no response|
|`BE3_32` / `_33`|N(2)|Daily walking duration, hours/minutes|Value · 88 N/A · 99 Unknown/no response|
|`BE5_1`|N(1)|Days/week of strength training|1 Never · 2–6 = 1 day, 2 days, 3 days, 4 days, ≥5 days · 8 N/A (child) · 9 Unknown/no response|
|`BE9`|N(2)|Adolescents: days/week with ≥60min activity|1 None in past 7 days · 2–8 = 1–7 days/week · 88 N/A (child/adult) · 99 Unknown/no response|
|`pa_aerobic`|N(1)*|Aerobic physical activity practice rate (derived; meets WHO-equivalent moderate/vigorous activity guideline)|0 Does not meet guideline · 1 Meets guideline (age 19+)|

### 2-17. Women's Health (여성건강)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`LW_ms`|N(1)|Menstruation status|1 Pre-menarche · 2 Menstruating · 3 Pregnant · 4 Postpartum/breastfeeding · 5 Natural menopause · 6 Induced menopause · 7 Other · 8 N/A (female age <10) · 9 Unknown/no response|
|`LW_mp_e`|C(50)|Amenorrhea reason: other, free text|—|
|`LW_mp_a`|N(3)*|Menopause age (derived; combines natural + induced)¹|0–79 age · 80 = 80+ · 888 N/A (female age <19 or `LW_ms` not menopause) · 999 Unknown/no response|
|`LW_ms_1`|N(1)|Cause of induced menopause (2024 only)|1 Hysterectomy · 2 Bilateral oophorectomy · 3 Radiation therapy · 4 Chemotherapy/drug treatment · 5 Other · 8 N/A · 9 Unknown/no response|
|`LW_ms_1_e`|C(50)|Induced menopause cause: other, free text|—|
|`LW_ms_a`|N(3)|Age at menarche|Age · 888 N/A · 999 Unknown/no response|
|`LW_pr`|N(1)|Ever pregnant (incl. miscarriage/abortion/ectopic)|1 Yes · 2 No · 8 N/A (female age <15) · 9 Unknown/no response|
|`LW_pr_1`|N(3)|Number of pregnancies|Count · 88 N/A · 99 Unknown/no response|
|`LW_mt`|N(1)|Ever given birth (incl. preterm)|1 Yes · 2 No · 8 N/A · 9 Unknown/no response|
|`LW_mt_a1`|N(3)|Age at first birth|Age · 888 N/A · 999 Unknown/no response|
|`LW_mt_a2`|N(3)|Age at last birth|Age · 888 N/A · 999 Unknown/no response|
|`LW_br`|N(1)|Breastfed for ≥1 month, ever|1 Yes · 2 No · 8 N/A (female age <19) · 9 Unknown/no response|
|`LW_br_ch`|N(3)|Number of children breastfed|Count · 88 N/A · 99 Unknown/no response|
|`LW_br_dur`|N(4)*|Total breastfeeding duration, months (derived)|Months · 8888 N/A · 9999 Unknown/no response|
|`LW_br_yy` / `_mm`|N(2)|Total breastfeeding duration: years / months|Value · 88 N/A · 99 Unknown/no response|
|`LW_oc`|N(1)|Ever used oral contraceptives ≥1 month|1 Yes · 2 No · 8 N/A (child/adolescent) · 9 Unknown/no response|
|`LW_wh`|N(1)|Ever used hormone therapy for menopause ≥1 month (2024 only)|1 Yes · 2 No · 8 N/A · 9 Unknown/no response|
|`LW_wh_a`|N(2)|Age started hormone therapy (2024 only)|Age · 888 N/A · 999 Unknown/no response|
|`LW_wh_dur`|N(4)*|Total hormone therapy duration, months (derived, 2024 only)|Months · 8888 N/A · 9999 Unknown/no response|
|`LW_wh_yy` / `_mm`|N(2)|Total hormone therapy duration: years / months (2024 only)|Value · 88 N/A · 99 Unknown/no response|

¹ Top-coding de-identification applied to `LW_mp_a`.

---

## 3. Health Examination Survey (검진조사)

### 3-1. Basic Examination (검진기본조사)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_fst`|N(2)|Fasting hours before exam|Hours|
|`HE_mens`|N(1)|Currently menstruating|0 No · 1 Yes · 8 N/A (male)|
|`HE_prg`|N(1)|Currently pregnant|0 No · 1 Yes · 8 N/A (male)|
|`HE_dprg`|N(2)|Months pregnant|Months|
|`HE_fh`|N(1)|Any family history of chronic disease (age 10+)|0 No · 1 Yes · 9 Unknown|
|`HE_HPfh1/2/3`|N(1)|Family history of hypertension: father/mother/sibling|0 No · 1 Yes · 8 N/A (only child, sibling var only) · 9 Unknown/no response|
|`HE_HLfh1/2/3`|N(1)|Family history of dyslipidemia: father/mother/sibling|Same coding pattern|
|`HE_IHDfh1/2/3`|N(1)|Family history of ischemic heart disease (MI/angina): father/mother/sibling|Same coding pattern|
|`HE_STRfh1/2/3`|N(1)|Family history of stroke: father/mother/sibling|Same coding pattern|
|`HE_DMfh1/2/3`|N(1)|Family history of diabetes: father/mother/sibling|Same coding pattern|
|`HE_CNfh11/21/31`|N(1)|Family history of cancer: father/mother/sibling|0 No · 1 Yes · 8 N/A (sibling, only child) · 9 Unknown/no response|
|`HE_CNfh12_1`–`_4`|C(50)|Cancer type(s): father (up to 4 free-text entries)|—|
|`HE_CNfh22_1`–`_4`|C(50)|Cancer type(s): mother|—|
|`HE_CNfh32_1`–`_4`|C(50)|Cancer type(s): sibling|—|

### 3-2. Blood Pressure Measurement (혈압 측정)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_rPLS`|N(1)|Pulse regularity|1 Regular · 2 Irregular|
|`HE_PLS_30`|N(3)|30-second pulse count|Count|
|`HE_mPLS`|N(3)|60-second pulse count|Count|
|`HE_nARM`|N(1)|Arm used for BP measurement|1 Right · 2 Left|
|`HE_armcir`|N(3)|Arm circumference|cm (1 decimal)|
|`HE_sbp1/2/3`, `HE_dbp1/2/3`|N(8)|Systolic/diastolic BP, measurements 1–3|mmHg|
|`HE_sbp`, `HE_dbp`|N(8)*|Final systolic/diastolic BP (derived; mean of readings 2 & 3)|mmHg|
|`HE_HP`|N(1)*|Hypertension status (derived)|1 Normal (SBP<120 & DBP<80) · 2 Elevated (SBP 120–129 & DBP<80) · 3 Pre-hypertension (SBP 130–139 or DBP 80–89) · 4 Hypertension (SBP≥140 or DBP≥90 or on medication)|

_Note: BP device changed from mercury to non-mercury sphygmomanometer across cycles; conversion formulas exist in source for cross-cycle comparison — see PDF p.176–177 if merging with pre-2020 data._

### 3-3. Body Measurements (신체계측)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_ht`|N(8.1)|Height|cm|
|`HE_wt`|N(8.1)|Weight¹|kg|
|`HE_wc`|N(8.1)|Waist circumference|cm|
|`HE_nc`|N(8.1)|Neck circumference (2022–2023 only)|cm|
|`HE_BMI`|N(8.1)*|BMI (derived)|kg/m²|
|`HE_obe`|N(1)*|Obesity status (derived; non-pregnant only)|1 Underweight (BMI<18.5) · 2 Normal (18.5–<23) · 3 Pre-obese (23–<25) · 4 Obese class 1 (25–<30) · 5 Obese class 2 (30–<35) · 6 Obese class 3 (≥35)|
|`HE_wt_pct`|N(1)*|Child/adolescent weight percentile, ages 1–18 (derived)|1 <5th percentile · 2 5th–<95th · 3 ≥95th|
|`HE_BMI_pct`|N(1)*|Child/adolescent BMI percentile, ages 2–18 (derived)|1 <5th · 2 5th–<85th · 3 85th–<95th · 4 ≥95th|

¹ Weight measurement includes a clothing-weight correction (varies by season/age); see source p.179 for correction table if merging with pre-2020 data.

### 3-4. Blood Test (혈액검사)

**Diabetes**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_glu`|N(8)|Fasting blood glucose|mg/dL|
|`HE_HbA1c`|N(8.1)|HbA1c|%|
|`HE_DM_HbA1c`|N(1)*|Diabetes status (derived; non-pregnant, fasted ≥8hr)|1 Normal (glucose <100 & HbA1c <5.7%) · 2 Pre-diabetes (glucose 100–125 or HbA1c 5.7–6.4%) · 3 Diabetes (glucose ≥126, doctor-diagnosed, on medication/insulin, or HbA1c ≥6.5%)|

**Dyslipidemia**

| Variable      | Type  | Description                                                  | Codes / Values                              |
| ------------- | ----- | ------------------------------------------------------------ | ------------------------------------------- |
| `HE_chol`     | N(8)  | Total cholesterol                                            | mg/dL                                       |
| `HE_HDL_st2`  | N(8)  | HDL cholesterol                                              | mg/dL                                       |
| `HE_TG`       | N(8)  | Triglycerides                                                | mg/dL                                       |
| `HE_LDL_drct` | N(8)  | LDL cholesterol (direct assay)                               | mg/dL                                       |
| `HE_HCHOL`    | N(1)* | Hypercholesterolemia status (derived; age 19+, fasted ≥8hr)  | 0 No · 1 Yes (total chol ≥240 or on statin) |
| `HE_HTG`      | N(1)* | Hypertriglyceridemia status (derived; age 19+, fasted ≥12hr) | 0 No · 1 Yes (TG ≥200)                      |

**Liver function**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_ast`|N(8)|AST (SGOT)|IU/L|
|`HE_alt`|N(8)|ALT (SGPT)|IU/L|
|`HE_alt_etc`|C(10)|ALT lower reporting limit flag|"<5" if below 5 IU/L|
|`HE_hepaB`|N(1)|Hepatitis B surface antigen (age 10+)|0 Negative · 1 Positive|
|`HE_hepaC`|N(1)|Hepatitis C antibody (age 10+)|0 Negative · 1 Positive|

**Anemia**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_HB`|N(8.1)|Hemoglobin|g/dL|
|`HE_HCT`|N(8.1)|Hematocrit|%|
|`HE_anem`|N(1)*|Anemia status (derived; age-/sex-/pregnancy-specific Hb thresholds, age 10+)|0 No · 1 Yes|

**Kidney function**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_BUN`|N(8)|Blood urea nitrogen|mg/dL|
|`HE_crea`|N(8.2)|Serum creatinine|mg/dL|

**General blood panel / other**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_WBC`|N(8.2)|White blood cell count|Thous/uL|
|`HE_RBC`|N(8.2)|Red blood cell count|Mil/uL|
|`HE_Bplt`|N(8)|Platelet count|Thous/uL|
|`HE_MCV`|N(8.1)|Mean corpuscular volume (2009–2023 data; released Jan 2026)|fL|
|`HE_MCH`|N(8.1)|Mean corpuscular hemoglobin (2009–2023)|pg|
|`HE_MCHC`|N(8.1)|Mean corpuscular hemoglobin concentration (2009–2023)|g/dL|
|`HE_PTH`|N(8)|Parathyroid hormone (2024 only)|pg/mL|
|`HE_ALP`|N(8)|Alkaline phosphatase (2024 only)|U/L|
|`HE_Uacid`|N(8.1)|Uric acid|mg/dL|
|`HE_hsCRP`|N(8.1)|High-sensitivity CRP|mg/L|
|`HE_hsCRP_etc`|C(10)|hsCRP lower reporting limit flag|"<0.2" etc., varies by year|
|`HE_Ca`|N(8.1)|Calcium (2024 only)|mg/dL|
|`HE_P`|N(8.1)|Inorganic phosphorus (2024 only)|mg/dL|
|`HE_Mg`|N(8.1)|Magnesium (2024 only)|mg/dL|
|`HE_D2`|N(8.2)|25(OH)D2 (vitamin D)|ng/mL|
|`HE_D2_etc`|C(10)|25(OH)D2 lower reporting limit flag|"<0.30"|
|`HE_D3`|N(8)|25(OH)D3 (vitamin D)|ng/mL|
|`HE_D3_3epi`|N(8.2)|3-epi-25(OH)D3|ng/mL|
|`HE_D3_3epi_etc`|C(10)|3-epi-25(OH)D3 lower reporting limit flag|"<0.50"|

> **Methodology note:** Lab vendor/equipment/reagent changed in 2022 (and at other points historically) for several analytes (HbA1c, triglycerides, AST/ALT, vitamin D, HDL). Research-use conversion formulas for cross-year comparability are provided in the source (pp.181–183) — consult these if pooling KNHANES cycles that span a lab-method change; official KDCA statistics use raw values without conversion.

### 3-5. Urine Test (소변검사)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_Uph`|N(8.1)|Urine pH|Value|
|`HE_Unitr`|N(1)|Urine nitrite|0 Negative · 1 Positive|
|`HE_Usg`|N(8.3)|Urine specific gravity|Value|
|`HE_Upro`|N(1)|Urine protein|0 Negative(-) · 1 Trace(±) · 2 Positive(+) · 3 Positive(++) · 4 Positive(+++) · 5 Positive(++++)|
|`HE_Uglu`|N(1)|Urine glucose|Same 0–5 scale as `HE_Upro`|
|`HE_Uket`|N(1)|Urine ketone|Same 0–5 scale|
|`HE_Ubil`|N(1)|Urine bilirubin|Same 0–5 scale|
|`HE_Ubld`|N(1)|Urine occult blood|Same 0–5 scale|
|`HE_Uro`|N(1)|Urobilinogen|Same 0–5 scale|
|`HE_Ucrea`|N(8.1)|Urine creatinine|mg/dL|
|`HE_UNa`|N(8)|Urine sodium|mmol/L|
|`HE_UNa_etc`|C(10)|Urine sodium lower reporting limit flag|"<20"|
|`HE_Ualb`|N(8)|Urine albumin|µg/mL|
|`HE_Ualb_etc`|C(10)|Urine albumin lower reporting limit flag|"<3.0"|
|`HE_Ukal`|N(8)|Urine potassium|mmol/L|
|`HE_Ukal_etc`|C(10)|Urine potassium reporting range flag|"<3" or ">100"|

### 3-6. Oral (Dental) Examination (구강검사)

#### 3-6-1. Teeth & Prosthetic Status (치아 및 보철상태)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`O_TC`|N(2)*|Number of remaining natural teeth (derived; total incl. 3rd molars)|Count (0–32)|
|`O_PROS_U`|N(1)|Maxillary (upper) prosthetic status|0 No prosthesis · 1 One fixed bridge · 2 Two+ fixed bridges · 3 Removable partial denture only · 4 Fixed bridge + removable partial denture · 5 Full/complete denture · 9 Unrecordable|
|`O_PROS_L`|N(1)|Mandibular (lower) prosthetic status|Same coding as `O_PROS_U`|
|`O_IMP_UI`|N(2)|Maxillary anterior implants|Count|
|`O_IMP_UM`|N(2)|Maxillary posterior implants|Count|
|`O_IMP_LI`|N(2)|Mandibular anterior implants|Count|
|`O_IMP_LM`|N(2)|Mandibular posterior implants|Count|
|`O_BR_N_U`|N(2)|Maxillary units needed for fixed bridge|Count|
|`O_BR_N_L`|N(2)|Mandibular units needed for fixed bridge|Count|
|`O_DENT_U`|N(1)|Maxillary denture need|0 None · 1 Partial denture needed · 2 Full denture needed|
|`O_DENT_L`|N(1)|Mandibular denture need|0 None · 1 Partial denture needed · 2 Full denture needed|
|`O_F`|N(1)|Dental fluorosis (age 11 only)|0 Normal · 1 Questionable · 2 Very mild · 3 Mild · 4 Moderate · 5 Severe · 7 Non-fluoride-related abnormality · 9 Unrecordable|

> **Key variable for your research:** `O_TC` (remaining natural teeth count) is likely your primary continuous/derivable outcome for tooth loss; `O_PROS_U`/`O_PROS_L` and `O_DENT_U`/`O_DENT_L` give denture/prosthetic status which could serve as an alternate categorical outcome or severity marker.

#### 3-6-2. Oral Health Interview (구강면접)

| Variable  | Type | Description                             | Codes / Values                                                       |
| --------- | ---- | --------------------------------------- | -------------------------------------------------------------------- |
| `OR1`     | N(1) | Self-rated oral health (age 1+)         | 1 Very good · 2 Good · 3 Fair · 4 Poor · 5 Very poor · 9 No response |
| `O_pain`  | N(1) | Toothache in past year (age 1+)         | 0 No · 1 Yes · 9 No response                                         |
| `O_ortho` | N(1) | Ever had orthodontic treatment (age 1+) | 0 No · 1 Yes · 9 No response                                         |

#### 3-6-3. Oral Health Behaviors (구강건강)

| Variable      | Type  | Description                                                                                                                                                                                       | Codes / Values                                                                                                                                  |
| ------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `BM1_0`       | N(1)  | Brushed teeth yesterday (age 1+)                                                                                                                                                                  | 0 No · 1 Yes · 9 Unknown/no response                                                                                                            |
| `BM1_1`–`_8`  | N(1)  | Brushing timing, multi-select: `_1` before breakfast · `_2` after breakfast · `_3` before lunch · `_4` after lunch · `_5` before dinner · `_6` after dinner · `_7` after snacks · `_8` before bed | 0 No · 1 Yes · 8 N/A (didn't brush) · 9 Unknown/no response                                                                                     |
| `BM2_1`       | N(1)  | Uses floss (age 12+, 2022 only)                                                                                                                                                                   | 0 No · 1 Yes · 8 N/A (age <12) · 9 Unknown/no response                                                                                          |
| `BM2_3`       | N(1)  | Uses interdental brush (2022 only)                                                                                                                                                                | Same coding as `BM2_1`                                                                                                                          |
| `BM2_2`       | N(1)  | Uses mouthwash/oral rinse (2022 only)                                                                                                                                                             | Same coding as `BM2_1`                                                                                                                          |
| `BM2_4`       | N(1)  | Uses electric toothbrush (2022 only)                                                                                                                                                              | Same coding as `BM2_1`                                                                                                                          |
| `BM2_5`       | N(1)  | Uses water flosser/tongue cleaner/implant brush/denture care products (2022 only)                                                                                                                 | Same coding as `BM2_1`                                                                                                                          |
| `BM13`        | N(1)  | Ever had tooth damage from sports/accident (age 1+, 2022 only)                                                                                                                                    | 0 No · 1 Yes · 9 Unknown/no response                                                                                                            |
| `BM13_1`–`_5` | N(1)  | Cause of tooth damage, multi-select: `_1` sports · `_2` violence · `_3` traffic accident · `_4` other safety accident · `_5` other                                                                | 0 No · 1 Yes · 8 N/A (no damage) · 9 Unknown/no response                                                                                        |
| `BM13_6`      | C(50) | Tooth damage cause: other, free text                                                                                                                                                              | —                                                                                                                                               |
| `BM7`         | N(1)  | Chewing difficulty (age 19+; report as-worn if denture user)                                                                                                                                      | 1 Very uncomfortable · 2 Uncomfortable · 3 Neutral · 4 Not uncomfortable · 5 Not at all uncomfortable · 8 N/A (age <19) · 9 Unknown/no response |
| `O_chew_d`    | N(1)* | Chewing discomfort complaint rate (derived; age 19+)                                                                                                                                              | 0 No (BM7=3,4,5) · 1 Yes (BM7=1,2)                                                                                                              |

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BM8`|N(1)|Speaking difficulty due to dental/gum problems (age 19+)|Same 5-point scale as `BM7` (1 Very uncomfortable → 5 Not at all) · 8 N/A · 9 Unknown/no response|
|`OR1_2`|N(1)|Had dental check-up (no specific complaint) in past year (age 1+)|0 No · 1 Yes · 9 Unknown/no response|
|`MO4_00`|N(1)|Used dental clinic/hospital in past year (age 1+)¹|0 No · 1 Yes · 9 Unknown/no response|
|`MO4_4`|N(1)|Dental service received: exam (visual/X-ray)|0 No · 1 Yes · 8 N/A (didn't use dental care) · 9 Unknown/no response|
|`MO4_9`|N(1)|Dental service received: gum disease treatment (incl. surgery)|Same coding as `MO4_4`|
|`MO4_7`|N(1)|Dental service received: simple cavity filling|Same coding as `MO4_4`|
|`MO4_8`|N(1)|Dental service received: root canal|Same coding as `MO4_4`|
|`MO4_17_1`|N(1)|Dental service received: preventive care (sealants, fluoride)|Same coding as `MO4_4`|
|`MO4_17_2`|N(1)|Dental service received: scaling (full-mouth)|Same coding as `MO4_4`|
|`MO4_11`|N(1)|Dental service received: extraction/oral surgery (excl. baby teeth)|Same coding as `MO4_4`|
|`MO4_12`|N(1)|Dental service received: treatment of accidentally lost/broken tooth|Same coding as `MO4_4`|
|`MO4_18`|N(1)|Dental service received: prosthetic (bridge/implant/denture) fabrication or repair|Same coding as `MO4_4`|
|`MO4_15`|N(1)|Dental service received: other (orthodontic, cosmetic, etc.)|Same coding as `MO4_4`|
|`BM14`|N(1)|Unmet dental need in past year (age 1+)|1 Yes · 2 No · 3 Not needed · 9 Unknown/no response|
|`BM14_1`|N(2)|Reason for unmet dental need|1 No time · 2 Symptom seemed mild · 3 Financial · 4 Transportation/distance · 5 Didn't want to wait · 6 Hard to book · 7 Afraid of treatment · 8 Other · 88 N/A · 9/99 Unknown/no response|
|`BM14_2`|C(50)|Unmet dental need reason: other, free text|—|

¹ Recall period changed: "past 2 weeks" (2010–2011) vs. "past year" (2012–2024) — relevant if pooling cycles.

### 3-7. Grip Strength (악력검사)

_Age scope varies by year: 2022 age 10+, 2023 age 65+, 2024 age 40+._

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`GS_use`|N(1)|Dominant hand|1 Right · 2 Left · 3 Both · 9 No response/not examined|
|`GS_mea_r_1` / `_2`|N(4.1)|Grip strength, right hand, trial 1 / 2|kg|
|`GS_mea_l_1` / `_2`|N(4.1)|Grip strength, left hand, trial 1 / 2|kg|
|`GS_SP_DXA`|N(1)*|Sarcopenia status by DXA criteria (derived; age 65+)|0 No · 1 Yes (max grip <28kg male/<18kg female AND appendicular lean mass/height² <7.0 male/<5.4 female)|

### 3-8. Body Composition (Bioimpedance) (체성분검사)

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`BIA_ex`|N(1)|Participated in body composition exam|1 Measured · 2 Excluded (pregnant, pacemaker, implanted defibrillator) · 3 Other (refused, uncooperative, prosthetic limb, etc.)|
|`BIA_FFM`|N(4.1)|Total fat-free mass (incl. head)|kg|
|`BIA_LRA` / `BIA_LLA`|N(4.2)|Right/left arm muscle mass (excl. bone mineral)|kg|
|`BIA_LRL` / `BIA_LLL`|N(5.2)|Right/left leg muscle mass (excl. bone mineral)|kg|
|`BIA_BFM`|N(4.1)|Total body fat mass (incl. head)|kg|
|`BIA_PBF`|N(4.1)|Body fat percentage|%|
|`BIA_FRA` / `BIA_FLA`|N(4.1)|Right/left arm fat mass|kg|
|`BIA_FT`|N(4.1)|Trunk fat mass|kg|
|`BIA_FRL` / `BIA_FLL`|N(4.1)|Right/left leg fat mass|kg|
|`BIA_TBW`|N(4.1)|Total body water|L|
|`BIA_ICW`|N(4.1)|Intracellular water|L|
|`BIA_ECW`|N(4.1)|Extracellular water|L|
|`BIA_WBPA50`|N(4.1)|50kHz whole-body phase angle (right-side measurement)|degrees|

### 3-9. Pulmonary Function Test (폐기능검사)

_Suspended 2020–2023 (COVID-19); 2024 only._

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`HE_fvc`|N(8.3)|Forced vital capacity|L|
|`HE_fev1`|N(8.3)|Forced expiratory volume in 1 sec|L|
|`HE_fev1fvc`|N(8.3)|FEV1/FVC ratio|Ratio|
|`HE_fev6`|N(8.3)|Forced expiratory volume in 6 sec|L|
|`HE_fef25_75`|N(8.3)|Forced expiratory flow, 25–75%|L/sec|
|`HE_pef`|N(8.3)|Peak expiratory flow|L/sec|
|`HE_COPD1`|N(1)*|COPD status by spirometry (derived; age 40+, FEV1/FVC <0.7, no bronchodilator)|0 No · 1 Yes · 9 Indeterminate|
|`HE_cough1`|N(1)|Chronic cough ≥3 consecutive months|0 No · 1 Yes|
|`HE_cough2`|N(2)|Duration of chronic cough|Years|
|`HE_sput1`|N(1)|Chronic sputum ≥3 consecutive months|0 No · 1 Yes|
|`HE_sput2`|N(2)|Duration of chronic sputum|Years|
|`HE_PFTdr`|N(1)|COPD ever diagnosed by doctor|0 No · 1 Yes|
|`HE_PFTag`|N(3)|Age at COPD diagnosis (top-coded)|Age|
|`HE_PFTtr`|N(1)|COPD treatment status|1 Currently treating · 2 Treated in past, not now · 3 Never treated|
|`HE_PFThs`|N(1)|Hospitalized for COPD in past year|0 No · 1 Yes|

### 3-10. ENT (Ear, Nose, Throat) Examination (이비인후검사)

_2022–2023 only._

**Hearing self-report & noise exposure**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`T_ex`|N(1)|ENT exam/survey participation|1 Measured|
|`T_Q_HR`|N(1)|Self-rated hearing (age 12+, without hearing aid)|1 No difficulty · 2 Slight difficulty · 3 Much difficulty · 4 Cannot hear at all · 9 No response|
|`T_Q_HR_1`|N(1)|Hearing device used|1 Hearing aid · 2 Cochlear implant · 3 None · 8 N/A (age <12/Q1=1) · 9 No response|
|`T_Q_HR_2`|N(1)|Hearing device usage frequency|1 Daily · 2 ≥15 days/month · 3 <15 days/month · 4 Rarely · 8 N/A · 9 No response|
|`T_NQ_OCP`|N(1)|Occupational noise exposure ≥3 years (age 40+)|1 Yes · 2 No · 8 N/A (age <40) · 9 No response|
|`T_NQ_PH2`|N(1)|Earphone use in noisy places (age 12+)¹|1 Yes · 2 No · 3 Don't recall · 9 No response|
|`T_NQ_PH2_T`|N(4)|Daily earphone use duration in noisy places|Minutes · 8888 N/A · 9999 No response|
|`T_Q_VN`|N(1)|Tinnitus ≥5min in past 12 months (age 40+)|1 Yes · 2 No · 3 Don't recall · 8 N/A · 9 No response|
|`T_Q_VN_1`|N(1)|Tinnitus lasted ≥6 months|1 Yes · 2 No · 8 N/A · 9 No response|
|`T_Q_VN_2`|N(2)|Tinnitus distress level (0–10 scale)|Score · 88 N/A · 99 No response|

¹ Question wording changed between cycles (added "games/video" in 2022) — not directly comparable to 2010–2018.

**Dizziness, rhinitis, sinusitis, voice (age 40+)**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`T_Q_DZ`|N(1)|Dizziness/balance problem in past 12 months|1 Yes · 2 No · 3 Don't recall · 8 N/A · 9 No response|
|`T_Q_DZ2`|N(1)|Fell/collapsed from balance loss w/o external cause|1 Yes · 2 No|
|`T_Q_DZ3`|N(1)|Dizziness/balance issue recurred ≥2 times|1 Yes · 2 No|
|`T_Q_DZ4`–`_7`|N(1)|Past 3 months: `_4` difficulty maintaining standing posture · `_5` difficulty walking · `_6` chronic dizziness · `_7` recurrent falls|1 Yes · 2 No · 8 N/A · 9 No response|
|`T_Q_CR`|N(1)|Non-cold rhinitis symptoms (sneezing/runny/blocked/itchy nose) in past 12 months|1 Yes · 2 No · 8 N/A · 9 No response|
|`T_Q_CR1`|N(1)|Symptom seasonality|1 Seasonal only · 2 Year-round · 8 N/A · 9 No response|
|`T_Q_CR2`|N(1)|Weekly symptom duration|1 <4 days · 2 ≥4 days|
|`T_Q_CR3`|N(1)|Longest symptom duration|1 <1 month · 2 ≥1 month|
|`T_Q_CR4`|N(1)|Symptoms interfere with study/work/sleep|1 Yes · 2 No|
|`T_Q_ALLE`|N(1)|Allergic rhinitis diagnosed by objective test|1 Yes · 2 No · 8 N/A · 9 No response|
|`T_Q_SNST1`–`_4`|N(1)|Symptoms ≥3 months: `_1` post-nasal drip · `_2` nasal congestion · `_3` facial pain/pressure · `_4` smell disorder|1 Present · 2 Absent · 8 N/A · 9 No response|
|`T_Q_SINU`|N(1)|Chronic sinusitis diagnosed by objective exam (endoscopy/CT)|1 Yes · 2 No · 8 N/A · 9 No response|
|`T_Q_SINU_1`|N(1)|Nasal polyp diagnosed|1 Yes · 2 No · 8 N/A · 9 No response|
|`T_Q_VC`|N(1)|Self-perceived voice abnormality|1 Yes · 2 No · 8 N/A · 9 No response|
|`T_Q_VC1`|N(1)|Duration of voice problem|1 <3 weeks · 2 ≥3 weeks · 8 N/A · 9 No response|

**Pure-tone audiometry (age 12+)**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`T_HR_EX_R` / `_L`|N(1)|Audiometry performed, right/left|0 Not measured · 1 Measured|
|`T_HR_EX_R_1` / `_L_1`|N(1)|Reason not measured|1 Refused · 2 Uncooperative · 3 Equipment error · 4 Other|
|`T_HR500_pass` etc. (`_1000`, `_2000`, `_4000`)|N(1)|Booth noise level within ANSI standard, by frequency|0 Within limit · 1 Exceeded|
|`T_HR500_RT`–`T_HR8000_RT`|N(3)|Right ear threshold at 500/1000/2000/4000/8000 Hz|dB|
|`T_HR500_LT`–`T_HR8000_LT`|N(3)|Left ear threshold at 500/1000/2000/4000/8000 Hz|dB|
|`T_HL_mod`|N(1)*|Moderate+ hearing loss status (derived; PTA ≥41dB either ear, age 40+)|0 No · 1 Yes|
|`T_HL_mild`|N(1)*|Mild hearing loss status (derived; PTA 26–40dB either ear, age 40+)|0 No · 1 Yes|

**Tympanometry (age 40+)**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`T_IM_EX_R` / `_L`|N(1)|Tympanometry performed, right/left|0 Not measured · 1 Measured|
|`T_IM_EX_R_1` / `_L_1`|N(1)|Reason not measured|1 Refused · 2 Uncooperative · 3 Equipment error · 4 Other|
|`T_IM_A_R/_L`, `T_IM_B_R/_L`, `T_IM_C_R/_L`, `T_IM_FL_R/_L`|N(1)|Tympanogram type A/B/C/Flat, right/left|0 Not applicable · 1 Applicable|
|`T_Tymp_Dis`|N(1)*|Tympanic membrane abnormality status (derived; type B/C/Flat either ear)|0 No · 1 Yes|

### 3-11. Eye Examination (안검사)

_Age scope varies by year: 2022 age 60+, 2023 age 40–59, 2024 age 19–39._

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`E_ex`|N(1)|Eye exam/survey participation|1 Participated|
|`E_Q_EX`|N(1)|Time since last eye exam|1 <1 month · 2 1mo–1yr · 3 1–3yr · 4 ≥3yr · 5 Never · 9 No response|
|`E_RT`|N(1)|Average daily reading time|1 ≤1hr · 2 1–2hr · 3 3hr · 4 ≥4hr · 9 No response|
|`E_CT`|N(1)|Average daily smart device use|1 ≤1hr · 2 1–2hr · 3 3hr · 4 ≥4hr · 9 No response|
|`E_EXC_1`|N(1)|Excluded from eye exam (anophthalmia/enucleation)|1 Both eyes · 2 Right eye · 3 Left eye · 4 N/A · 9 No response|
|`E_Cr_m` / `E_Cl_m`|N(1)|Visual acuity measurement method, right/left|1 Uncorrected · 2 Corrected (glasses/lens) · 8 N/A · 9 No response/not examined|
|`E_Cr_1` / `E_Cl_1`|N(2)|Visual acuity value, right/left (2022–2023 only)|Snellen-equivalent decimal scale: 1=1.0, 2=0.8, 3=0.63 ... 12=0.025, 13 finger count, 14 hand motion, 15 light perception present, 16 light perception absent · 88 N/A · 99 No response|
|`E_Dr_dsph` / `E_Dl_dsph`|N(6.2)|Autorefraction sphere, right/left|Diopters · 888.88 N/A · 999.99 No response|
|`E_Dr_dcyl` / `E_Dl_dcyl`|N(6.2)|Autorefraction cylinder, right/left|Diopters · 888.88 N/A · 999.99 No response|
|`E_Dr_a` / `E_Dl_a`|N(4)|Autorefraction axis, right/left|Degrees · 8888 N/A · 9999 No response|
|`E_Dr_2_1` / `E_Dl_2_1`|N(2)|Corrected acuity from autorefraction, right/left|Same 1–16 scale as `E_Cr_1` · 88 N/A · 99 No response|

---

## Bone Density (골밀도검사) & Nutrition Survey Note

Section 3-12 (Bone Density / DXA, ~590 lines covering whole-body, spine, femur, forearm BMD/BMC/area for numerous skeletal sites — variable prefixes `DX_*` and `DW_*`) and Section 4 (Nutrition Survey: 4-1 Dietary Habits, 4-2 Food Intake incl. the 24-hr recall macro/micronutrient variables `N_*`, 4-3 Food Security `LF_*`) are large, highly granular technical modules (bone density alone covers ~150 variables across body sites; the nutrient intake table alone covers ~50 variables per food item). Given the length already produced, I've paused before these two to check whether you want:

1. **Full same-detail treatment** (will roughly double the document length — bone density DXA sites + nutrition intake variables are extremely repetitive across body regions/nutrients), or
2. **A condensed version** — one row per variable _group_ (e.g. "DX_L1_A/BMC/BMD through DX_L4_A/BMC/BMD = lumbar vertebrae 1–4: area/bone mineral content/bone mineral density, cm²/g/g·cm⁻²" as a single row instead of 12 rows), which captures 100% of the variables but far more compactly.

Given neither bone density nor detailed nutrient-intake variables are central to your marital-status/tooth-loss analysis, I'd lean toward condensed for these two sections. Let me know, or I'll default to condensed and continue.

### 3-12. Bone Density (골밀도검사) — DXA

_Age scope: 40+. Data from Hologic DXA scanner; Asian(Japan)-reference T-/Z-scores._

**3-12-1. Survey questions**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`DXW_ex`|N(1)|Bone density exam/survey participation|1 Participated · 2 Excluded · 3 N/A (age <40)|
|`DX_Q_dxa`|N(1)|Ever had a DXA scan before|1 Yes · 2 No · 8 N/A · 9 No response|
|`DX_Q_fall`|N(1)|Fell ≥1 time in past year|1 Yes · 2 No · 8 N/A · 9 No response|
|`DX_Q_fnm`|N(4)|Number of falls|Count · 8888 N/A · 9999 No response|
|`DX2_dg`|N(1)|Ever diagnosed with fracture (spine/hip/wrist/upper arm)|1 Yes · 2 No · 8 N/A · 9 No response|
|`DX2_1`|N(1)|Fracture site|1 Spine · 2 Hip · 3 Wrist · 4 Upper arm · 5 Other · 8 N/A · 9 No response|
|`DX2_2`|N(1)|Fracture diagnosed in past year|1 Yes · 2 No · 8 N/A · 9 No response|
|`DX_Q_st`|N(1)|Took oral steroids ≥3 consecutive months, ever|1 Yes · 2 No · 3 Don't know · 8 N/A · 9 No response|
|`DX_Q_hsty`|N(1)|Parent(s) with osteoporosis/fragility fracture history|1 Father · 2 Mother · 3 Both · 4 None · 5 Don't know · 8 N/A · 9 No response|

**3-12-2. Regional bone density** — variable pattern `DX_[site]_A` (area, cm²), `DX_[site]_BMC` (bone mineral content, g), `DX_[site]_BMD` (density, g/cm²); missing/unreadable = 9999.99 (A, BMC) or 9999.999 (BMD)

|Site group|Variables|
|---|---|
|Total femur|`DX_TFM_A/BMC/BMD`|
|Femur trochanter|`DX_TR_A/BMC/BMD`|
|Femur intertrochanter|`DX_IT_A/BMC/BMD`|
|Femoral neck|`DX_NK_A/BMC/BMD`|
|Ward's triangle|`DX_WD_A/BMC/BMD`|
|Lumbar spine (L1–L4 combined)|`DX_LSP_A/BMC/BMD`|
|Lumbar vertebrae individually|`DX_L1_A/BMC/BMD` … `DX_L4_A/BMC/BMD` (12 variables, L1 through L4)|
|T-scores (Asian reference)|`DX_F_Ts_A` (total femur) · `DX_FN_Ts_A` (femoral neck) · `DX_S1_Ts_A`–`DX_S4_Ts_A` (L1–L4) · `DX_S_Ts_A` (overall spine, excludes outlier vertebra if T-score range ≥1) — all N(8.3)*|
|Z-scores (Asian reference)|`DX_F_Zs_A` (total femur) · `DX_FN_Zs_A` (femoral neck) · `DX_S_Zs_A` (overall spine) — N(8.3)*|
|Osteoporosis status (derived)|`DX_OST` N(1)*: 1 Normal (lowest T-score ≥-1.0) · 2 Osteopenia (-2.5 < T-score < -1.0) · 3 Osteoporosis (T-score ≤-2.5); postmenopausal women or men 50+ only|

**3-12-3. Hip geometry** — pattern `DX_[site]_CSA` (cross-sectional area, cm²), `DX_[site]_WD` (width, cm), `DX_[site]_CTK` (cortical thickness, cm)

|Site group|Variables|
|---|---|
|Femoral neck|`DX_NK_CSA/WD/CTK`|
|Intertrochanter|`DX_IT_CSA/WD/CTK`|
|Femur shaft|`DX_FS_CSA/WD/CTK`|
|Other|`DX_HAL` hip axis length (cm) · `DX_NS_ANG` neck-shaft angle (degrees)|

**3-12-4. Whole-body regional bone mass** — pattern `DW_[site]_A/BMC/BMD` (same units as 3-12-2)

|Site group|Variables|
|---|---|
|Head|`DW_HD_A/BMC/BMD`|
|Arms|`DW_Lrm_A/BMC/BMD` (left) · `DW_Rrm_A/BMC/BMD` (right)|
|Ribs|`DW_Lrb_A/BMC/BMD` (left) · `DW_Rrb_A/BMC/BMD` (right)|
|Spine|`DW_TS_A/BMC/BMD` (thoracic) · `DW_LS_A/BMC/BMD` (lumbar)|
|Pelvis|`DW_plv_A/BMC/BMD`|
|Legs|`DW_Llg_A/BMC/BMD` (left) · `DW_Rlg_A/BMC/BMD` (right)|
|Subtotal (excl. head)|`DW_SBT_A/BMC/BMD`|
|Whole body total|`DW_WBT_A/BMC/BMD`|

**3-12-5. Whole-body regional fat/lean composition (DXA)** — pattern `DW_[site]_FT` (fat mass, g), `DW_[site]_LN` (lean mass incl. bone, g), `DW_[site]_MS` (total mass, g), `DW_[site]_pFT` (fat %)

|Site group|Variables|
|---|---|
|Head|`DW_HD_FT/LN/MS/pFT`|
|Arms|`DW_Lrm_FT/LN/MS/pFT` (left) · `DW_Rrm_FT/LN/MS/pFT` (right)|
|Trunk|`DW_Trk_FT/LN/MS/pFT`|
|Legs|`DW_Llg_FT/LN/MS/pFT` (left) · `DW_Rlg_FT/LN/MS/pFT` (right)|
|Subtotal (excl. head)|`DW_SBT_FT/LN/MS/pFT`|
|Whole body total|`DW_WBT_FT/LN/MS/pFT`|

---

## 4. Nutrition Survey (영양조사)

### 4-1. Dietary Habits (식생활조사)

| Variable                             | Type   | Description                                                               | Codes / Values                                                                                                                                                      |
| ------------------------------------ | ------ | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `L_BR` / `L_LN` / `L_DN`             | N(1)*  | Skipped breakfast/lunch/dinner 2 days before food-intake survey (derived) | 1 Yes · 0 No                                                                                                                                                        |
| `L_BR_FQ` / `L_LN_FQ` / `L_DN_FQ`    | N(1)   | Weekly frequency of breakfast/lunch/dinner, past year                     | 1 5–7×/wk · 2 3–4×/wk · 3 1–2×/wk · 4 Almost never (0×/wk) · 9 Unknown/no response                                                                                  |
| `L_BR_TO` / `L_LN_TO` / `L_DN_TO`    | N(1)   | Usually eats breakfast/lunch/dinner with others                           | 1 Yes · 2 No · 3 N/A (meal freq ≤2×/wk) · 9 Unknown/no response                                                                                                     |
| `L_BR_WHO` / `L_LN_WHO` / `L_DN_WHO` | N(1)   | Who they eat breakfast/lunch/dinner with                                  | 1 Family · 2 Non-family · 8 N/A · 9 Unknown/no response                                                                                                             |
| `L_OUT_FQ`                           | N(1)   | Average eating-out frequency, past year                                   | 1 ≥2×/day · 2 1×/day · 3 5–6×/wk · 4 3–4×/wk · 5 1–2×/wk · 6 1–3×/month · 7 Almost never (<1×/month) · 9 Unknown/no response                                        |
| `LS_VEG1`                            | N(2)   | Frequency of vegetables/mushrooms/seaweed incl. kimchi/pickles, past year | 1 ≥3×/day · 2 2×/day · 3 1×/day · 4 5–6×/wk · 5 2–4×/wk · 6 1×/wk · 7 2–3×/month · 8 1×/month · 9 Almost never · 99 Unknown/no response                             |
| `LS_VEG2`                            | N(2)   | Same as `LS_VEG1` but excluding kimchi/pickles                            | Same coding                                                                                                                                                         |
| `LS_FRUIT`                           | N(2)   | Frequency of fruit intake, past year                                      | Same coding as `LS_VEG1`                                                                                                                                            |
| `LS_1YR`                             | N(1)   | Took dietary supplements ≥2 weeks continuously, past year                 | 1 Yes · 2 No · 9 Unknown/no response                                                                                                                                |
| `LK_EDU`                             | N(1)   | Received nutrition education/counseling in past year                      | 1 Yes · 2 No · 3 N/A (below elementary school age) · 9 Unknown/no response                                                                                          |
| `LK_LB_CO`                           | N(1)   | Aware of nutrition labeling                                               | 1 Yes · 2 No · 3 N/A · 9 Unknown/no response                                                                                                                        |
| `LK_LB_US`                           | N(1)   | Reads nutrition labels when buying processed food                         | 1 Yes · 2 No · 8 N/A · 9 Unknown/no response                                                                                                                        |
| `LK_LB_IT`                           | N(2)   | Nutrient of most interest on labels                                       | 1 Calories · 2 Carbohydrates · 3 Sugars · 4 Protein · 5 Fat · 6 Saturated fat · 7 Trans fat · 8 Cholesterol · 9 Sodium · 10 Other · 88 N/A · 99 Unknown/no response |
| `LK_LB_EF`                           | N(1)   | Nutrition label influences food choice                                    | 1 Yes · 2 No · 8 N/A · 9 Unknown/no response                                                                                                                        |
| `Y_BTH_WT`                           | N(8.2) | Birth weight (respondent ages 12–47 months)                               | kg · 999 Unknown/no response                                                                                                                                        |
| `Y_MTM_YN`                           | N(1)   | Ever breastfed                                                            | 1 Yes · 2 No · 9 Unknown/no response                                                                                                                                |
| `Y_MTM_S1` / `_S2`                   | N(3)   | Breastfeeding start age, 1st/2nd period                                   | Weeks · 888 N/A · 999 Unknown/no response                                                                                                                           |
| `Y_MTM_D1` / `_D2`                   | N(3)   | Breastfeeding duration, 1st/2nd period                                    | Months · 888 N/A · 999 Unknown/no response                                                                                                                          |
| `Y_FM_YN`                            | N(1)   | Ever formula-fed                                                          | 1 Yes · 2 No · 9 Unknown/no response                                                                                                                                |
| `Y_FM_S1` / `_S2`                    | N(3)   | Formula feeding start age, 1st/2nd period                                 | Weeks · 888 N/A · 999 Unknown/no response                                                                                                                           |
| `Y_FM_D1` / `_D2`                    | N(3)   | Formula feeding duration, 1st/2nd period                                  | Months · 888 N/A · 999 Unknown/no response                                                                                                                          |
| `Y_MLK_ST`                           | N(3)   | Age started regular cow's milk                                            | Months · 888 N/A · 999 Unknown/no response                                                                                                                          |
| `Y_WN_ST`                            | N(3)   | Age started weaning/complementary food                                    | Months · 888 N/A · 999 Unknown/no response                                                                                                                          |
| `Y_SUP_YN`                           | N(1)   | Took supplements before age 12 months                                     | 1 Yes · 2 No · 9 Unknown/no response                                                                                                                                |
| `Y_SUP_KD1`                          | N(1)   | Supplement type: vitamin/mineral                                          | 0 No · 1 Yes · 8 N/A                                                                                                                                                |
| `Y_SUP_KD3`                          | N(1)   | Supplement type: probiotics                                               | 0 No · 1 Yes · 8 N/A                                                                                                                                                |
| `Y_SUP_KD4`                          | N(1)   | Supplement type: colostrum product                                        | 0 No · 1 Yes · 8 N/A                                                                                                                                                |
| `Y_SUP_KD7`                          | N(1)   | Supplement type: other                                                    | 0 No · 1 Yes · 8 N/A                                                                                                                                                |

### 4-2. Food Intake Survey (식품섭취조사) — Individual 24-hr Recall

_Data in HNYR_24RC DB (recall-detail level, one row per food/dish reported) rather than HNYR_ALL._

**4-2-1. Recall context variables**

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`N_DIET`|N(1)|On a special diet|1 Yes · 2 No · 9 Unknown/no response|
|`N_DIET_WHY`|N(1)|Reason for diet|1 Medical condition · 2 Weight control · 3 Other · 8 N/A · 9 Unknown/no response|
|`N_DT_DS`|C(50)|Diet reason: condition name, free text|—|
|`N_DT_ETC`|C(50)|Diet reason: other, free text|—|
|`N_DUSUAL`|C(1)|Yesterday's intake vs. usual|1 More than usual · 2 About usual · 3 Less than usual · 9 Unknown/no response|
|`N_WAT_C`|N(10.2)|Water intake, cups (200mL/cup)|Cups|
|`N_BF`|N(1)|Currently breastfeeding/nursing|1 Yes · 2 No · 8 N/A|
|`N_BFD_Y`|N(1)|Breastfed (ages 1–3 only)|1 Yes · 2 No · 8 N/A (other ages)|
|`N_DAY`|C(2)|Day of week of nutrition survey|—|
|`N_MEAL`|N(1)|Meal type|1 Breakfast · 2 Lunch · 3 Dinner · 4 Snack|
|`N_MEAL_T`|C(4)|Meal time (24hr format, e.g. 0930)|HHMM · 8881 Unknown AM · 8882 Unknown PM · 8883 Unknown/no response|
|`N_MEAL_P`|N(2)|Meal location|1 Home · 2 School/work · 5 Senior center etc. · 7 Restaurant/food establishment · 11 Temple/church · 98 Other · 99 Unknown/no response|
|`N_MTYPE`|N(2)|Meal source type|1 Home-cooked · 5 Restaurant food · 12 General food product · 14 Institutional catering · 21 Convenience food · 99 Unknown/no response|
|`N_MEAL_W`|N(1)|Ate alone or with others|1 Alone · 2 With family · 3 With non-family · 9 Unknown/no response|
|`N_DNAME`|C(50)|Dish name (as reported)|—|
|`N_DCODE`|C(5)|Dish code|5-digit code|
|`N_CD_VOL` / `N_CD_WT`|N(10)|Total cooked dish volume (mL) / weight (g)|—|
|`N_TD_VOL` / `N_TD_WT`|N(10)|Amount actually consumed: volume (mL) / weight (g)|—|
|`N_FCODE`|C(5)|Food ingredient code|5-digit code|
|`N_FNAME`|C(80)|Food ingredient name (Korean)|—|
|`N_FD_NS`|C(60)|Food name/state as reported by respondent|—|
|`N_FM_WT`|N(10.2)|Ingredient weight|g|
|`N_PRODUCT`|C(70)|Product name (branded foods)|"888" = processed food but product unknown|
|`N_CNAME`|C(50)|Manufacturer name|"888" = unknown|
|`N_AP`|N(1)|Plant vs. animal origin|1 Plant · 2 Animal|
|`N_KINDG1`|C(2)|Food group classification|01 Grains · 02 Potatoes/starches · 03 Sugars · 04 Legumes · 05 Seeds/nuts · 06 Vegetables · 07 Mushrooms · 08 Fruits · 09 Seaweed · 11 Seasonings · 12 Plant oils/fats · 13 Other (plant) · 15 Meat · 16 Eggs · 17 Fish/shellfish · 18 Dairy · 19 Animal oils/fats · 20 Other (animal) · 21 Beverages · 22 Alcohol|
|`N_FCODE3` / `N_FNAME3`|C(5) / C(40)|Tertiary (grouped) food code / name — groups foods with identical raw ingredient for "top consumed food" analysis|—|
|`NF_INTK`|N(10.2)|Food intake amount|g|
|`NF_INTK3`|N(10.2)|Food intake amount, converted to tertiary-code reference basis (for cross-food summation)|g|

**4-2-2. Per-food nutrient content** — prefix `NF_` (per food item consumed); an aggregated **per-person daily total** version of the same nutrients exists with prefix `N_` (e.g. `N_EN`, `N_PROT`, `N_CA`, etc., as seen in your dataset's column headers) — same units, summed across all foods/day.

|Nutrient group|Variables (suffix after `NF_`/`N_` prefix)|Unit|
|---|---|---|
|Energy & macronutrients|`EN` energy · `WATER` water · `PROT` protein · `FAT` fat · `CHO` carbohydrate · `TDF` dietary fiber · `SUGAR` sugar|kcal or g|
|Fatty acid classes|`SFA` saturated · `MUFA` monounsaturated · `PUFA` polyunsaturated · `N3` n-3 · `N6` n-6|g|
|Individual saturated fatty acids|`10_0` capric · `12_0` lauric · `14_0` myristic · `16_0` palmitic · `18_0` stearic · `20_0` arachidic · `22_0` behenic · `24_0` lignoceric|mg|
|Individual mono-unsaturated fatty acids|`14_1` myristoleic · `16_1` palmitoleic · `18_1` oleic · `20_1` eicosenoic · `22_1` erucic · `24_1` nervonic|mg|
|Individual poly-unsaturated fatty acids|`18_2N6` linoleic · `18_3N3` alpha-linolenic · `18_3N6` gamma-linolenic · `18_4` stearidonic · `20_2` eicosadienoic · `20_3N6` dihomo-gamma-linolenic · `20_4N6` arachidonic · `20_5N3` EPA · `22_2` docosadienoic · `22_5` DPA · `22_6N3` DHA|mg|
|Cholesterol|`CHOL`|mg|
|Minerals|`CA` calcium · `PHOS` phosphorus · `NA` sodium · `K` potassium · `MG` magnesium · `FE` iron · `ZN` zinc|mg|
|Vitamins|`VA_RAE` vitamin A (retinol activity equivalents, μg) · `VITD` vitamin D (μg) · `VITE` vitamin E (mg α-TE) · `CAROT` beta-carotene (μg) · `RETIN` retinol (μg) · `B1` thiamin (mg) · `B2` riboflavin (mg) · `NIAC` niacin (mg) · `FOLATE` folate (μg DFE) · `VITC` vitamin C (mg)|as noted|

> Note: your dataset's flat column list (`N_EN`, `N_WATER`, `N_PROT`, ... `N_FOLATE`, `N_VITC`) corresponds to the daily-total aggregated versions of this same nutrient list — i.e., one row per person with the day's total intake, rather than one row per food item.

### 4-3. Food Security (식품안정성조사)

_Household-level._

|Variable|Type|Description|Codes / Values|
|---|---|---|---|
|`LF_secur_y`|N(1)|Food security survey participation|1 Participated|
|`LF_BUYER`|N(1)|Respondent is household's food shopper/preparer|1 Yes · 2 No · 9 Unknown/no response|
|`LF_SAFE`|N(1)|Household food security status, past year|1 Enough & varied food · 2 Enough food but not varied · 3 Sometimes not enough food (financial) · 4 Often not enough food (financial) · 9 Unknown/no response|

---

_End of codebook. Covers all variables in Section IV (변수설명서) of the KNHANES 9th Cycle (2022–2024) user guide, pp. 93–236, translated and restructured for reference._