"""
KNHANES variable-code -> plain-English label resolver, parsed live from
codebook.md, for relabelling SHAP beeswarm axes for peer reviewers.

Deliberately NOT a hardcoded {code: label} dict tied to today's feature list.
Everything resolvable from codebook.md is parsed at call time, so if the
model's feature set changes, labels stay correct without editing this file.
The only exception is _ENGINEERED below: features computed inside the
notebooks (not raw KNHANES fields), which by definition have no codebook row.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CODEBOOK_PATH = os.path.join(HERE, "..", "codebook.md")

# Derived in the notebooks' feature-engineering cells, not in codebook.md.
# Add an entry here only when a new engineered (non-raw-KNHANES) feature is
# introduced upstream.
_ENGINEERED = {
    "eGFR": "Estimated kidney function (eGFR, CKD-EPI)",
    "diabetes": "Diabetes (diagnosed or HbA1c ≥ 6.5%)",
    "brush_freq": "Daily brushing frequency (count)",
    "hypertension": "Hypertension: SBP ≥ 140 OR DBP ≥ 90 mmHg",
}

_CODE_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s+(.*)$")
_RANGE_RE = re.compile(r"^([A-Za-z_]+?)(\d+)$")
_FOOTNOTE_RE = re.compile(r"[¹²³⁴⁵⁶⁷⁸⁹⁰]")

# Codebook Description text that reads badly as a display prefix -- written
# for the variable as a whole (e.g. describing its domain of values) rather
# than as a label stem for its individual levels. Kept deliberately tiny:
# only added when the raw codebook wording is actually unusable, not for
# general polish.
_PREFIX_OVERRIDE = {
    "region": "Region",
    "occp": "Occupation",
}

# Levels the notebooks recode onto an existing codebook variable that don't
# exist in the raw KNHANES code list (final.ipynb ~line 613: marri_2 is
# reassigned 0 = "never married" from marri_1==2, and 5 = "married, detail
# missing" for marri_1==1 respondents with marri_2 originally NaN). Checked
# before the codebook's own Codes/Values list.
_LEVEL_OVERRIDE = {
    ("marri_2", "0"): "Never married",
    ("marri_2", "5"): "Married (detail missing)",
}


def _clean_description(desc):
    """Strip decorative parenthetical notes and footnote markers from a
    variable-level description (e.g. '(derived; non-pregnant, fasted
    >=8hr)', trailing '¹'), but never touch per-code value labels --
    those parens (e.g. '(regional)' vs '(employer)') carry the actual
    distinguishing meaning between codes."""
    desc = desc.split(" — ")[0]
    desc = re.sub(r"\([^)]*\)", "", desc)
    desc = _FOOTNOTE_RE.sub("", desc)
    desc = desc.replace("*", "")
    desc = re.sub(r"\s{2,}", " ", desc)
    return desc.strip(" /,-–")


def _display_desc(base):
    """Cleaned description for `base`, honoring _PREFIX_OVERRIDE."""
    if base in _PREFIX_OVERRIDE:
        return _PREFIX_OVERRIDE[base]
    return _clean_description(_VAR_TABLE[base][0])


def _parse_codes_cell(codes_cell):
    codes = {}
    if not codes_cell or codes_cell.strip() in ("—", "-", ""):
        return codes
    for chunk in codes_cell.split("·"):
        m = _CODE_RE.match(chunk.strip())
        if m:
            codes[m.group(1)] = m.group(2).strip()
    return codes


def _expand_var_names(var_cell):
    """Turn the Variable column of a codebook row into a list of variable
    names. Handles single vars, comma/slash-separated vars sharing one
    description, and simple numeric ranges like `M_HL_1`-`M_HL_10`."""
    tokens = re.findall(r"`([^`]+)`", var_cell)
    if not tokens:
        return []
    if len(tokens) == 2 and ("–" in var_cell or "-" in var_cell.replace(tokens[0], "").replace(tokens[1], "")):
        m1, m2 = _RANGE_RE.match(tokens[0]), _RANGE_RE.match(tokens[1])
        if m1 and m2 and m1.group(1) == m2.group(1):
            lo, hi = int(m1.group(2)), int(m2.group(2))
            if 0 < hi - lo < 50:
                return [f"{m1.group(1)}{n}" for n in range(lo, hi + 1)]
    return tokens


def _build_var_table(text):
    table = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        var_cell, type_cell, desc_cell, codes_cell = cells[0], cells[1], cells[2], cells[3]
        if not re.match(r"^[NC]\(", type_cell):
            continue
        names = _expand_var_names(var_cell)
        if not names:
            continue
        codes = _parse_codes_cell(codes_cell)
        for n in names:
            table[n] = (desc_cell, codes)
    return table


def _build_nutrient_suffix_table(text):
    """Section 4-2-2: N_/NF_ nutrient columns are documented as suffix lists
    inside a 3-column 'Nutrient group | Variables | Unit' table, not as
    individual variable rows -- needs its own small parser."""
    suffixes = {}
    in_block = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|Nutrient group|") or line.startswith("| Nutrient group |"):
            in_block = True
            continue
        if not in_block:
            continue
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 3 or set(cells[0]) <= {"-"}:
            continue
        for chunk in cells[1].split("·"):
            m = re.match(r"^\s*`([^`]+)`\s*(.+?)\s*$", chunk.strip())
            if m:
                suffixes[m.group(1)] = m.group(2)
    return suffixes


_TEXT = open(CODEBOOK_PATH, encoding="utf-8").read()
_VAR_TABLE = _build_var_table(_TEXT)
_NUTRIENT_SUFFIX = _build_nutrient_suffix_table(_TEXT)

_warned = set()


def _resolve_dummy(name):
    if "_" not in name:
        return None
    base, level = name.rsplit("_", 1)
    if base not in _VAR_TABLE:
        return None
    _, codes = _VAR_TABLE[base]
    prefix = _display_desc(base)
    if level == "nan":
        return f"{prefix}: Missing/not reported"
    level_key = level[:-2] if level.endswith(".0") else level
    if (base, level_key) in _LEVEL_OVERRIDE:
        return f"{prefix}: {_LEVEL_OVERRIDE[(base, level_key)]}"
    if level_key in codes:
        return f"{prefix}: {codes[level_key]}"
    return None


def _resolve_nutrient(name):
    for prefix in ("N_", "NF_"):
        if name.startswith(prefix):
            suffix = name[len(prefix):]
            if suffix in _NUTRIENT_SUFFIX:
                kind = "Daily total" if prefix == "N_" else "Per-food"
                return f"{kind} {_NUTRIENT_SUFFIX[suffix]}"
    return None


def label_for(name):
    """Resolve one feature-column name to a plain-English label. Falls back
    to the raw code (with a one-time printed warning) if nothing matches,
    rather than guessing -- so gaps are visible instead of silently wrong."""
    if name in _ENGINEERED:
        return _ENGINEERED[name]
    if name in _VAR_TABLE:
        return _display_desc(name)
    dummy = _resolve_dummy(name)
    if dummy:
        return dummy
    nutrient = _resolve_nutrient(name)
    if nutrient:
        return nutrient
    if name not in _warned:
        print(f"[codebook_labels] WARNING: no codebook match for '{name}', showing raw code")
        _warned.add(name)
    return name


def label_list(names):
    return [label_for(n) for n in names]
