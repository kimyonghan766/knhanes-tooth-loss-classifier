# O_TC-COUNT
Binary classification of severe tooth loss (<20 teeth) in Korean adults aged 50+ using KNHANES IX survey data. Compares Logistic Regression, SVM, and KNN with SMOTE-based class balancing.

# Tooth Loss Prediction

Binary classification of severe tooth loss in Korean adults aged 50+ using machine learning.

## Overview

This project predicts whether an individual has fewer than 20 teeth (a clinical threshold for severe tooth loss) based on health and demographic data from the **Korea National Health and Nutrition Examination Survey IX (KNHANES IX)**.

## Dataset

- **Source:** KNHANES IX (`KNHANES9.csv`)
- **Population:** Adults aged 50 and older
- **Target:** `O_TC_` — `1` if tooth count < 20, `0` if tooth count ≥ 20
- **Class distribution:** ~2,441 (no loss) vs ~894 (severe loss)

## Features

| Column | Description |
|--------|-------------|
| age | Age |
| ho_incm | Household income |
| edu | Education level |
| BD1 | Dental visit (past year) |
| BD1_11 | Reason for dental visit |
| BS1_1 | Lifetime smoking status |
| BM7 | BMI |
| BM14 | Total cholesterol |

## Methods

- Missing value imputation (median)
- SMOTE for class imbalance
- Standardization via StandardScaler
- Model comparison using PyCaret

## Results

| Model | Accuracy | F1 |
|-------|----------|----|
| SVM - Linear Kernel | 0.8728 | 0.6673 |
| K Neighbors Classifier | 0.8612 | 0.6503 |
| Logistic Regression | 0.8603 | 0.6473 |

**Best model: SVM** (Accuracy: 0.8728, F1: 0.6673)

## Requirements

```bash
pip install pandas numpy scikit-learn imbalanced-learn pycaret
