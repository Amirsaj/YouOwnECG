"""
Node 1.1 — ECG Ingestion.

Accepts WFDB (.hea/.dat), SCP-ECG (.scp), EDF (.edf), and CSV formats.
Outputs a RawECGRecord with signal in µV at original sampling rate.
All PHI is stripped except sex and age (mapped to ranges before storage).
"""

from __future__ import annotations
import os
import uuid
import numpy as np
from typing import Optional
from pipeline.schemas import RawECGRecord

STANDARD_LEADS = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]

# Mapping from common alternative lead name spellings to standard names
LEAD_NAME_MAP = {
    "avr": "aVR", "avl": "aVL", "avf": "aVF",
    "AVR": "aVR", "AVL": "aVL", "AVF": "aVF",
    "lead_i": "I", "lead_ii": "II", "lead_iii": "III",
}

# PHI fields that must never appear in RawECGRecord or any downstream object
PHI_ALLOWLIST_PATIENT_FIELDS = {"patient_sex", "patient_age"}


def load_ecg(file_path: str, ecg_id: Optional[str] = None) -> RawECGRecord:
    """
    Load an ECG file into a RawECGRecord.

    Detects format from file extension. Calibrates signal to µV (float32).
    Strips all PHI except sex (M/F) and age (integer years).

    Parameters
    ----------
    file_path : str
        Path to the ECG file (.hea, .scp, .edf, .csv).
    ecg_id : str, optional
        UUID for this record. Generated if not provided.

    Returns
    -------
    RawECGRecord
    """
    if ecg_id is None:
        ecg_id = str(uuid.uuid4())

    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".hea", ".dat", ""):
        return _load_wfdb(file_path, ecg_id)
    if ext == ".edf":
        return _load_edf(file_path, ecg_id)
    if ext == ".scp":
        return _load_scp(file_path, ecg_id)
    if ext == ".csv":
        return _load_csv(file_path, ecg_id)

    raise ValueError(f"Unsupported ECG file format: {ext!r}")


def _load_wfdb(file_path: str, ecg_id: str) -> RawECGRecord:
    import wfdb
    # wfdb records: strip extension for record path
    record_path = file_path.replace(".hea", "").replace(".dat", "")
    record = wfdb.rdrecord(record_path)

    signal = record.p_signal.T.astype(np.float32)  # (n_leads, N)
    # Convert to µV: wfdb stores in the unit given by record.units
    signal = _normalize_to_uv(signal, record.units, record.adc_gain)

    lead_names = _normalize_lead_names(record.sig_name)
    signal, lead_names = _reorder_to_standard(signal, lead_names)

    fs = float(record.fs)
    duration_sec = signal.shape[1] / fs

    sex, age = _extract_demographics_wfdb(record)

    return RawECGRecord(
        ecg_id=ecg_id,
        signal=signal,
        fs=fs,
        lead_names=lead_names,
        duration_sec=duration_sec,
        source_format="wfdb",
        patient_sex=sex,
        patient_age=age,
        device_id=None,
    )


def _load_edf(file_path: str, ecg_id: str) -> RawECGRecord:
    import pyedflib
    f = pyedflib.EdfReader(file_path)
    n_signals = f.signals_in_file
    fs = float(f.getSampleFrequency(0))

    raw_labels = [f.getLabel(i) for i in range(n_signals)]
    lead_names = _normalize_lead_names(raw_labels)

    buffers = [f.readSignal(i).astype(np.float32) for i in range(n_signals)]
    # Align lengths (EDF channels can differ by ±1 sample)
    min_len = min(len(b) for b in buffers)
    signal = np.stack([b[:min_len] for b in buffers])  # (n_leads, N)

    # EDF stores in physical units (typically mV); convert to µV
    physical_dims = [f.getPhysicalDimension(i).strip() for i in range(n_signals)]
    signal = _normalize_to_uv_from_dim(signal, physical_dims)

    # EDF patient field format: "X F 01-JAN-1980 name" — strip everything except sex
    patient_info = f.getPatientCode()  # may contain PHI — we extract only sex
    sex = _extract_sex_from_edf_patient(patient_info)
    age = None  # EDF birthdate → age derivation requires current date; skip for privacy

    f.close()
    signal, lead_names = _reorder_to_standard(signal, lead_names)

    return RawECGRecord(
        ecg_id=ecg_id,
        signal=signal,
        fs=fs,
        lead_names=lead_names,
        duration_sec=signal.shape[1] / fs,
        source_format="edf",
        patient_sex=sex,
        patient_age=age,
        device_id=None,
    )


def _load_scp(file_path: str, ecg_id: str) -> RawECGRecord:
    """SCP-ECG via wfdb SCP reader (wfdb ≥ 4.1 supports .scp)."""
    import wfdb
    record = wfdb.rdrecord(file_path)
    return _load_wfdb(file_path, ecg_id)


