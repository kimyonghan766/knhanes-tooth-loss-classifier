import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import sklearn as sk

#load data set 
df = pd.read_csv('KNHANES9.csv') 
df_subset = (df.iloc[:, [1,9,12,15,234, 237, 303, 304, 520, 535, 496]])
age_threshold = 50 
df_subset = df_subset[df_subset['age'] >= age_threshold]
# ID, age, ho_incm, edu, BD1_11, BD2_31, BS3_1, BS3_2, BM7, BM14, O_TC
print(df_subset.head(1))

'''

For ages >= 19 
Label 0 (≥20 teeth): 4437
Label 1 (<20 teeth): 905

For ages >= 50 
Label 0 (≥20 teeth): 2441
Label 1 (<20 teeth): 894

'''


# count 
print(df_subset[pd.to_numeric(df_subset['O_TC'], errors='coerce').isna()]['O_TC'].unique())
# ^ the value that its going to drop is ['-1.80E+308'] <-- classified as NaN in the data set 
df_subset['O_TC'] = pd.to_numeric(df_subset['O_TC'], errors='coerce')
# ^ converts O_TC from strings to numbers; any value that can't be converted 
#   gets resulted to NaN <-- blank and special codes 
#   if it encounters values that are not numbers --> that gets swapped to NaN 
before_drop = len(df_subset)
df_subset = df_subset.dropna(subset=['O_TC'])
print(f"Rows droppped (NaN O_TC): {before_drop - len(df_subset)}")
# ^ removes all rows where O_TC is NaN, keeps rows with valid tooth count 
#   subset=['O_TC'] means that it only checks that column --> drops it / deletes
df_subset['O_TC_'] = (df_subset['O_TC'] < 20).astype(int)
# ^ creates a new binary label column for O_TC; 
# ^ 'astype(int) <-- computer views 1 = True; 0 = False 
# ^ 'O_TC_' <-- creates a new column 
label_counts    = df_subset['O_TC_'].value_counts()
# ^ counts how many people are in each group 0 and 1 
label_0         = label_counts[0]
label_1         = label_counts[1]
imbalance_ratio = label_0 / label_1

#PRINT count 

print(f"Age filter: >= {age_threshold}")
print(f"Label 0 (≥20 teeth): {label_0}")
print(f"Label 1 (<20 teeth): {label_1}")
print(df_subset['O_TC'].value_counts(dropna=False).head(20))
print(f"Imbalance ratio: {imbalance_ratio:.2f}")

print(df_subset['O_TC'].isna().sum())
print(df_subset['O_TC'].value_counts(dropna=False).head(20))

# Missing Value Audit 

sentinel_codes = [8, 9, 88, 99, 888, 999]

for col in df_subset.columns:
    sentinel_count      = df_subset[col].isin(sentinel_codes).sum()
    missing_percentage  = (sentinel_count / len(df_subset)) * 100
    print(f"{col}: {sentinel_count} sentinel values ({missing_percentage:.1f}%)")

'''
    ID: 0 sentinel values (0.0%)
    age: 0 sentinel values (0.0%)
    ho_incm: 0 sentinel values (0.0%)
    edu: 0 sentinel values (0.0%)
    BD1_11: 203 sentinel values (6.1%)
    BD2_31: 506 sentinel values (15.2%)
    BS3_1: 853 sentinel values (25.6%)
    BS3_2: 1198 sentinel values (35.9%)
    BM7: 47 sentinel values (1.4%)
    BM14: 47 sentinel values (1.4%)
    O_TC: 70 sentinel values (2.1%)
    O_TC_: 0 sentinel values (0.0%)
'''

# Standardization

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

# For Logistic Regression and SVM — normalize all features
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# For RF, XGBoost, LightGBM — NO standardization needed
X_train_tree = X_train.copy()
X_test_tree  = X_test.copy()

# class imbalance 
from imblearn.over_sampling import SMOTE

smote = SMOTE(k_neighbors=5, random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

print("Before SMOTE:", pd.Series(y_train).value_counts().to_dict())
print("After SMOTE: ", pd.Series(y_train_resampled).value_counts().to_dict())