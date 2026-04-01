#!/usr/bin/env python3
"""Generate publication-quality figures from validation results."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

plt.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'axes.grid': False,
})

RESULTS_DIR = Path(__file__).parent.parent / 'validation' / 'results'
FIGURES_DIR = Path(__file__).parent / 'figures'

COLORS = {
    'primary': '#2C3E50',
    'secondary': '#E74C3C',
    'accent': '#3498DB',
    'light': '#BDC3C7',
    'green': '#27AE60',
    'orange': '#F39C12',
}

FIDUCIAL_ORDER = ['pon', 'ppeak', 'poff', 'qrson', 'r', 's', 'qrsoff', 'ton', 'tpeak', 'toff']
FIDUCIAL_LABELS = {
    'pon': 'P-on', 'ppeak': 'P-peak', 'poff': 'P-off',
    'qrson': 'QRS-on', 'r': 'R', 's': 'S', 'qrsoff': 'QRS-off',
    'ton': 'T-on', 'tpeak': 'T-peak', 'toff': 'T-off',
}


def _save(fig, name):
    """Save figure as both PNG and PDF."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'pdf'):
        path = FIGURES_DIR / f'{name}.{ext}'
        fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {name}.png and {name}.pdf')


def fig1_fiducial_error_distribution():
    """Histograms of error distribution for each fiducial type in a 2x5 grid."""
    csv = RESULTS_DIR / 'fiducial_accuracy.csv'
    if not csv.exists():
        print('  SKIP fig1: fiducial_accuracy.csv not found')
        return
    df = pd.read_csv(csv)

    fig, axes = plt.subplots(2, 5, figsize=(12, 5))
    axes = axes.flatten()

    for i, fid in enumerate(FIDUCIAL_ORDER):
        ax = axes[i]
        sub = df[df['fiducial'] == fid]
        detected = sub[sub['detected'] == True]
        det_rate = len(detected) / len(sub) * 100 if len(sub) > 0 else 0
        errors = detected['error_ms'].dropna()

        if len(errors) > 0:
            mae = errors.abs().mean()
            clipped = errors.clip(-50, 50)
            ax.hist(clipped, bins=40, color=COLORS['accent'], alpha=0.7,
                    edgecolor='white', linewidth=0.3)
            ax.axvline(0, color=COLORS['secondary'], linewidth=0.8, linestyle='--')
            ax.text(0.97, 0.95, f'MAE={mae:.1f} ms\nDet={det_rate:.0f}%',
                    transform=ax.transAxes, ha='right', va='top', fontsize=7,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=COLORS['light'], alpha=0.9))
        else:
            ax.text(0.5, 0.5, f'No detections\nDet={det_rate:.0f}%',
                    transform=ax.transAxes, ha='center', va='center', fontsize=8)

        ax.set_title(FIDUCIAL_LABELS.get(fid, fid), fontsize=9, fontweight='bold')
        if i >= 5:
            ax.set_xlabel('Error (ms)', fontsize=8)
        if i % 5 == 0:
            ax.set_ylabel('Count', fontsize=8)
        ax.tick_params(labelsize=7)

    fig.suptitle('Fiducial Detection Error Distribution', fontsize=11, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save(fig, 'fig1_fiducial_error_distribution')


def fig2_bland_altman():
    """Bland-Altman plots for PR, QRS, QT, QTc intervals."""
    csv = RESULTS_DIR / 'measurement_accuracy.csv'
    if not csv.exists():
        print('  SKIP fig2: measurement_accuracy.csv not found')
        return
    df = pd.read_csv(csv)

    measurements = ['pr_ms', 'qrs_ms', 'qt_ms', 'qtc_bazett_ms']
    titles = ['PR Interval', 'QRS Duration', 'QT Interval', 'QTc (Bazett)']

    # Fall back to qtc_ms if qtc_bazett_ms missing
    available = df['measurement'].unique()
    if 'qtc_bazett_ms' not in available and 'qtc_ms' in available:
        measurements[3] = 'qtc_ms'
        titles[3] = 'QTc'

    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))

    for i, (meas, title) in enumerate(zip(measurements, titles)):
        ax = axes[i]
        sub = df[df['measurement'] == meas].dropna(subset=['gt_value', 'pred_value'])

        if len(sub) == 0:
            ax.text(0.5, 0.5, 'No data', transform=ax.transAxes,
                    ha='center', va='center')
            ax.set_title(title, fontsize=9, fontweight='bold')
            continue

        gt = sub['gt_value'].values
        pred = sub['pred_value'].values
        mean_vals = (gt + pred) / 2
        diff = pred - gt
        bias = diff.mean()
        sd = diff.std()
        upper = bias + 1.96 * sd
        lower = bias - 1.96 * sd

        ax.scatter(mean_vals, diff, s=8, alpha=0.4, color=COLORS['accent'],
                   edgecolors='none')
        ax.axhline(bias, color=COLORS['primary'], linewidth=1, label=f'Bias={bias:.1f}')
        ax.axhline(upper, color=COLORS['secondary'], linewidth=0.8, linestyle='--',
                   label=f'+1.96SD={upper:.1f}')
        ax.axhline(lower, color=COLORS['secondary'], linewidth=0.8, linestyle='--',
                   label=f'-1.96SD={lower:.1f}')

        ax.set_title(title, fontsize=9, fontweight='bold')
        ax.set_xlabel('Mean (ms)', fontsize=8)
        if i == 0:
            ax.set_ylabel('Difference (Pred - GT) (ms)', fontsize=8)
        ax.tick_params(labelsize=7)
        ax.legend(fontsize=6, loc='best', framealpha=0.9)

    fig.suptitle('Bland-Altman Analysis of Interval Measurements',
                 fontsize=11, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save(fig, 'fig2_bland_altman')


def fig3_heart_rate_scatter():
    """Scatter plot of predicted vs ground truth heart rate."""
    csv = RESULTS_DIR / 'measurement_accuracy.csv'
    if not csv.exists():
        print('  SKIP fig3: measurement_accuracy.csv not found')
        return
    df = pd.read_csv(csv)
    hr = df[df['measurement'] == 'heart_rate_bpm'].dropna(subset=['gt_value', 'pred_value'])

    if len(hr) == 0:
        print('  SKIP fig3: no heart_rate_bpm data')
        return

    gt = hr['gt_value'].values
    pred = hr['pred_value'].values

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(gt, pred, s=15, alpha=0.5, color=COLORS['accent'], edgecolors='none')

    all_vals = np.concatenate([gt, pred])
    lo, hi = all_vals.min() - 5, all_vals.max() + 5
    ax.plot([lo, hi], [lo, hi], 'k--', linewidth=0.8, alpha=0.5, label='Identity')

    r, p = stats.pearsonr(gt, pred)
    mae = np.abs(pred - gt).mean()
    rmse = np.sqrt(np.mean((pred - gt) ** 2))

    ax.text(0.05, 0.95,
            f'r = {r:.3f}\nMAE = {mae:.1f} bpm\nRMSE = {rmse:.1f} bpm\nn = {len(gt)}',
            transform=ax.transAxes, ha='left', va='top', fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=COLORS['light'], alpha=0.9))

    ax.set_xlabel('Ground Truth Heart Rate (bpm)', fontsize=9)
    ax.set_ylabel('Predicted Heart Rate (bpm)', fontsize=9)
    ax.set_title('Heart Rate: Predicted vs Ground Truth', fontsize=11, fontweight='bold')
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect('equal')
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=8, loc='lower right')

    fig.tight_layout()
    _save(fig, 'fig3_heart_rate_scatter')