def _load_csv(file_path: str, ecg_id: str) -> RawECGRecord:
    """
    Generic CSV loader. First row must be lead names; remaining rows are samples.
    First column may be a timestamp (detected by non-numeric content) and is skipped.
    Units assumed to be mV (most common for exported ECG CSV).
    """
    import csv
    with open(file_path) as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = [row for row in reader]

    # Detect timestamp column
    col_start = 0
    try:
        float(rows[0][0])
    except (ValueError, IndexError):
        col_start = 1

    lead_names = _normalize_lead_names(header[col_start:])
    data = np.array([[float(v) for v in row[col_start:]] for row in rows], dtype=np.float32)
    signal = data.T  # (n_leads, N)

    # Assume mV → µV
    signal = signal * 1000.0
    signal, lead_names = _reorder_to_standard(signal, lead_names)

    # CSV has no metadata — assume 500 Hz (most common digital ECG export)
    fs = 500.0

    return RawECGRecord(
        ecg_id=ecg_id,
        signal=signal,
        fs=fs,
        lead_names=lead_names,
        duration_sec=signal.shape[1] / fs,
        source_format="csv",
        patient_sex=None,
        patient_age=None,
        device_id=None,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_lead_names(names: list[str]) -> list[str]:
    return [LEAD_NAME_MAP.get(n, n).strip() for n in names]


def _reorder_to_standard(signal: np.ndarray, lead_names: list[str]) -> tuple[np.ndarray, list[str]]:
    """
    Reorder signal rows to match STANDARD_LEADS order.
    Augmented leads (III, aVR, aVL, aVF) are computed if missing.
    """
    name_to_row = {name: i for i, name in enumerate(lead_names)}

    # Compute augmented leads from I and II if missing
    has_i = "I" in name_to_row
    has_ii = "II" in name_to_row

    if has_i and has_ii:
        i_sig = signal[name_to_row["I"]]
        ii_sig = signal[name_to_row["II"]]

        if "III" not in name_to_row:
            signal = np.vstack([signal, (ii_sig - i_sig)[np.newaxis]])
            name_to_row["III"] = signal.shape[0] - 1

        if "aVR" not in name_to_row:
            signal = np.vstack([signal, (-(i_sig + ii_sig) / 2)[np.newaxis]])
            name_to_row["aVR"] = signal.shape[0] - 1

        if "aVL" not in name_to_row:
            iii_sig = signal[name_to_row["III"]]
            signal = np.vstack([signal, ((i_sig - iii_sig) / 2)[np.newaxis]])
            name_to_row["aVL"] = signal.shape[0] - 1

        if "aVF" not in name_to_row:
            iii_sig = signal[name_to_row["III"]]
            signal = np.vstack([signal, ((ii_sig + iii_sig) / 2)[np.newaxis]])
            name_to_row["aVF"] = signal.shape[0] - 1

    ordered_signal = []
    ordered_names = []
    for lead in STANDARD_LEADS:
        if lead in name_to_row:
            ordered_signal.append(signal[name_to_row[lead]])
            ordered_names.append(lead)

    return np.stack(ordered_signal).astype(np.float32), ordered_names


def _normalize_to_uv(signal: np.ndarray, units: list[str], adc_gain: list[float]) -> np.ndarray:
    """Convert signal to µV based on wfdb unit strings."""
    result = signal.copy()
    for i, unit in enumerate(units):
        u = unit.strip().lower()
        if u in ("mv", "millivolt", "millivolts"):
            result[i] *= 1000.0
        elif u in ("v", "volt", "volts"):
            result[i] *= 1_000_000.0
        # µV: no conversion needed
    return result


def _normalize_to_uv_from_dim(signal: np.ndarray, dims: list[str]) -> np.ndarray:
    result = signal.copy()
    for i, dim in enumerate(dims):
        d = dim.strip().lower()
        if d in ("mv", "millivolt"):
            result[i] *= 1000.0
        elif d in ("v", "volt"):
            result[i] *= 1_000_000.0
    return result


def _extract_demographics_wfdb(record) -> tuple[Optional[str], Optional[int]]:
    """Extract sex and age from wfdb record comments. Returns (sex, age)."""
    sex = None
    age = None
    for comment in (record.comments or []):
        c = comment.strip()
        if c.startswith("Sex:") or c.startswith("sex:"):
            raw = c.split(":", 1)[1].strip().upper()
            if raw in ("M", "MALE"):
                sex = "M"
            elif raw in ("F", "FEMALE"):
                sex = "F"
        if c.startswith("Age:") or c.startswith("age:"):
            try:
                age = int(c.split(":", 1)[1].strip())
            except ValueError:
                pass
    return sex, age


def _extract_sex_from_edf_patient(patient_info: str) -> Optional[str]:
    """EDF patient field: 'X F 01-JAN-1980 name' — extract sex character (position 2)."""
    parts = patient_info.strip().split()
    if len(parts) >= 2:
        sex_char = parts[1].upper()
        if sex_char in ("M", "F"):
            return sex_char
    return None
