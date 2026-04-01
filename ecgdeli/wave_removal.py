"""
Wave removal utilities - Python port of Remove_PQRS.m and Remove_QRST.m.

remove_pqrs : replace P wave + QRS complex with sigmoid transitions
             (used before T-wave detection)
remove_qrst : replace QRS complex + T wave with sigmoid transitions
             (used before P-wave detection)
"""

import numpy as np
from .filtering import ecg_baseline_removal


def _sigmoid_replace(signal, start, end, n1_samples, n2_samples):
    """Replace signal[start:end+1] with a sigmoid from mean(start window)
    to mean(end window)."""
    seg = signal[start: end + 1].copy()
    length = len(seg)
    y1 = np.mean(seg[:n1_samples])
    y2 = np.mean(seg[max(0, length - n2_samples):])
    xc = np.linspace(-6, 6, length)
    c = 1.0 / (1.0 + np.exp(-xc))
    return (y2 - y1) * c + y1


def remove_pqrs(signal, samplerate, fpt):
    """Replace P wave and QRS complex with a sigmoidal function.

    Parameters
    ----------
    signal     : 1-D numpy array (N,)
    samplerate : sampling frequency in Hz
    fpt        : (n_beats, 13) Fiducial Point Table (0-indexed positions)

    Returns
    -------
    replaced_signal : signal with P+QRS replaced
    interval_sigmoid: (n_beats, 2) array of [start, end] replacement intervals
    """
    signal = np.asarray(signal, dtype=float).ravel()
    N = len(signal)

    # Baseline removal
    w = 0.75
    _, baseline = ecg_baseline_removal(signal, samplerate, w, 0.75)
    w2 = 2.0
    _, baseline = ecg_baseline_removal(baseline, samplerate, w2, 0.75)
    signal = signal - baseline

    replaced = signal.copy()
    n_beats = fpt.shape[0]
    interval_sigmoid = np.full((n_beats, 2), np.nan)

    n1 = max(1, int(np.ceil(samplerate * 10e-3)))
    n2 = max(1, int(np.ceil(samplerate * 10e-3)))

    for i in range(n_beats):
        r_pos = int(fpt[i, 5])  # R peak (0-indexed)

        if i == 0:
            remove_l = int(round(r_pos / 3))
        else:
            remove_l = int(round((r_pos - int(fpt[i - 1, 5])) / 3))

        s_pos = int(fpt[i, 6]) if fpt[i, 6] > 0 else 0
        if s_pos > 0:
            remove_r = int(round(s_pos - r_pos + 50e-3 * samplerate))
        else:
            remove_r = int(round(80e-3 * samplerate))

        start = r_pos - remove_l
        end = r_pos + remove_r

        if start < 0:
            start = 0
            xc = np.linspace(-6, 6, end - start + 1)
            c = 1.0 / (1.0 + np.exp(-xc))
            seg = replaced[start: end + 1]
            y1 = np.mean(seg[:n1])
            y2 = np.mean(seg[max(0, len(seg) - n2):])
            idx = len(xc) - len(seg)
            replaced[start: end + 1] = (y2 - y1) * c[idx:] + y1
            interval_sigmoid[i] = [start, end]
        elif end >= N:
            end = N - 1
            xc = np.linspace(-6, 6, end - start + 1)
            c = 1.0 / (1.0 + np.exp(-xc))
            seg = replaced[start: end + 1]
            y1 = np.mean(seg[:n1])
            y2 = np.mean(seg[max(0, len(seg) - n2):])
            replaced[start: end + 1] = (y2 - y1) * c[:len(seg)] + y1
            interval_sigmoid[i] = [start, end]
        else:
            xc = np.linspace(-6, 6, end - start + 1)
            c = 1.0 / (1.0 + np.exp(-xc))
            seg = replaced[start: end + 1]
            y1 = np.mean(seg[:n1])
            y2 = np.mean(seg[max(0, len(seg) - n2):])
            replaced[start: end + 1] = (y2 - y1) * c + y1
            interval_sigmoid[i] = [start, end]

    return replaced, interval_sigmoid


def remove_qrst(signal, samplerate, fpt):
    """Replace QRS complex and T wave with a sigmoidal function.

    Parameters
    ----------
    signal     : 1-D numpy array (N,)
    samplerate : sampling frequency in Hz
    fpt        : (n_beats, 13) Fiducial Point Table (0-indexed positions)

    Returns
    -------
    sig_killed : signal with QRS+T replaced
    perc       : fraction of median RR interval that is replaced
    """
    signal = np.asarray(signal, dtype=float).ravel()
    N = len(signal)
    n_beats = fpt.shape[0]

    r_peaks = fpt[:, 5].astype(int)
    rr = np.diff(r_peaks)

    # Template parameters
    L1 = int(round(min(1 / 3 * np.median(rr), 500e-3 * samplerate)))
    L2 = int(round(min(2 / 3 * np.median(rr), 1000e-3 * samplerate)))
    template_len = L1 + L2 + 1
    perc = (template_len - L1 - 1 - 0.05 * samplerate) / template_len

    # Poincaré-plot-based beat selection (filter ectopics)
    if len(rr) >= 3:
        X = np.column_stack([rr[:-1], rr[1:]])
        mean_X = X.mean(axis=0)
        rot = (1 / np.sqrt(2)) * np.array([[1, -1], [1, 1]])
        score = (X - mean_X) @ rot
        d1 = np.abs(score[:, 0])
        thl1 = 2.5 * np.std(d1, ddof=1)
        idx_normal = np.where((score[:, 0] >= -thl1) & (score[:, 1] <= 0))[0] + 1
    else:
        idx_normal = np.arange(n_beats)

    if len(idx_normal) == 0:
        idx_normal = np.arange(n_beats)

    sig_killed = signal.copy()
    rr_int = np.concatenate([[rr[0]], rr])  # pad first

    for i in range(n_beats - 1):
        q_pos = int(fpt[i, 4]) if fpt[i, 4] > 0 else int(fpt[i, 5])
        remove_l = int(round(r_peaks[i] - q_pos + 30e-3 * samplerate))
        remove_r = int(round(rr_int[i] * perc))

        start = r_peaks[i] - remove_l
        end = r_peaks[i] + remove_r

        if start <= 0:
            start = 0
            xc = np.linspace(-6, 6, end + 1)
            c = 1.0 / (1.0 + np.exp(-xc))
            y1 = signal[0]
            y2 = signal[min(end + 1, N - 1)]
            sig_killed[0: end + 1] = (y2 - y1) * c + y1
        elif end >= N:
            end = N - 1
            length = end - start + 1
            xc = np.linspace(-6, 6, length)
            c = 1.0 / (1.0 + np.exp(-xc))
            y1 = signal[max(start - 1, 0)]
            y2 = signal[-1]
            sig_killed[start: end + 1] = (y2 - y1) * c + y1
        else:
            length = end - start + 1
            xc = np.linspace(-6, 6, length)
            c = 1.0 / (1.0 + np.exp(-xc))
            y1 = signal[max(start - 1, 0)]
            y2 = signal[min(end + 1, N - 1)]
            sig_killed[start: end + 1] = (y2 - y1) * c + y1

    return sig_killed, perc
