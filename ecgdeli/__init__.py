"""
ECGdeli Python Implementation
==============================
Python port of the MATLAB ECGdeli toolbox (KIT-IBT/ECGdeli).

ECGdeli provides algorithms for ECG filtering and waveform delineation,
detecting onset/peak/offset of P wave, QRS complex, and T wave.

Original MATLAB toolbox:
  Pilia et al., "ECGdeli - An Open Source ECG Delineation Toolbox for MATLAB",
  SoftwareX 13:100639, 2021. doi:10.1016/j.softx.2020.100639

FPT (Fiducial Point Table) column layout (0-indexed):
  0  : Pon
  1  : Ppeak
  2  : Poff
  3  : QRSon
  4  : Q
  5  : R peak   ← primary column
  6  : S
  7  : QRSoff
  8  : L point  (ST midpoint)
  9  : Ton
  10 : Tpeak
  11 : Toff
  12 : classification

All sample positions are 0-indexed integers.
"""

from .filtering import (
    isoline_correction,
    ecg_high_filter,
    ecg_low_filter,
    ecg_high_low_filter,
    ecg_baseline_removal,
    notch_filter,
)
from .qrs_detection import qrs_detection, EXPECTED_R_POSITIVE
from .p_detection import p_detection
from .t_detection import t_detection
from .annotate import annotate_ecg_multi
from .mastermind import mastermind_delineate, detect_condition
from .metrics import compute_intervals, validate_markers, summarise_patient
from .visualize import plot_12lead, plot_single

__all__ = [
    "isoline_correction",
    "ecg_high_filter",
    "ecg_low_filter",
    "ecg_high_low_filter",
    "ecg_baseline_removal",
    "notch_filter",
    "qrs_detection",
    "EXPECTED_R_POSITIVE",
    "p_detection",
    "t_detection",
    "annotate_ecg_multi",
    "mastermind_delineate",
    "detect_condition",
    "compute_intervals",
    "validate_markers",
    "summarise_patient",
    "plot_12lead",
    "plot_single",
]
