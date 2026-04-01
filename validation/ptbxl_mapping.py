"""
PTB-XL dataset utilities for validation.

Handles: loading ptbxl_database.csv, SCP code → finding_type mapping,
record path resolution, and fiducial annotation loading.
"""

from __future__ import annotations
import ast
import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import wfdb

PTBXL_DIR = Path(
    os.environ.get(
        "PTBXL_DIR",
        "/Users/amirsadjadtaleban/Documents/PTBXL/"
        "ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1",
    )
)

# SCP code → YouOwnECG finding_type (None = not mapped / skip)
SCP_TO_FINDING: dict[str, Optional[str]] = {
    "NORM":  None,
    "SR":    None,
    "SBRAD": "sinus_bradycardia",
    "STACH": "sinus_tachycardia",
    "AFIB":  "afib",
    "AFLT":  "aflutter",
    "SARRH": None,
    "SVTAC": "svt",
    "PSVT":  "svt",
    "PAC":   None,
    "PVC":   None,
    "BIGU":  "bigeminy",
    "TRIGU": "trigeminy",
    "1AVB":  "first_degree_avb",
    "2AVB":  "second_degree_avb",
    "3AVB":  "complete_avb",
    "CLBBB": "lbbb",
    "ILBBB": None,
    "CRBBB": "rbbb",
    "IRBBB": None,
    "LAFB":  "lafb",
    "LPFB":  "lpfb",
    "IVCD":  None,
    "WPW":   "wpw_pattern",
    "PACE":  None,
    "LVH":   "lvh",
    "RVH":   "rvh",
    "SEHYP": None,
    "LAO/LAE": "lae",
    "RAO/RAE": "rae",
    "HVOLT": None,
    "LVOLT": "low_voltage",
    "AMI":   "anterior_stemi",
    "ASMI":  "anterior_stemi",
    "ALMI":  "lateral_stemi",
    "IMI":   "inferior_stemi",
    "ILMI":  "inferior_stemi",
    "IPLMI": "inferior_stemi",
    "IPMI":  "inferior_stemi",
    "LMI":   "lateral_stemi",
    "PMI":   None,
    "INJAL": "possible_stemi",
    "INJAS": "possible_stemi",
    "INJIL": "possible_stemi",
    "INJIN": "possible_stemi",
    "INJLA": "possible_stemi",
    "ISC_":  None,
    "ISCAN": None,
    "ISCAS": None,
    "ISCAL": None,
    "ISCIL": None,
    "ISCIN": None,
    "ISCLA": None,
    "NDT":   None,
    "NST_":  None,
    "LNGQT": "long_qt",
    "INVT":  None,
    "LOWT":  None,
    "NT_":   None,
    "STD_":  None,
    "STE_":  None,
    "DIG":   None,
    "ANEUR": None,
    "EL":    None,
    "QWAVE": None,
    "TAB_":  None,
    "PRC(S)": "pericarditis",
}

# Fiducial aux_note label → FPT column index
FIDUCIAL_LABEL_TO_COL: dict[str, int] = {
    "p-wave onset":        0,
    "p-wave peak":         1,
    "p-wave offset":       2,
    "QRS onset":           3,
    "Q peak":              4,
    "R peak":              5,
    "S peak":              6,
    "QRS offset":          7,
    # L point (col 8) skipped — not in our standard set
    "t-wave onset":        9,
    "t-wave peak":         10,
    "t-wave offset":       11,
}

FIDUCIAL_NAMES = {
    0: "pon", 1: "ppeak", 2: "poff",
    3: "qrson", 4: "q", 5: "r", 6: "s", 7: "qrsoff",
    9: "ton", 10: "tpeak", 11: "toff",
}

# Lead name normalisation (PTB-XL uses "AVF"; we use "aVF")
_LEAD_NORM = {"AVF": "aVF", "AVL": "aVL", "AVR": "aVR"}

# Conditions evaluated in Module C
VALIDATED_CONDITIONS = [
    "lbbb", "rbbb", "first_degree_avb", "lafb", "wpw_pattern",
    "afib", "lvh", "anterior_stemi", "inferior_stemi", "lateral_stemi",
    "long_qt", "pericarditis", "low_voltage",
]


def load_database(min_likelihood: float = 50.0) -> pd.DataFrame:
    """Load ptbxl_database.csv; parse scp_codes dict column."""
    path = PTBXL_DIR / "ptbxl_database.csv"
    df = pd.read_csv(path)
    df["scp_codes"] = df["scp_codes"].apply(_parse_scp)
    return df


def _parse_scp(raw) -> dict[str, float]:
    if pd.isna(raw):
        return {}
    try:
        return ast.literal_eval(raw)
    except Exception:
        return {}


def get_positive_findings(scp_codes: dict, min_likelihood: float = 50.0) -> set[str]:
    """Return set of finding_type strings that are positive for this record."""
    findings = set()
    for code, likelihood in scp_codes.items():
        if likelihood < min_likelihood:
            continue
        mapped = SCP_TO_FINDING.get(code)
        if mapped:
            findings.add(mapped)
    return findings


def record_hr_path(filename_hr: str) -> Path:
    """Convert PTB-XL filename_hr column to absolute .hea path."""
    return PTBXL_DIR / (filename_hr + ".hea")


def load_gt_fiducials(ecg_id: int, lead: str) -> Optional[dict[int, int]]:
    """
    Load ground-truth fiducial annotations for one record + lead.

    Returns dict mapping FPT column index → list of sample positions
    (one per beat), or None if the file doesn't exist.
    """
    subfolder = f"{(ecg_id - 1) // 1000 * 1000:05d}"
    norm_lead = _LEAD_NORM.get(lead, lead)
    # Try normalised lead name, then original
    for try_lead in [norm_lead, lead]:
        atr_path = (
            PTBXL_DIR / "fiducial_points" / "ecgdeli"
            / subfolder
            / f"{ecg_id:05d}_points_lead_{try_lead}"
        )
        full = atr_path.with_suffix(".atr")
        if not full.exists():
            continue
        ann = wfdb.rdann(str(atr_path), extension="atr")
        result: dict[int, list[int]] = {}
        for sample, aux in zip(ann.sample, ann.aux_note):
            col = FIDUCIAL_LABEL_TO_COL.get(aux)
            if col is not None:
                result.setdefault(col, []).append(int(sample))
        return result
    return None


def load_gt_fiducials_global(ecg_id: int) -> Optional[dict[int, list[int]]]:
    """Load the global (consensus) annotation file for a record."""
    subfolder = f"{(ecg_id - 1) // 1000 * 1000:05d}"
    atr_path = (
        PTBXL_DIR / "fiducial_points" / "ecgdeli"
        / subfolder
        / f"{ecg_id:05d}_points_global"
    )
    full = atr_path.with_suffix(".atr")
    if not full.exists():
        return None
    ann = wfdb.rdann(str(atr_path), extension="atr")
    result: dict[int, list[int]] = {}
    for sample, aux in zip(ann.sample, ann.aux_note):
        col = FIDUCIAL_LABEL_TO_COL.get(aux)
        if col is not None:
            result.setdefault(col, []).append(int(sample))
    return result
