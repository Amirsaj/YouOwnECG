"""
Synchronisation utilities - Python port of Sync_R_Peaks.m, Sync_Beats.m,
Check_Small_RR.m, and Check_R_Peaks_Multi.m.
"""

import numpy as np


def check_small_rr(fpt, samplerate):
    """Remove beats whose RR interval to the next beat is < 250 ms.

    Parameters
    ----------
    fpt        : (n_beats, 13) FPT array (0-indexed positions)
    samplerate : sampling frequency in Hz

    Returns
    -------
    fpt_clean     : FPT with short-RR beats removed
    removed_index : boolean mask (True = removed)
    """
    if fpt is None or len(fpt) == 0:
        return fpt, np.array([], dtype=int)

    r_peaks = fpt[:, 5].astype(float)
    rr = np.diff(r_peaks) / samplerate  # in seconds
    remove = np.where(rr < 0.25)[0] + 1  # the second of the pair
    removed_index = np.zeros(len(fpt), dtype=bool)
    removed_index[remove] = True
    fpt_clean = fpt[~removed_index]
    return fpt_clean, removed_index


def sync_r_peaks(fpt_cell, samplerate):
    """Synchronise R-peak detections across multiple FPT tables.

    For single-channel input the FPT is returned unchanged.
    For multiple channels a voting scheme retains beats detected in at least
    half of the channels (within 100 ms tolerance).

    Parameters
    ----------
    fpt_cell   : list of (n_i, 13) FPT arrays (0-indexed positions)
    samplerate : sampling frequency in Hz

    Returns
    -------
    fpt_synced      : (n_synced, 13) merged FPT
    fpt_cell_synced : list of per-channel FPTs aligned to fpt_synced
    """
    n_ch = len(fpt_cell)

    if n_ch == 1:
        return fpt_cell[0], fpt_cell

    time_limit_ms = 100.0
    # Multi-lead (12 ch): require ≥4 agreeing leads (~33%) so low-voltage leads
    # do not veto a real QRS.  Small n_ch (e.g. 3 wavelet passes in qrs_detection):
    # keep ≥50% → 2-of-3 agreement.
    if n_ch >= 8:
        min_votes = max(5, int(np.ceil(0.38 * n_ch)))
    else:
        min_votes = int(np.ceil(0.5 * n_ch))

    # Work on mutable copies
    cell = [f.copy() if f is not None else np.zeros((0, 13)) for f in fpt_cell]
    M = np.zeros((0, 13))
    synced = [np.zeros((0, 13)) for _ in range(n_ch)]

    for n in range(n_ch):
        if len(cell[n]) == 0:
            continue
        n_rows = len(cell[n])
        comp_mat = np.zeros((n_rows, n_ch), dtype=bool)
        pos_mat = np.zeros((n_rows, n_ch), dtype=int)
        samp_mat = np.zeros((n_rows, n_ch))

        for i in range(n_rows):
            r_i = cell[n][i, 5]
            for j in range(n_ch):
                if len(cell[j]) == 0:
                    continue
                diffs = 1000.0 / samplerate * np.abs(r_i - cell[j][:, 5])
                min_diff = diffs.min()
                best_pos = int(np.argmin(diffs))
                if min_diff <= time_limit_ms:
                    comp_mat[i, j] = True
                    pos_mat[i, j] = best_pos
                    samp_mat[i, j] = cell[j][best_pos, 5]

            votes = comp_mat[i].sum() / n_ch
            n_agree = int(comp_mat[i].sum())
            if n_agree >= min_votes:
                r_synced = int(round(np.median(samp_mat[i, comp_mat[i]])))
                new_row = np.zeros((1, 13))
                new_row[0, 5] = r_synced
                M = np.vstack([M, new_row])
                for ch in range(n_ch):
                    if comp_mat[i, ch]:
                        row_ch = np.zeros((1, 13))
                        row_ch[0, 5] = cell[ch][pos_mat[i, ch], 5]
                        synced[ch] = np.vstack([synced[ch], row_ch])
                    else:
                        synced[ch] = np.vstack([synced[ch], new_row])

        # Remove accepted beats
        for j in range(n_ch):
            accepted = pos_mat[pos_mat[:, j] > 0, j]
            mask = np.ones(len(cell[j]), dtype=bool)
            mask[accepted] = False
            cell[j] = cell[j][mask]

    if len(M) == 0:
        return None, synced

    # Sort by R peak position
    order = np.argsort(M[:, 5])
    fpt_out = np.zeros((len(M), 13))
    fpt_out[:, 5] = M[order, 5]
    for ch in range(n_ch):
        if len(synced[ch]) > 0:
            synced[ch] = synced[ch][order]

    # Uniqueness
    _, uniq = np.unique(fpt_out[:, 5], return_index=True)
    fpt_out = fpt_out[uniq]
    for ch in range(n_ch):
        if len(synced[ch]) > 0:
            synced[ch] = synced[ch][uniq]

    fpt_out, removed = check_small_rr(fpt_out, samplerate)
    for ch in range(n_ch):
        if len(synced[ch]) > 0:
            synced[ch] = synced[ch][~removed]

    return fpt_out, synced