def fig4_pipeline_timing():
    """Box plots showing latency distribution for each pipeline stage."""
    csv = RESULTS_DIR / 'pipeline_timing.csv'
    if not csv.exists():
        print('  SKIP fig4: pipeline_timing.csv not found')
        return
    df = pd.read_csv(csv)

    stage_order = [s for s in ['ingest', 'preprocess', 'quality', 'fiducials', 'features', 'total']
                   if s in df['stage'].unique()]

    fig, ax = plt.subplots(figsize=(6, 4))

    data = [df[df['stage'] == s]['latency_ms'].dropna().values for s in stage_order]
    bp = ax.boxplot(data, tick_labels=[s.capitalize() for s in stage_order],
                    patch_artist=True, widths=0.5,
                    medianprops=dict(color=COLORS['secondary'], linewidth=1.2),
                    flierprops=dict(marker='o', markersize=3, alpha=0.4))

    for patch in bp['boxes']:
        patch.set_facecolor(COLORS['accent'])
        patch.set_alpha(0.6)

    for i, s in enumerate(stage_order):
        vals = df[df['stage'] == s]['latency_ms'].dropna()
        if len(vals) > 0:
            ax.text(i + 1, vals.median(), f'{vals.median():.1f}',
                    ha='center', va='bottom', fontsize=7, fontweight='bold')

    ax.set_ylabel('Latency (ms)', fontsize=9)
    ax.set_title('Pipeline Stage Latency', fontsize=11, fontweight='bold')
    ax.tick_params(labelsize=8)

    fig.tight_layout()
    _save(fig, 'fig4_pipeline_timing')


