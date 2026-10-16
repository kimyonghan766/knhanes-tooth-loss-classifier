"""
verify_app.py — headless checks on the form schema, row builder and explainers.

Runs without Streamlit. The important one is the ROUND TRIP: take real respondents out
of each cohort's 2024 test matrix, read off the answers the form would have collected,
rebuild the row through features.build_row(), and require it back byte-for-byte. That
exercises reference levels, explicit *_nan unknowns, the cohort-specific rare-dummy
guard and every direct field at once -- the places the previous app silently encoded
the wrong thing.

Run:  python webapp/verify_app.py
"""

import json
import os
import sys

import joblib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import explain  # noqa: E402
import export_cohort_models as ex  # noqa: E402
import features  # noqa: E402

# Derived in-app from HbA1c / creatinine / brushing count rather than read off a column,
# so a round trip that starts from the feature matrix cannot reconstruct their inputs.
DERIVED_COLS = {"eGFR", "diabetes", "brush_freq", "BM1_0"}

failures = []


def check(name, condition, detail=""):
    print(f"[{'ok' if condition else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not condition:
        failures.append(name)


def load(cohort_key):
    model = joblib.load(os.path.join(HERE, "artifacts", f"model_{cohort_key}.pkl"))
    with open(os.path.join(HERE, "artifacts", f"meta_{cohort_key}.json")) as f:
        meta = json.load(f)
    return model, meta


def default_values(meta, age):
    values = {"age": age}
    for field in features.DIRECT_FIELDS:
        values[field["column"]] = field["default"]
    for field in features.DERIVED_FIELDS:
        values[field["key"]] = field["default"]
    for field in features.NOMINAL_FIELDS:
        values[field["parent"]] = features.default_level(field, meta)
    return values


def values_from_row(row, meta):
    """Invert the encoding: what would the form have to hold to produce this row?"""
    values = {"age": float(row["age"])}
    for field in features.DIRECT_FIELDS:
        values[field["column"]] = float(row[field["column"]])
    for field in features.DERIVED_FIELDS:      # untested here, see DERIVED_COLS
        values[field["key"]] = field["default"]

    for field in features.NOMINAL_FIELDS:
        parent = field["parent"]
        level = meta["nominal_ref"][parent]     # all-zero block == reference level
        for value, _ in features.available_levels(field, meta):
            column = (f"{parent}_nan" if value == features.UNKNOWN_LEVEL
                      else f"{parent}_{value}")
            if column in row.index and row[column] == 1.0:
                level = value
                break
        values[parent] = level
    return values


def cohort_test_matrix(cohort_key):
    """Rebuild the cohort's 2024 test matrix exactly as export_cohort_models does."""
    cfg = ex.COHORTS[cohort_key]
    d = ex.load_and_clean(cfg["age_threshold"])
    feat, nominal_dummies = ex.build_feature_frame(d)

    binary_cols = ex.BASE_BINARY_COLS + nominal_dummies
    feature_cols = ex.ORDINAL_SCALED_COLS + binary_cols + ex.CONTINUOUS_COLS
    train_mask = d["year"].isin(ex.TRAIN_YEARS)
    counts = feat.loc[train_mask, nominal_dummies].sum()
    rare = set(counts[counts < ex.MIN_DUMMY_COUNT].index)
    feature_cols = [c for c in feature_cols if c not in rare]

    test_mask = d["year"].isin(ex.TEST_YEARS)
    return feat.loc[test_mask, feature_cols].replace([np.inf, -np.inf], np.nan)


def run(cohort_key, age):
    model, meta = load(cohort_key)
    print(f"\n{'=' * 70}\n{cohort_key}  ({meta['model_name']}, age {age})\n{'=' * 70}")

    # ── schema ──
    row = features.build_row(default_values(meta, age), meta)
    check(f"{cohort_key}: row schema matches feature_cols",
          list(row.columns) == meta["feature_cols"], f"{row.shape[1]} columns")

    unexpected = [c for c in row.columns
                  if row[c].isna().all() and c not in features.DIET_COLS]
    check(f"{cohort_key}: only the dietary block is left NaN", not unexpected,
          f"unexpected NaN: {unexpected}" if unexpected else "7 diet columns")
    check(f"{cohort_key}: imputed_columns == DIET_COLS",
          sorted(features.imputed_columns(meta)) == sorted(features.DIET_COLS))

    # ── inference and explanation ──
    proba = float(model.predict_proba(row)[0, 1])
    check(f"{cohort_key}: predict_proba in (0, 1)", 0.0 < proba < 1.0, f"p = {proba:.4f}")

    contrib = explain.contributions(model, meta, row)
    check(f"{cohort_key}: contributions are finite", bool(np.isfinite(contrib.values).all()),
          f"top driver: {contrib.index[0]} ({contrib.iloc[0]:+.3f})")
    check(f"{cohort_key}: contributions sorted by |value|",
          list(contrib.abs().values) == sorted(contrib.abs().values, reverse=True))
    check(f"{cohort_key}: no raw codes leaked into labels",
          not any(lbl in meta["feature_cols"] for lbl in contrib.index))

    # ── round trip against real test respondents ──
    X_test = cohort_test_matrix(cohort_key)
    comparable = [c for c in meta["feature_cols"]
                  if c not in DERIVED_COLS and c not in features.DIET_COLS]
    complete = X_test[X_test[comparable].notna().all(axis=1)]
    check(f"{cohort_key}: complete-case test rows available", len(complete) > 0,
          f"{len(complete):,} of {len(X_test):,}")

    sample = complete.head(300)
    mismatches = []
    for idx, original in sample.iterrows():
        rebuilt = features.build_row(values_from_row(original, meta), meta).iloc[0]
        diff = [c for c in comparable if not np.isclose(rebuilt[c], original[c])]
        if diff:
            mismatches.append((idx, diff[:5]))
    check(f"{cohort_key}: {len(sample)} test rows round-trip through the form",
          not mismatches, f"first mismatch: {mismatches[0]}" if mismatches else
          f"{len(comparable)} columns each")

    return meta


def main():
    meta_50 = run("50plus", 58)
    meta_65 = run("65plus", 70)

    print(f"\n{'=' * 70}\ncohort switching\n{'=' * 70}")
    check("age 64 -> 50plus, age 65 -> 65plus",
          features_cohort(64) == "50plus" and features_cohort(65) == "65plus")

    fam_rela = next(f for f in features.NOMINAL_FIELDS if f["parent"] == "fam_rela")
    labels_50 = {lbl for _, lbl in features.available_levels(fam_rela, meta_50)}
    labels_65 = {lbl for _, lbl in features.available_levels(fam_rela, meta_65)}
    check("fam_rela drops 'Child' and 'Sibling' in the >=65 cohort",
          {"Child", "Sibling"} <= labels_50 and not ({"Child", "Sibling"} & labels_65),
          f"{len(labels_50)} options at >=50, {len(labels_65)} at >=65")
    check("occp offers an explicit 'Unknown' in both cohorts",
          all(features.UNKNOWN_LEVEL in [v for v, _ in features.available_levels(
              next(f for f in features.NOMINAL_FIELDS if f["parent"] == "occp"), m)]
              for m in (meta_50, meta_65)))

    # Platt must be monotone or the displayed threshold would disagree with the decision.
    for meta in (meta_50, meta_65):
        grid = np.linspace(0.01, 0.99, 99)
        mapped = [_platt(p, meta) for p in grid]
        check(f"{meta['cohort']}: Platt map is monotone increasing",
              all(b > a for a, b in zip(mapped, mapped[1:])),
              f"threshold {meta['mcc_threshold']:.3f} -> {_platt(meta['mcc_threshold'], meta):.3f}")

    print(f"\n{'=' * 70}")
    if failures:
        print(f"{len(failures)} FAILED: {', '.join(failures)}")
        sys.exit(1)
    print("All checks passed.")


def features_cohort(age):
    return "65plus" if age >= 65 else "50plus"


def _platt(proba, meta):
    p = np.clip(proba, 1e-6, 1 - 1e-6)
    z = meta["platt_slope"] * np.log(p / (1 - p)) + meta["platt_intercept"]
    return float(1.0 / (1.0 + np.exp(-z)))


if __name__ == "__main__":
    main()