def reorder_fpt_cell(fpt_cell_with_data, fpt_reference, samplerate):
    """Re-order per-channel FPTs (which have full P/T/QRS data) to match
    the ordering of fpt_reference (a synced global FPT).

    Each channel's FPT is matched to the reference R peaks by nearest-
    neighbour search within 100 ms.  Any unmatched reference beat gets a
    zero row.

    Parameters
    ----------
    fpt_cell_with_data : list of (n_i, 13) FPTs with full delineation data
    fpt_reference      : (n_beats, 13) reference FPT (sorted by R peak)
    samplerate         : sampling frequency in Hz

    Returns
    -------
    fpt_cell_aligned : list of per-channel FPTs aligned to fpt_reference
    """
    n_ref = len(fpt_reference)
    n_ch = len(fpt_cell_with_data)
    time_lim = 100.0  # ms

    aligned = []
    for ch in range(n_ch):
        src = fpt_cell_with_data[ch]
        out = np.zeros((n_ref, 13))
        if src is None or len(src) == 0:
            # Fill R column from reference so downstream detectors have a position
            out[:, 5] = fpt_reference[:, 5]
            aligned.append(out)
            continue
        for i in range(n_ref):
            r_ref = fpt_reference[i, 5]
            diffs = 1000.0 / samplerate * np.abs(r_ref - src[:, 5])
            if diffs.min() <= time_lim:
                best = int(np.argmin(diffs))
                out[i] = src[best]
            else:
                # Unmatched: keep global R as reference, zeros for the rest
                out[i, 5] = r_ref
        aligned.append(out)
    return aligned


def sync_beats(fpt_cell, samplerate):
    """Wrapper that synchronises beats across channels.

    For a single-channel list this is a no-op (returns the same FPT).

    Parameters
    ----------
    fpt_cell   : list of FPT arrays
    samplerate : sampling frequency in Hz

    Returns
    -------
    fpt_multi  : (n_beats, 13) global FPT
    fpt_cell   : list of per-channel FPTs
    """
    if len(fpt_cell) == 1:
        return fpt_cell[0], fpt_cell
    return sync_r_peaks(fpt_cell, samplerate)


def check_r_peaks_multi(signal, samplerate, fpt_multi):
    """Verify R peaks from a global FPT in a single channel.

    Searches ±50 ms around each declared R peak and re-centres the peak.

    Parameters
    ----------
    signal    : 1-D array (N,)
    samplerate: sampling frequency in Hz
    fpt_multi : (n_beats, 13) global FPT (0-indexed)

    Returns
    -------
    fpt : (n_beats, 13) channel-specific FPT with corrected R peaks
    """
    signal = np.asarray(signal, dtype=float).ravel()
    N = len(signal)
    wb = int(round(0.05 * samplerate))

    fpt = np.zeros_like(fpt_multi)
    fpt[:, 5] = fpt_multi[:, 5].copy()

    for i in range(len(fpt)):
        r0 = int(fpt_multi[i, 5])
        lo = max(r0 - wb, 0)
        hi = min(r0 + wb + 1, N)
        seg = signal[lo:hi]
        peak = int(np.argmax(np.abs(seg))) + lo
        fpt[i, 5] = peak

    return fpt