def fig5_detection_rates():
    """Bar chart showing detection rate per fiducial type."""
    csv = RESULTS_DIR / 'fiducial_accuracy.csv'
    if not csv.exists():
        print('  SKIP fig5: fiducial_accuracy.csv not found')
        return
    df = pd.read_csv(csv)

    rates = []
    labels = []
    for fid in FIDUCIAL_ORDER:
        sub = df[df['fiducial'] == fid]
        if len(sub) > 0:
            rate = sub['detected'].sum() / len(sub) * 100
            rates.append(rate)
            labels.append(FIDUCIAL_LABELS.get(fid, fid))

    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(labels))
    bars = ax.bar(x, rates, color=COLORS['accent'], alpha=0.8, edgecolor='white', width=0.6)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=7, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
    ax.set_ylabel('Detection Rate (%)', fontsize=9)
    ax.set_title('Fiducial Point Detection Rates', fontsize=11, fontweight='bold')
    ax.set_ylim(0, max(rates) * 1.15 if rates else 100)
    ax.tick_params(labelsize=8)

    fig.tight_layout()
    _save(fig, 'fig5_detection_rates')


def fig6_disease_detection():
    """Grouped bar chart of per-condition sensitivity and specificity."""
    csv = RESULTS_DIR / 'disease_detection.csv'
    if not csv.exists():
        print('  SKIP fig6: disease_detection.csv not found')
        return
    df = pd.read_csv(csv)
    conditions = sorted(df['condition'].unique())

    stats_list = []
    for cond in conditions:
        sub = df[df['condition'] == cond]
        tp = sub['true_positive'].sum()
        fp = sub['false_positive'].sum()
        fn = sub['false_negative'].sum()
        tn = sub['true_negative'].sum()
        sens = tp / (tp + fn) if (tp + fn) > 0 else None
        spec = tn / (tn + fp) if (tn + fp) > 0 else None
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        stats_list.append({'condition': cond, 'sensitivity': sens, 'specificity': spec, 'f1': f1})

    stats_df = pd.DataFrame(stats_list)
    stats_df = stats_df.dropna(subset=['sensitivity', 'specificity'])

    if len(stats_df) == 0:
        print('  SKIP fig6: no conditions with valid sensitivity/specificity')
        return

    short_labels = [c.replace('_', ' ').replace('first degree ', '1st deg ') for c in stats_df['condition']]
    x = np.arange(len(short_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(8, len(short_labels) * 1.2), 5))
    bars_sens = ax.bar(x - width / 2, stats_df['sensitivity'], width,
                       color=COLORS['accent'], alpha=0.85, label='Sensitivity')
    bars_spec = ax.bar(x + width / 2, stats_df['specificity'], width,
                       color=COLORS['orange'], alpha=0.85, label='Specificity')

    for i, row in stats_df.iterrows():
        idx = stats_df.index.get_loc(i)
        ax.text(x[idx], max(row['sensitivity'], row['specificity']) + 0.03,
                f'F1={row["f1"]:.2f}', ha='center', va='bottom', fontsize=7, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=35, ha='right', fontsize=8)
    ax.set_ylabel('Score', fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.set_title('Disease Detection: Sensitivity & Specificity per Condition',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.tick_params(labelsize=8)

    fig.tight_layout()
    _save(fig, 'fig6_disease_detection')


def fig7_disease_f1():
    """Horizontal bar chart of F1 per condition, sorted descending."""
    csv = RESULTS_DIR / 'disease_detection.csv'
    if not csv.exists():
        print('  SKIP fig7: disease_detection.csv not found')
        return
    df = pd.read_csv(csv)
    conditions = sorted(df['condition'].unique())

    f1_data = []
    for cond in conditions:
        sub = df[df['condition'] == cond]
        tp = sub['true_positive'].sum()
        fp = sub['false_positive'].sum()
        fn = sub['false_negative'].sum()
        denom = 2 * tp + fp + fn
        f1 = 2 * tp / denom if denom > 0 else 0
        f1_data.append({'condition': cond, 'f1': f1})

    f1_df = pd.DataFrame(f1_data).sort_values('f1', ascending=True)

    if len(f1_df) == 0:
        print('  SKIP fig7: no F1 data')
        return

    short_labels = [c.replace('_', ' ').replace('first degree ', '1st deg ') for c in f1_df['condition']]

    fig, ax = plt.subplots(figsize=(7, max(4, len(short_labels) * 0.45)))
    bars = ax.barh(range(len(short_labels)), f1_df['f1'].values,
                   color=COLORS['accent'], alpha=0.85, edgecolor='white', height=0.6)

    for i, (bar, val) in enumerate(zip(bars, f1_df['f1'].values)):
        ax.text(val + 0.01, i, f'{val:.3f}', va='center', fontsize=7, fontweight='bold')

    ax.set_yticks(range(len(short_labels)))
    ax.set_yticklabels(short_labels, fontsize=8)
    ax.set_xlabel('F1 Score', fontsize=9)
    ax.set_xlim(0, min(1.15, f1_df['f1'].max() + 0.1))
    ax.set_title('Disease Detection: F1 Score per Condition', fontsize=11, fontweight='bold')
    ax.tick_params(labelsize=8)

    fig.tight_layout()
    _save(fig, 'fig7_disease_f1')


def fig8_cross_dataset_comparison():
    """Grouped bar chart of per-condition F1 across PTB-XL, Chapman, and CPSC 2018."""
    sources = {
        'PTB-XL': RESULTS_DIR / 'disease_summary.csv',
        'Chapman': RESULTS_DIR / 'chapman_summary.csv',
        'CPSC 2018': RESULTS_DIR / 'cpsc2018_summary.csv',
    }

    dataset_f1 = {}
    for label, csv in sources.items():
        if not csv.exists():
            print(f'  WARN fig8: {csv.name} not found, skipping {label}')
            continue
        df = pd.read_csv(csv)
        f1_map = {}
        for _, row in df.iterrows():
            cond = row['condition']
            gt_pos = row.get('n_gt_positive', 0)
            f1_val = row.get('F1', row.get('f1', None))
            if pd.notna(gt_pos) and gt_pos > 0 and pd.notna(f1_val):
                f1_map[cond] = float(f1_val)
        dataset_f1[label] = f1_map

    if not dataset_f1:
        print('  SKIP fig8: no dataset summaries found')
        return

    all_conditions = set()
    for f1_map in dataset_f1.values():
        all_conditions.update(f1_map.keys())
    conditions = sorted(all_conditions)

    if not conditions:
        print('  SKIP fig8: no conditions with GT positives in any dataset')
        return

    datasets = list(dataset_f1.keys())
    n_datasets = len(datasets)
    x = np.arange(len(conditions))
    width = 0.8 / n_datasets
    dataset_colors = [COLORS['accent'], COLORS['orange'], COLORS['green']]

    fig, ax = plt.subplots(figsize=(max(10, len(conditions) * 1.4), 5.5))

    for i, ds in enumerate(datasets):
        vals = [dataset_f1[ds].get(c, 0) for c in conditions]
        offset = (i - (n_datasets - 1) / 2) * width
        ax.bar(x + offset, vals, width, label=ds,
               color=dataset_colors[i % len(dataset_colors)], alpha=0.85,
               edgecolor='white', linewidth=0.3)

    short_labels = [c.replace('_', ' ').replace('first degree ', '1st deg ')
                    for c in conditions]
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=40, ha='right', fontsize=7)
    ax.set_ylabel('F1 Score', fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.set_title('Cross-Dataset Comparison: F1 per Condition', fontsize=11, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.tick_params(labelsize=8)

    fig.tight_layout()
    _save(fig, 'fig8_cross_dataset_comparison')


def fig9_multimodel_comparison():
    """Grouped bar chart of per-condition F1 for each model in multimodel results."""
    csv = RESULTS_DIR / 'multimodel_detection.csv'
    if not csv.exists():
        print('  SKIP fig9: multimodel_detection.csv not found')
        return
    df = pd.read_csv(csv)

    if len(df) == 0:
        print('  SKIP fig9: multimodel_detection.csv is empty')
        return

    models = sorted(df['model'].unique())
    conditions = sorted(df['condition'].unique())

    model_f1 = {}
    for model in models:
        f1_map = {}
        for cond in conditions:
            sub = df[(df['model'] == model) & (df['condition'] == cond)]
            if len(sub) == 0:
                continue
            tp = sub['TP'].sum()
            fp = sub['FP'].sum()
            fn = sub['FN'].sum()
            denom = 2 * tp + fp + fn
            f1 = 2 * tp / denom if denom > 0 else 0
            f1_map[cond] = f1
        model_f1[model] = f1_map

    all_conds = set()
    for f1_map in model_f1.values():
        all_conds.update(k for k, v in f1_map.items() if v is not None)
    conditions = sorted(all_conds)

    if not conditions:
        print('  SKIP fig9: no conditions with data')
        return

    n_models = len(models)
    x = np.arange(len(conditions))
    width = 0.8 / n_models
    model_colors = [COLORS['accent'], COLORS['orange'], COLORS['green'],
                    COLORS['secondary'], COLORS['primary']]

    fig, ax = plt.subplots(figsize=(max(10, len(conditions) * 1.4), 5.5))

    for i, model in enumerate(models):
        vals = [model_f1[model].get(c, 0) for c in conditions]
        offset = (i - (n_models - 1) / 2) * width
        ax.bar(x + offset, vals, width, label=model,
               color=model_colors[i % len(model_colors)], alpha=0.85,
               edgecolor='white', linewidth=0.3)

    short_labels = [c.replace('_', ' ').replace('first degree ', '1st deg ')
                    for c in conditions]
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=40, ha='right', fontsize=7)
    ax.set_ylabel('F1 Score', fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.set_title('Multi-Model Comparison: F1 per Condition', fontsize=11, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.tick_params(labelsize=8)

    fig.tight_layout()
    _save(fig, 'fig9_multimodel_comparison')


GENERATORS = {
    1: ('Fiducial Error Distribution', fig1_fiducial_error_distribution),
    2: ('Bland-Altman Plots', fig2_bland_altman),
    3: ('Heart Rate Scatter', fig3_heart_rate_scatter),
    4: ('Pipeline Timing Box Plot', fig4_pipeline_timing),
    5: ('Fiducial Detection Rates', fig5_detection_rates),
    6: ('Disease Detection Bar Chart', fig6_disease_detection),
    7: ('Disease Detection F1 Chart', fig7_disease_f1),
    8: ('Cross-Dataset Comparison', fig8_cross_dataset_comparison),
    9: ('Multi-Model Comparison', fig9_multimodel_comparison),
}


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate paper figures')
    parser.add_argument('--fig', nargs='*', type=int,
                        help='Specific figure numbers (default: all)')
    args = parser.parse_args()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figs = args.fig if args.fig else sorted(GENERATORS.keys())

    for n in figs:
        if n not in GENERATORS:
            print(f'Fig {n}: no generator available')
            continue
        name, fn = GENERATORS[n]
        print(f'Fig {n}: {name}')
        fn()

    print('\nDone.')


if __name__ == '__main__':
    main()
