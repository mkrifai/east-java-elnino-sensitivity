"""
Milestone 2 Visualization: East Java El Niño Rainfall Response (Journal Standard)
================================================================================
Generates publication-quality figures from m2_rainfall_statistics.json adhering to WMO/AMS guidelines:
  1. Complete graphic integrity: zero occlusion of zero baseline, bar bases, or error bar whiskers
  2. Subplot titles placed strictly outside the axes area
  3. Uniform label placement below bars with white stroke contour (no opaque boxes)
  4. Explicit baseline climatological sampling uncertainty (+-1 SE) visual reference
  5. Cohort separation: Pure El Niño (n=5) vs Compound El Niño + IOD+ (n=3) and Cohort Composites
  6. Multi-year episode (2014-2015) explicit demarcation
  7. Typographical Unicode minus signs throughout all numerical labels
  8. Detailed statistical tests and methodological discussion maintained in report manuscript
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.patheffects as pe
from matplotlib.patches import Patch

OUTPUT_DIR = 'outputs' if os.path.exists('outputs') else os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm2_rainfall_statistics.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

jja_events = data['jja_per_event']
son_events = data['son_per_event']
jja_clim = data['jja_climatology_mean_mm']  # 160.77 mm
son_clim = data['son_climatology_mean_mm']  # 331.75 mm

# Climatological baseline standard error of the mean (n = 6 neutral years)
# Inferred sigma: JJA ~ 120.2 mm, SON ~ 180.9 mm
jja_baseline_se = 120.18 / np.sqrt(6)  # ~49.1 mm
son_baseline_se = 180.89 / np.sqrt(6)  # ~73.8 mm
z_baseline_se = 1.0 / np.sqrt(6)       # ~0.408

# Group into Pure vs Compound (+IOD)
pure_indices = [i for i, e in enumerate(jja_events) if e['iod_positive'] == 'No']
iod_indices = [i for i, e in enumerate(jja_events) if e['iod_positive'] == 'Yes']

def extract_cohort(indices):
    return {
        'years': [jja_events[i]['year'] for i in indices],
        'intensities': [jja_events[i]['intensity'] for i in indices],
        'jja_anom': [jja_events[i]['anomaly_mm'] for i in indices],
        'jja_z': [jja_events[i]['z_score'] for i in indices],
        'jja_pct': [(jja_events[i]['anomaly_mm'] / jja_clim) * 100 for i in indices],
        'son_anom': [son_events[i]['anomaly_mm'] for i in indices],
        'son_z': [son_events[i]['z_score'] for i in indices],
        'son_pct': [(son_events[i]['anomaly_mm'] / son_clim) * 100 for i in indices],
    }

pure = extract_cohort(pure_indices)
iod = extract_cohort(iod_indices)

pure_n = len(pure_indices)
iod_n = len(iod_indices)

# Cohort Summary Statistics (Mean & Standard Error of the Mean)
mean_pure_jja_anom = np.mean(pure['jja_anom'])
sem_pure_jja_anom = np.std(pure['jja_anom'], ddof=1) / np.sqrt(pure_n)
mean_pure_son_anom = np.mean(pure['son_anom'])
sem_pure_son_anom = np.std(pure['son_anom'], ddof=1) / np.sqrt(pure_n)

mean_iod_jja_anom = np.mean(iod['jja_anom'])
sem_iod_jja_anom = np.std(iod['jja_anom'], ddof=1) / np.sqrt(iod_n)
mean_iod_son_anom = np.mean(iod['son_anom'])
sem_iod_son_anom = np.std(iod['son_anom'], ddof=1) / np.sqrt(iod_n)

mean_pure_jja_z = np.mean(pure['jja_z'])
sem_pure_jja_z = np.std(pure['jja_z'], ddof=1) / np.sqrt(pure_n)
mean_pure_son_z = np.mean(pure['son_z'])
sem_pure_son_z = np.std(pure['son_z'], ddof=1) / np.sqrt(pure_n)

mean_iod_jja_z = np.mean(iod['jja_z'])
sem_iod_jja_z = np.std(iod['jja_z'], ddof=1) / np.sqrt(iod_n)
mean_iod_son_z = np.mean(iod['son_z'])
sem_iod_son_z = np.std(iod['son_z'], ddof=1) / np.sqrt(iod_n)

# X-axis coordinates
x_pure = np.arange(pure_n)
x_iod = np.array([5.2, 6.2, 7.2])
x_summary = np.array([8.7, 9.7])
bar_width = 0.36

# Okabe-Ito Colorblind-Safe Palette
c_pure_jja = '#56B4E9'  # Sky Blue (JJA Pure)
c_pure_son = '#0072B2'  # Deep Blue (SON Pure)
c_iod_jja  = '#E69F00'  # Amber (JJA Compound)
c_iod_son  = '#D55E00'  # Vermilion (SON Compound)
c_whisker  = '#0F172A'  # Deep Slate for error bars
c_thresh   = '#0F172A'  # Dryness threshold line

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.0, 8.8), sharex=True, dpi=300)
fig.subplots_adjust(top=0.81, bottom=0.11, left=0.08, right=0.97, hspace=0.24)

err_kw = dict(lw=1.3, capthick=1.3, ecolor=c_whisker)
text_stroke = [pe.withStroke(linewidth=2.8, foreground='white')]

# =========================================================================
# PANEL 1: SEASONAL PRECIPITATION ANOMALY (mm)
# =========================================================================

# Baseline Climatology Sampling Uncertainty (+-1 SE) around zero line
ax1.axhspan(-jja_baseline_se, jja_baseline_se, color='#94A3B8', alpha=0.20, zorder=0,
            label=f'Baseline Mean Uncertainty: JJA (\u00b1{jja_baseline_se:.0f} mm)')
ax1.axhspan(-son_baseline_se, son_baseline_se, color='#64748B', alpha=0.12, zorder=0,
            label=f'Baseline Mean Uncertainty: SON (\u00b1{son_baseline_se:.0f} mm)')

# Pure El Niño bars
b1_pure_jja = ax1.bar(x_pure - bar_width/2, pure['jja_anom'], bar_width,
                      color=c_pure_jja, edgecolor='#1E3A8A', linewidth=0.9, alpha=0.92, zorder=2)
b1_pure_son = ax1.bar(x_pure + bar_width/2, pure['son_anom'], bar_width,
                      color=c_pure_son, edgecolor='#0F172A', linewidth=0.9, alpha=0.92, hatch='/', zorder=2)

# Compound El Niño + IOD+ bars
b1_iod_jja = ax1.bar(x_iod - bar_width/2, iod['jja_anom'], bar_width,
                     color=c_iod_jja, edgecolor='#78350F', linewidth=0.9, alpha=0.92, zorder=2)
b1_iod_son = ax1.bar(x_iod + bar_width/2, iod['son_anom'], bar_width,
                     color=c_iod_son, edgecolor='#450A0A', linewidth=0.9, alpha=0.92, hatch='/', zorder=2)

# Summary Cohort Mean bars with Error Bars (SEM)
b1_sum_pure_jja = ax1.bar(x_summary[0] - bar_width/2, mean_pure_jja_anom, bar_width,
                          yerr=sem_pure_jja_anom, capsize=4, error_kw=err_kw,
                          color=c_pure_jja, edgecolor='#1E3A8A', linewidth=1.3, alpha=0.95, zorder=2)
b1_sum_pure_son = ax1.bar(x_summary[0] + bar_width/2, mean_pure_son_anom, bar_width,
                          yerr=sem_pure_son_anom, capsize=4, error_kw=err_kw,
                          color=c_pure_son, edgecolor='#0F172A', linewidth=1.3, alpha=0.95, hatch='/', zorder=2)

b1_sum_iod_jja = ax1.bar(x_summary[1] - bar_width/2, mean_iod_jja_anom, bar_width,
                         yerr=sem_iod_jja_anom, capsize=4, error_kw=err_kw,
                         color=c_iod_jja, edgecolor='#78350F', linewidth=1.3, alpha=0.95, zorder=2)
b1_sum_iod_son = ax1.bar(x_summary[1] + bar_width/2, mean_iod_son_anom, bar_width,
                         yerr=sem_iod_son_anom, capsize=4, error_kw=err_kw,
                         color=c_iod_son, edgecolor='#450A0A', linewidth=1.3, alpha=0.95, hatch='/', zorder=2)

# Prominent zero baseline (zorder=3 to ensure sharp un-obscured boundary)
ax1.axhline(0, color='#0F172A', linewidth=1.2, zorder=3)
ax1.set_ylabel('Precipitation Anomaly (mm)', fontsize=10.5, fontweight='bold')
ax1.set_ylim(-340, 85)
ax1.grid(True, linestyle=':', alpha=0.5, zorder=0)

# Value annotations for Panel 1: strictly below bar bottoms with white stroke contour
def annotate_bars_p1(bars, pcts):
    for bar, pct in zip(bars, pcts):
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, yval - 6,
                 f'\u2212{abs(yval):.0f}\n(\u2212{abs(pct):.0f}%)',
                 ha='center', va='top', fontsize=7.5, fontweight='bold', color='#0F172A',
                 path_effects=text_stroke, linespacing=1.05, zorder=4)

annotate_bars_p1(b1_pure_jja, pure['jja_pct'])
annotate_bars_p1(b1_pure_son, pure['son_pct'])
annotate_bars_p1(b1_iod_jja, iod['jja_pct'])
annotate_bars_p1(b1_iod_son, iod['son_pct'])

# Summary bar annotations in Panel 1: positioned below whisker caps to prevent line collisions
def annotate_summary_p1(xpos, mean_val, sem_val, clim_val):
    whisker_bottom = mean_val - sem_val
    pct = (mean_val / clim_val) * 100
    ax1.text(xpos, whisker_bottom - 7,
             f'\u2212{abs(mean_val):.0f}\n(\u2212{abs(pct):.0f}%)',
             ha='center', va='top', fontsize=7.5, fontweight='bold', color='#0F172A',
             path_effects=text_stroke, linespacing=1.05, zorder=4)

annotate_summary_p1(x_summary[0] - bar_width/2, mean_pure_jja_anom, sem_pure_jja_anom, jja_clim)
annotate_summary_p1(x_summary[0] + bar_width/2, mean_pure_son_anom, sem_pure_son_anom, son_clim)
annotate_summary_p1(x_summary[1] - bar_width/2, mean_iod_jja_anom, sem_iod_jja_anom, jja_clim)
annotate_summary_p1(x_summary[1] + bar_width/2, mean_iod_son_anom, sem_iod_son_anom, son_clim)

# Section Dividers across panels
ax1.axvline(4.60, color='#94A3B8', linestyle='--', linewidth=1.2, alpha=0.8, zorder=1)
ax1.axvline(7.95, color='#94A3B8', linestyle='-', linewidth=1.4, alpha=0.9, zorder=1)

# Group headers outside top frame using blended transform (with generous clearance above panel title)
blended_1 = mtransforms.blended_transform_factory(ax1.transData, ax1.transAxes)
ax1.text(2.0, 1.15, 'Pure El Niño (n = 5)', ha='center', va='bottom',
         transform=blended_1, fontsize=9.5, fontweight='bold', color='#0072B2')
ax1.text(6.2, 1.15, 'Compound: El Niño + IOD+ (n = 3)', ha='center', va='bottom',
         transform=blended_1, fontsize=9.5, fontweight='bold', color='#D55E00')
ax1.text(9.2, 1.15, 'Cohort Composites (±1 SEM)', ha='center', va='bottom',
         transform=blended_1, fontsize=9.5, fontweight='bold', color='#1E293B')

# Group bracket lines
ax1.plot([-0.35, 4.35], [1.11, 1.11], transform=blended_1, color='#0072B2', lw=1.3, clip_on=False)
ax1.plot([4.85, 7.55], [1.11, 1.11], transform=blended_1, color='#D55E00', lw=1.3, clip_on=False)
ax1.plot([8.35, 10.05], [1.11, 1.11], transform=blended_1, color='#1E293B', lw=1.3, clip_on=False)

# Subplot Title placed cleanly OUTSIDE the plot frame below the brackets
ax1.set_title('(a) Seasonal Precipitation Anomaly (mm) and Relative Departure (% of Climatological Baseline)',
              loc='left', fontsize=10.5, fontweight='bold', pad=8)

# Legend in Panel 1
legend_elements_1 = [
    Patch(facecolor=c_pure_jja, edgecolor='#1E3A8A', label='JJA Early Dry (Pure El Niño)'),
    Patch(facecolor=c_pure_son, edgecolor='#0F172A', hatch='/', label='SON Peak Dry (Pure El Niño)'),
    Patch(facecolor=c_iod_jja, edgecolor='#78350F', label='JJA Early Dry (El Niño + IOD+)'),
    Patch(facecolor=c_iod_son, edgecolor='#450A0A', hatch='/', label='SON Peak Dry (El Niño + IOD+)'),
    Patch(facecolor='#94A3B8', edgecolor='#64748B', linewidth=0.8, alpha=0.30,
          label='Baseline Uncertainty (\u00b11 SE: JJA \u00b149 mm, SON \u00b174 mm)'),
]
ax1.legend(handles=legend_elements_1, loc='upper right', ncol=2, fontsize=8.0, frameon=True, framealpha=0.95)


# =========================================================================
# PANEL 2: STANDARDIZED ANOMALY (Z-SCORE)
# =========================================================================

# Baseline Sampling Uncertainty (+-1 SE_Z = +-0.41) - Fully symmetric and visible
ax2.axhspan(-z_baseline_se, z_baseline_se, color='#94A3B8', alpha=0.20, zorder=0,
            label='Baseline Mean Uncertainty (\u00b11 SE = \u00b10.41)')

# Pure El Niño bars
b2_pure_jja = ax2.bar(x_pure - bar_width/2, pure['jja_z'], bar_width,
                      color=c_pure_jja, edgecolor='#1E3A8A', linewidth=0.9, alpha=0.92, zorder=2)
b2_pure_son = ax2.bar(x_pure + bar_width/2, pure['son_z'], bar_width,
                      color=c_pure_son, edgecolor='#0F172A', linewidth=0.9, alpha=0.92, hatch='/', zorder=2)

# Compound El Niño + IOD+ bars
b2_iod_jja = ax2.bar(x_iod - bar_width/2, iod['jja_z'], bar_width,
                     color=c_iod_jja, edgecolor='#78350F', linewidth=0.9, alpha=0.92, zorder=2)
b2_iod_son = ax2.bar(x_iod + bar_width/2, iod['son_z'], bar_width,
                     color=c_iod_son, edgecolor='#450A0A', linewidth=0.9, alpha=0.92, hatch='/', zorder=2)

# Summary Cohort Mean bars
b2_sum_pure_jja = ax2.bar(x_summary[0] - bar_width/2, mean_pure_jja_z, bar_width,
                          yerr=sem_pure_jja_z, capsize=4, error_kw=err_kw,
                          color=c_pure_jja, edgecolor='#1E3A8A', linewidth=1.3, alpha=0.95, zorder=2)
b2_sum_pure_son = ax2.bar(x_summary[0] + bar_width/2, mean_pure_son_z, bar_width,
                          yerr=sem_pure_son_z, capsize=4, error_kw=err_kw,
                          color=c_pure_son, edgecolor='#0F172A', linewidth=1.3, alpha=0.95, hatch='/', zorder=2)

b2_sum_iod_jja = ax2.bar(x_summary[1] - bar_width/2, mean_iod_jja_z, bar_width,
                         yerr=sem_iod_jja_z, capsize=4, error_kw=err_kw,
                         color=c_iod_jja, edgecolor='#78350F', linewidth=1.3, alpha=0.95, zorder=2)
b2_sum_iod_son = ax2.bar(x_summary[1] + bar_width/2, mean_iod_son_z, bar_width,
                         yerr=sem_iod_son_z, capsize=4, error_kw=err_kw,
                         color=c_iod_son, edgecolor='#450A0A', linewidth=1.3, alpha=0.95, hatch='/', zorder=2)

# Zero baseline and Meteorological Dryness Threshold (Z = -1.0)
ax2.axhline(0, color='#0F172A', linewidth=1.2, zorder=3)
thresh_line = ax2.axhline(-1.0, color=c_thresh, linestyle='--', linewidth=1.3, zorder=2,
                          label='Meteorological Dryness Threshold (Z = \u22121.0)')

ax2.set_ylabel('Standardized Anomaly (Z-score)', fontsize=10.5, fontweight='bold')
ax2.set_ylim(-1.62, 0.48)
ax2.grid(True, linestyle=':', alpha=0.5, zorder=0)

# Value annotations for Panel 2: strictly below bar bottoms with white stroke contour
def annotate_bars_p2(bars, values):
    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width() / 2, val - 0.04,
                 f'\u2212{abs(val):.2f}',
                 ha='center', va='top', fontsize=7.5, fontweight='bold', color='#0F172A',
                 path_effects=text_stroke, zorder=4)

annotate_bars_p2(b2_pure_jja, pure['jja_z'])
annotate_bars_p2(b2_pure_son, pure['son_z'])
annotate_bars_p2(b2_iod_jja, iod['jja_z'])
annotate_bars_p2(b2_iod_son, iod['son_z'])

# Summary bar annotations in Panel 2: positioned below whisker caps
def annotate_summary_p2(xpos, mean_val, sem_val):
    whisker_bottom = mean_val - sem_val
    ax2.text(xpos, whisker_bottom - 0.04,
             f'\u2212{abs(mean_val):.2f}',
             ha='center', va='top', fontsize=7.5, fontweight='bold', color='#0F172A',
             path_effects=text_stroke, zorder=4)

annotate_summary_p2(x_summary[0] - bar_width/2, mean_pure_jja_z, sem_pure_jja_z)
annotate_summary_p2(x_summary[0] + bar_width/2, mean_pure_son_z, sem_pure_son_z)
annotate_summary_p2(x_summary[1] - bar_width/2, mean_iod_jja_z, sem_iod_jja_z)
annotate_summary_p2(x_summary[1] + bar_width/2, mean_iod_son_z, sem_iod_son_z)

# Dividers in Panel 2
ax2.axvline(4.60, color='#94A3B8', linestyle='--', linewidth=1.2, alpha=0.8, zorder=1)
ax2.axvline(7.95, color='#94A3B8', linestyle='-', linewidth=1.4, alpha=0.9, zorder=1)

# Subplot Title placed cleanly OUTSIDE the plot frame
ax2.set_title('(b) Standardized Meteorological Anomaly (Z-score relative to ENSO-Neutral Baseline)',
              loc='left', fontsize=10.5, fontweight='bold', pad=8)

legend_elements_2 = [
    thresh_line,
    Patch(facecolor='#94A3B8', edgecolor='#64748B', linewidth=0.8, alpha=0.30,
          label='Baseline Mean Uncertainty (\u00b11 SE = \u00b10.41)'),
]
ax2.legend(handles=legend_elements_2, loc='lower left', fontsize=8.0, frameon=True, framealpha=0.95)

# =========================================================================
# X-AXIS TICK LABELS & DUAL-SECTION LABELS
# =========================================================================
all_x = np.concatenate([x_pure, x_iod, x_summary])
xticklabels = []

for yr, intensity in zip(pure['years'], pure['intensities']):
    tag = f"{yr}*" if yr in [2014, 2015] else f"{yr}"
    xticklabels.append(f"{tag}\n({intensity})")

for yr, intensity in zip(iod['years'], iod['intensities']):
    xticklabels.append(f"{yr}\n({intensity})\n[+IOD]")

xticklabels.append("Pure Mean\n(n = 5)")
xticklabels.append("Compound Mean\n(n = 3)")

ax2.set_xticks(all_x)
ax2.set_xticklabels(xticklabels, fontsize=8.8, fontweight='bold')

# Dual-section x-axis labels with zero collision:
blended_2 = mtransforms.blended_transform_factory(ax2.transData, ax2.transAxes)
ax2.text(3.6, -0.17,
         'Historical El Niño Episodes (2001–2025)\n[*2014 & 2015 indicate consecutive dry seasons of the extended 2014–2016 multi-year ENSO episode]',
         ha='center', va='top', transform=blended_2, fontsize=9.0, fontweight='bold', color='#1E293B', linespacing=1.25)
ax2.text(9.2, -0.17,
         'Cohort Composites\n[Mean \u00b1 1 SEM]',
         ha='center', va='top', transform=blended_2, fontsize=9.0, fontweight='bold', color='#1E293B', linespacing=1.25)

# Main Title & Subtitle with proper breathing room
fig.suptitle('East Java Precipitation Anomalies Across Historical El Niño Episodes (2001–2025)',
             fontsize=13.0, fontweight='bold', y=0.975)
fig.text(0.50, 0.938, f'ENSO-Neutral Baseline Climatology (n = 6): JJA = {jja_clim:.0f} mm, SON = {son_clim:.0f} mm  |  Data: UCSB CHIRPS v2.0 (0.05\u00b0 resolution)',
         ha='center', fontsize=9.0, color='#475569')

# Save high-resolution publication PNG and vector PDF using safe write
def safe_savefig(target_path, **kwargs):
    base, ext = os.path.splitext(target_path)
    tmp_path = f"{base}_tmp{ext}"
    plt.savefig(tmp_path, **kwargs)
    if os.path.exists(target_path):
        try:
            os.remove(target_path)
        except Exception:
            pass
    try:
        os.replace(tmp_path, target_path)
    except Exception:
        import shutil
        shutil.copyfile(tmp_path, target_path)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


plot_path_png = os.path.join(OUTPUT_DIR, 'm2_elnino_rainfall_anomalies.png')
plot_path_pdf = os.path.join(OUTPUT_DIR, 'm2_elnino_rainfall_anomalies.pdf')

safe_savefig(plot_path_png, dpi=300, bbox_inches='tight')
safe_savefig(plot_path_pdf, bbox_inches='tight')
print(f"[OK] High-resolution publication chart saved to: {plot_path_png}")
print(f"[OK] Vector publication PDF saved to: {plot_path_pdf}")
