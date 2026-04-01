"""
ECG visualisation helpers — Python port companion.

plot_12lead : annotated 12-lead ECG in standard clinical layout (4 rows × 3 columns).
plot_single : annotated single-lead ECG (used internally and by tests).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Standard clinical lead order and layout (4 rows × 3 cols)
_LEAD_GRID = [
    ['I',   'AVR', 'V1'],
    ['II',  'AVL', 'V2'],
    ['III', 'AVF', 'V3'],
    ['II',  'V4',  'V5'],   # row 4: long rhythm strip (II) + V4/V5
]
# Row 3 of the 4th row is V6 in some layouts; we use V5/V6 to fit 12 leads cleanly
_LEAD_GRID_FULL = [
    ['I',   'AVR', 'V1'],
    ['II',  'AVL', 'V2'],
    ['III', 'AVF', 'V3'],
    ['II',  'V4',  'V5'],
    ['V6',  '',    ''],
]

# FPT column indices
_COL = {
    'Pon': 0, 'Ppeak': 1, 'Poff': 2,
    'QRSon': 3, 'Q': 4, 'R': 5, 'S': 6, 'QRSoff': 7,
    'Ton': 9, 'Tpeak': 10, 'Toff': 11,
}

_MARKER_STYLE = {
    'Pon':    ('limegreen',   'o', 4,  'Pon'),
    'Ppeak':  ('green',       'D', 5,  'Ppeak'),
    'Poff':   ('darkgreen',   'o', 4,  'Poff'),
    'R':      ('red',         'o', 6,  'R'),
    'Q':      ('orange',      'v', 4,  'Q'),
    'S':      ('darkorange',  '^', 4,  'S'),
    'Ton':    ('deepskyblue', '<', 4,  'Ton'),
    'Tpeak':  ('navy',        'o', 5,  'Tpeak'),
    'Toff':   ('steelblue',   '>', 4,  'Toff'),
}


def _scatter_on_ax(ax, sig_1d, fpt, legend_set):
    """Add fiducial scatter markers to an existing Axes."""
    for name, (col, marker, size, label) in _MARKER_STYLE.items():
        ci = _COL[name]
        if fpt is None:
            continue
        idx = fpt[:, ci].astype(int)
        valid = (idx > 0) & (idx < len(sig_1d))
        if not valid.any():
            continue
        lbl = label if label not in legend_set else '_'
        ax.scatter(idx[valid], sig_1d[idx[valid]],
                   color=col, marker=marker, s=size * 4,
                   zorder=5, label=lbl, linewidths=0)
        legend_set.add(label)


def plot_12lead(signal, fs, fpt_cell, lead_names,
                title='', out_file=None, patient_info=None):
    """Plot an annotated 12-lead ECG in standard clinical layout.

    Parameters
    ----------
    signal     : (N, C) numpy array, C must be len(lead_names)
    fs         : sampling frequency (Hz)
    fpt_cell   : list of C per-channel FPT arrays (each (n_beats, 13)), or None entries
    lead_names : list of C lead name strings matching signal columns
    title      : figure suptitle
    out_file   : if given, save the PNG to this path
    patient_info : optional dict with keys like 'ecg_id', 'condition', 'heart_axis'

    Returns
    -------
    fig : matplotlib Figure
    """
    signal = np.asarray(signal, dtype=float)
    if signal.ndim == 1:
        signal = signal[:, np.newaxis]
    if signal.shape[0] < signal.shape[1]:
        signal = signal.T
    N, C = signal.shape

    lead_upper = [ln.upper().replace(' ', '') for ln in lead_names]

    # Build lead index lookup: lead_name → (signal_col, fpt)
    lead_data = {}
    for ch, ln in enumerate(lead_upper):
        fpt = fpt_cell[ch] if (fpt_cell is not None and ch < len(fpt_cell)) else None
        lead_data[ln] = (signal[:, ch], fpt)

    # Determine which leads are present
    all_leads_ordered = ['I', 'II', 'III', 'AVR', 'AVL', 'AVF',
                         'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
    present = [ln for ln in all_leads_ordered if ln in lead_data]

    # Grid: 4 rows × 3 cols; row 4 = full-width rhythm strip (lead II) + remaining
    nrows = 4 if len(present) <= 12 else 5
    fig = plt.figure(figsize=(20, nrows * 2.2))
    fig.patch.set_facecolor('#f8f8f8')

    if patient_info:
        info_str = '  |  '.join(
            f"{k}: {v}" for k, v in patient_info.items() if v
        )
        full_title = f"{title}\n{info_str}" if title else info_str
    else:
        full_title = title

    fig.suptitle(full_title, fontsize=10, y=1.01, fontweight='bold')

    # Layout: first 9 leads in 3×3, then bottom row is rhythm strip (II) + V4+V5+V6
    layout_leads = [
        ('I',   0, 0), ('AVR', 0, 1), ('V1', 0, 2),
        ('II',  1, 0), ('AVL', 1, 1), ('V2', 1, 2),
        ('III', 2, 0), ('AVF', 2, 1), ('V3', 2, 2),
    ]
    bottom_leads = ['V4', 'V5', 'V6']

    gs_top = gridspec.GridSpec(3, 3, figure=fig,
                               top=0.93, bottom=0.32,
                               hspace=0.4, wspace=0.25)
    gs_bot = gridspec.GridSpec(1, 3, figure=fig,
                               top=0.27, bottom=0.05,
                               hspace=0, wspace=0.25)

    legend_set = set()

    def _draw(ax, ln):
        if ln not in lead_data:
            ax.set_visible(False)
            return
        sig_1d, fpt = lead_data[ln]
        x = np.arange(len(sig_1d))
        ax.plot(x, sig_1d, 'k-', lw=0.6)
        _scatter_on_ax(ax, sig_1d, fpt, legend_set)
        ax.set_title(ln, fontsize=8, pad=2, fontweight='bold')
        ax.set_xlim(0, len(sig_1d))
        ax.tick_params(labelsize=6)
        # Light grid at 0.2 s (= 0.2*fs samples) intervals
        step = int(round(0.2 * fs))
        xticks = np.arange(0, len(sig_1d), step)
        ax.set_xticks(xticks)
        ax.set_xticklabels([f"{t/fs:.1f}" for t in xticks], fontsize=5)
        ax.set_ylabel('mV', fontsize=5)
        ax.axhline(0, color='gray', lw=0.3, ls='--')
        ax.set_facecolor('#ffffff')

    for ln, row, col in layout_leads:
        ax = fig.add_subplot(gs_top[row, col])
        _draw(ax, ln)

    for i, ln in enumerate(bottom_leads):
        ax = fig.add_subplot(gs_bot[0, i])
        _draw(ax, ln)

    # Legend at the bottom
    handles, labels = [], []
    for name, (col, marker, size, label) in _MARKER_STYLE.items():
        handles.append(plt.scatter([], [], color=col, marker=marker,
                                   s=size * 4, label=label))
        labels.append(label)
    fig.legend(handles, labels, loc='lower center', ncol=9,
               fontsize=7, bbox_to_anchor=(0.5, -0.02),
               frameon=True, framealpha=0.8)

    if out_file:
        fig.savefig(out_file, dpi=130, bbox_inches='tight')
        plt.close(fig)

    return fig


def plot_single(sig_1d, fs, fpt, title='ECG Annotation', out_file=None):
    """Plot a single-lead annotated ECG and optionally save to PNG.

    Parameters
    ----------
    sig_1d   : 1-D numpy array
    fs       : sampling frequency (Hz)
    fpt      : (n_beats, 13) FPT array
    title    : plot title
    out_file : optional output PNG path
    """
    sig_1d = np.asarray(sig_1d, dtype=float).ravel()
    t = np.arange(len(sig_1d)) / fs

    fig, ax = plt.subplots(figsize=(14, 3.5))
    ax.plot(t, sig_1d, 'k-', lw=0.7, label='ECG')

    legend_set = set()
    for name, (col_color, marker, size, label) in _MARKER_STYLE.items():
        ci = _COL[name]
        if fpt is None:
            continue
        idx = fpt[:, ci].astype(int)
        valid = (idx > 0) & (idx < len(sig_1d))
        if not valid.any():
            continue
        lbl = label if label not in legend_set else '_'
        ax.scatter(t[idx[valid]], sig_1d[idx[valid]],
                   color=col_color, marker=marker, s=size * 5,
                   zorder=5, label=lbl)
        legend_set.add(label)

    ax.set_title(title, fontsize=9)
    ax.set_xlabel('Time (s)', fontsize=8)
    ax.set_ylabel('Amplitude (mV)', fontsize=8)
    ax.axhline(0, color='gray', lw=0.3, ls='--')
    ax.legend(loc='upper right', fontsize=7, ncol=5, framealpha=0.7)
    ax.set_facecolor('#fafafa')
    plt.tight_layout()

    if out_file:
        fig.savefig(out_file, dpi=130, bbox_inches='tight')
        plt.close(fig)

    return fig
