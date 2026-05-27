"""
Standalone SHAP check — replicates testing.ipynb preprocessing through the
XGBoost fit, then compares default gain importance vs mean|SHAP|.
NOTE: uses a representative XGBoost config (not the tuned params) — the
importance RANKING is what we care about here and it's robust to this.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import shap

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "csv", "KNHANES9.csv")

# ---- replicate preprocessing ----
df = pd.read_csv(CSV)

raw_columns = ['age', 'sex', 'ho_incm', 'edu', 'BS1_1', 'BD1',
               'BM7', 'BM14', 'HE_HbA1c', 'HE_BMI', 'HE_crea', 'O_TC']
df_subset = df[raw_columns].copy()
df_subset = df_subset[df_subset['age'] >= 40]

df_subset['O_TC'] = pd.to_numeric(df_subset['O_TC'], errors='coerce')
df_subset['O_TC'] = df_subset['O_TC'].replace(-1.80e308, np.nan)
df_subset = df_subset.dropna(subset=['O_TC'])
df_subset['O_TC_'] = (df_subset['O_TC'] < 20).astype(int)

invalid_codes = [8, 9, 88, 99, 888, 999]
survey_cols = ['BS1_1', 'BD1', 'edu', 'ho_incm', 'BM7', 'BM14']
lab_cols = ['HE_HbA1c', 'HE_BMI', 'HE_crea']

df_subset[survey_cols] = df_subset[survey_cols].replace(invalid_codes, np.nan)
df_subset[lab_cols] = df_subset[lab_cols].apply(pd.to_numeric, errors='coerce')
df_subset[lab_cols] = df_subset[lab_cols].where(df_subset[lab_cols].abs() < 1e10, np.nan)
df_subset.loc[df_subset['HE_crea'] <= 0, 'HE_crea'] = np.nan

df_subset[survey_cols] = df_subset[survey_cols].apply(pd.to_numeric, errors='coerce')
df_subset[survey_cols] = df_subset[survey_cols].replace(invalid_codes, np.nan)
df_subset['BM7'] = 6 - df_subset['BM7']
df_subset['BM14'] = df_subset['BM14'].map({1: 1, 2: 0, 3: 0})
df_subset['BS1_1'] = 4 - df_subset['BS1_1']


def calculate_egfr(row):
    scr, age, sex = row['HE_crea'], row['age'], row['sex']
    if pd.isna(scr) or pd.isna(sex):
        return np.nan
    if sex == 2:
        kappa, alpha, sex_factor = 0.7, -0.241, 1.012
    else:
        kappa, alpha, sex_factor = 0.9, -0.302, 1.0
    ratio = scr / kappa
    return (142 * (min(ratio, 1) ** alpha) * (max(ratio, 1) ** -1.200)
            * (0.9938 ** age) * sex_factor)


df_subset['eGFR'] = df_subset.apply(calculate_egfr, axis=1)
df_subset = df_subset.drop(columns=['HE_crea', 'sex'])

df_subset['age_group'] = pd.cut(
    df_subset['age'], bins=[40, 50, 60, 70, 150], labels=[0, 1, 2, 3],
    include_lowest=True).cat.codes.astype(float)

feature_cols = ['age_group', 'ho_incm', 'edu', 'BS1_1', 'BD1',
                'BM7', 'BM14', 'HE_HbA1c', 'HE_BMI', 'eGFR']
X = df_subset[feature_cols].replace([np.inf, -np.inf], np.nan)
y = df_subset['O_TC_']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

imputer = SimpleImputer(strategy='median')
X_train = pd.DataFrame(imputer.fit_transform(X_train), columns=feature_cols)
X_test = pd.DataFrame(imputer.transform(X_test), columns=feature_cols)

# SMOTE inside final fit (mirrors the pipeline's refit behaviour)
X_res, y_res = SMOTE(sampling_strategy=1/1.5, random_state=42).fit_resample(X_train, y_train)

model = XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.1,
                      subsample=0.8, random_state=42, eval_metric='logloss')
model.fit(X_res, y_res)

# ---- default gain importance ----
gain = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)

# ---- SHAP (XGBoost native exact TreeSHAP; avoids shap<->xgboost version bug) ----
import xgboost as xgb
dtest = xgb.DMatrix(X_test, feature_names=feature_cols)
contribs = model.get_booster().predict(dtest, pred_contribs=True)
sv = contribs[:, :-1]  # drop bias column
mean_abs = pd.Series(np.abs(sv).mean(axis=0), index=feature_cols).sort_values(ascending=False)

# normalise both to % share for apples-to-apples
gain_pct = (gain / gain.sum() * 100).round(1)
shap_pct = (mean_abs / mean_abs.sum() * 100).round(1)

cmp = pd.DataFrame({'gain_%': gain_pct, 'shap_%': shap_pct}).fillna(0)
cmp = cmp.sort_values('shap_%', ascending=False)
print("\n=== Importance share: default gain vs mean|SHAP| ===")
print(cmp.to_string())
print(f"\nage_group  ->  gain: {gain_pct.get('age_group',0)}%   |   SHAP: {shap_pct.get('age_group',0)}%")

# ---- plots ----
plt.figure()
shap.summary_plot(sv, X_test, plot_type="bar", show=False)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "SHAP_bar.png"), dpi=120, bbox_inches="tight")
plt.close()

plt.figure()
shap.summary_plot(sv, X_test, show=False)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "SHAP_beeswarm.png"), dpi=120, bbox_inches="tight")
plt.close()
print("\nSaved: Main/SHAP_bar.png, Main/SHAP_beeswarm.png")
