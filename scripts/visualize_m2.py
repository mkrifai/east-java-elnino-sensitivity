"""
Milestone 2 Visualization: East Java El Niño Rainfall Response (Upgraded)
========================================================================
Generates publication-quality charts from m2_rainfall_statistics.json:
  1. Per-event seasonal rainfall anomalies (mm & % normal) and Z-scores (JJA & SON)
  2. Clear cohort separation: Pure El Niño (n=5) vs Compound El Niño + IOD+ (n=3)
  3. Cohort composite summary bars with standard error of the mean (±1 SEM)
  4. Okabe-Ito colorblind-safe palette, typographic minus signs, and non-overlapping labels
  5. Adheres to WMO/AMS journal visualization guidelines and Project Framework specifications
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUTPUT_DIR = 'outputs' if os.path.exists('outputs') else os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm2_rainfall_statistics.json')


with open(JSON_PATH, 'r') as f:
    data = json.load(f)

jja_events = data['jja_per_event']
son_events = data['son_per_event']
jja_clim = data['jja_climatology_mean_mm']  # 160.77 mm
son_clim = data['son_climatology_mean_mm']  # 331.75 mm

# Group into Pure vs Compound (+IOD)
pure_indices = [i for i, e in enumerate(jja_events) if e['iod_positive'] == 'No']
iod_indices = [i for i, e in enumerate(jja_events) if e['iod_positive'] == 'Yes']

# Data extraction helper
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

# Cohort Summary Statistics (Mean & Standard Error of the Mean)
pure_n = len(pure_indices)
iod_n = len(iod_indices)

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

# X-axis coordinate layout with distinct spacing gaps
# Pure: 0, 1, 2, 3, 4
# Compound: 5.3, 6.3, 7.3
# Summary: 8.8, 9.8
x_pure = np.arange(pure_n)
x_iod = np.array([5.3, 6.3, 7.3])
x_summary = np.array([8.8, 9.8])
bar_width = 0.36

# Okabe-Ito Colorblind-Safe Palette
c_pure_jja = '#56B4E9'  # Sky Blue (JJA Pure)
c_pure_son = '#0072B2'  # Deep Blue (SON Pure)
c_iod_jja  = '#E69F00'  # Amber (JJA Compound)
c_iod_son  = '#D55E00'  # Vermilion (SON Compound)
c_thresh   = '#2B2D42'  # Slate Charcoal for dryness threshold

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12.5, 9.0), sharex=True, dpi=300)

# =========================================================================
# PANEL 1: ABSOLUTE RAINFALL ANOMALY (mm) & RELATIVE DEFICIT (% NORMAL)
# =========================================================================

# Pure El Niño bars
b1_pure_jja = ax1.bar(x_pure - bar_width/2, pure['jja_anom'], bar_width,
                      color=c_pure_jja, edgecolor='#1E3A8A', linewidth=0.8, alpha=0.9)
b1_pure_son = ax1.bar(x_pure + bar_width/2, pure['son_anom'], bar_width,
                      color=c_pure_son, edgecolor='#0F172A', linewidth=0.8, alpha=0.9, hatch='//')

# Compound El Niño + IOD+ bars
b1_iod_jja = ax1.bar(x_iod - bar_width/2, iod['jja_anom'], bar_width,
                     color=c_iod_jja, edgecolor='#78350F', linewidth=0.8, alpha=0.9)
b1_iod_son = ax1.bar(x_iod + bar_width/2, iod['son_anom'], bar_width,
                     color=c_iod_son, edgecolor='#450A0A', linewidth=0.8, alpha=0.9, hatch='//')

# Summary Cohort Mean bars with Error Bars (SEM)
b1_sum_pure_jja = ax1.bar(x_summary[0] - bar_width/2, mean_pure_jja_anom, bar_width,
                          yerr=sem_pure_jja_anom, capsize=4, error_kw=dict(lw=1.2, capthick=1.2, ecolor='#1E3A8A'),
                          color=c_pure_jja, edgecolor='#1E3A8A', linewidth=1.4, alpha=0.95)
b1_sum_pure_son = ax1.bar(x_summary[0] + bar_width/2, mean_pure_son_anom, bar_width,
                          yerr=sem_pure_son_anom, capsize=4, error_kw=dict(lw=1.2, capthick=1.2, ecolor='#0F172A'),
                          color=c_pure_son, edgecolor='#0F172A', linewidth=1.4, alpha=0.95, hatch='//')

b1_sum_iod_jja = ax1.bar(x_summary[1] - bar_width/2, mean_iod_jja_anom, bar_width,
                         yerr=sem_iod_jja_anom, capsize=4, error_kw=dict(lw=1.2, capthick=1.2, ecolor='#78350F'),
                         color=c_iod_jja, edgecolor='#78350F', linewidth=1.4, alpha=0.95)
b1_sum_iod_son = ax1.bar(x_summary[1] + bar_width/2, mean_iod_son_anom, bar_width,
                         yerr=sem_iod_son_anom, capsize=4, error_kw=dict(lw=1.2, capthick=1.2, ecolor='#450A0A'),
                         color=c_iod_son, edgecolor='#450A0A', linewidth=1.4, alpha=0.95, hatch='//')

# Zero baseline
ax1.axhline(0, color='black', linewidth=1.0)
ax1.set_ylabel('Precipitation Anomaly (mm)', fontsize=11, fontweight='bold')
ax1.set_ylim(-345, 45)
ax1.grid(True, linestyle=':', alpha=0.6)

# Value annotations for Panel 1 with white protective badge
def annotate_bars_p1(bars, pcts):
    for bar, pct in zip(bars, pcts):
        yval = bar.get_height()
        ax1.annotate(f'\u2212{abs(yval):.0f}\n({pct:.0f}%)',
                     xy=(bar.get_x() + bar.get_width() / 2, yval),
                     xytext=(0, -16), textcoords="offset points",
                     ha='center', va='top', fontsize=7.5, fontweight='bold', color='#0F172A',
                     bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.88))

annotate_bars_p1(b1_pure_jja, pure['jja_pct'])
annotate_bars_p1(b1_pure_son, pure['son_pct'])
annotate_bars_p1(b1_iod_jja, iod['jja_pct'])
annotate_bars_p1(b1_iod_son, iod['son_pct'])

# Summary bar annotations
ax1.annotate(f'\u2212{abs(mean_pure_jja_anom):.0f}\n({(mean_pure_jja_anom/jja_clim)*100:.0f}%)',
             xy=(x_summary[0] - bar_width/2, mean_pure_jja_anom),
             xytext=(0, -18), textcoords="offset points",
             ha='center', va='top', fontsize=7.5, fontweight='bold', color='#1E3A8A',
             bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.88))
ax1.annotate(f'\u2212{abs(mean_pure_son_anom):.0f}\n({(mean_pure_son_anom/son_clim)*100:.0f}%)',
             xy=(x_summary[0] + bar_width/2, mean_pure_son_anom),
             xytext=(0, -22), textcoords="offset points",
             ha='center', va='top', fontsize=7.5, fontweight='bold', color='#0F172A',
             bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.88))

ax1.annotate(f'\u2212{abs(mean_iod_jja_anom):.0f}\n({(mean_iod_jja_anom/jja_clim)*100:.0f}%)',
             xy=(x_summary[1] - bar_width/2, mean_iod_jja_anom),
             xytext=(0, -18), textcoords="offset points",
             ha='center', va='top', fontsize=7.5, fontweight='bold', color='#78350F',
             bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.88))
ax1.annotate(f'\u2212{abs(mean_iod_son_anom):.0f}\n({(mean_iod_son_anom/son_clim)*100:.0f}%)',
             xy=(x_summary[1] + bar_width/2, mean_iod_son_anom),
             xytext=(0, -25), textcoords="offset points",
             ha='center', va='top', fontsize=7.5, fontweight='bold', color='#450A0A',
             bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.88))


# Section Dividers & Headers in Panel 1
ax1.axvline(4.65, color='#64748B', linestyle='--', linewidth=1.2, alpha=0.8)
ax1.axvline(8.05, color='#64748B', linestyle='-', linewidth=1.4, alpha=0.9)

# Group headers inside plot
ax1.text(2.0, 22, 'PURE EL NIÑO EPISODES (n = 5)', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0072B2')
ax1.text(6.3, 22, 'COMPOUND: EL NIÑO + IOD+ (n = 3)', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#D55E00')
ax1.text(9.2, 22, 'COHORT MEANS (±1 SEM)', ha='center', va='bottom', fontsize=9.0, fontweight='bold', color='#1E293B')

# Panel tag (a)
ax1.text(0.015, 0.94, '(a) Absolute Seasonal Precipitation Anomaly (mm) & Relative Deficit (% of Baseline)',
         transform=ax1.transAxes, fontsize=11, fontweight='bold', va='top')

# Climatology baseline reference label
ax1.text(0.985, 0.94, f'Baseline Mean: JJA = {jja_clim:.0f} mm | SON = {son_clim:.0f} mm',
         transform=ax1.transAxes, fontsize=8.5, fontstyle='italic', ha='right', va='top',
         bbox=dict(boxstyle='round,pad=0.25', fc='#F8FAFC', ec='#CBD5E1', lw=0.6))

# Legend in Panel 1
legend_elements = [
    Patch(facecolor=c_pure_jja, edgecolor='#1E3A8A', label='JJA Early Dry (Pure El Niño)'),
    Patch(facecolor=c_pure_son, edgecolor='#0F172A', hatch='//', label='SON Peak Dry (Pure El Niño)'),
    Patch(facecolor=c_iod_jja, edgecolor='#78350F', label='JJA Early Dry (El Niño + IOD+)'),
    Patch(facecolor=c_iod_son, edgecolor='#450A0A', hatch='//', label='SON Peak Dry (El Niño + IOD+)'),
]
ax1.legend(handles=legend_elements, loc='lower left', ncol=2, fontsize=8.5, frameon=True, framealpha=0.95)


# =========================================================================
# PANEL 2: STANDARDIZED METEOROLOGICAL ANOMALY (Z-SCORE)
# =========================================================================

# Pure El Niño bars
b2_pure_jja = ax2.bar(x_pure - bar_width/2, pure['jja_z'], bar_width,
                      color=c_pure_jja, edgecolor='#1E3A8A', linewidth=0.8, alpha=0.9)
b2_pure_son = ax2.bar(x_pure + bar_width/2, pure['son_z'], bar_width,
                      color=c_pure_son, edgecolor='#0F172A', linewidth=0.8, alpha=0.9, hatch='//')

# Compound El Niño + IOD+ bars
b2_iod_jja = ax2.bar(x_iod - bar_width/2, iod['jja_z'], bar_width,
                     color=c_iod_jja, edgecolor='#78350F', linewidth=0.8, alpha=0.9)
b2_iod_son = ax2.bar(x_iod + bar_width/2, iod['son_z'], bar_width,
                     color=c_iod_son, edgecolor='#450A0A', linewidth=0.8, alpha=0.9, hatch='//')

# Summary Cohort Mean bars
b2_sum_pure_jja = ax2.bar(x_summary[0] - bar_width/2, mean_pure_jja_z, bar_width,
                          yerr=sem_pure_jja_z, capsize=4, error_kw=dict(lw=1.2, capthick=1.2, ecolor='#1E3A8A'),
                          color=c_pure_jja, edgecolor='#1E3A8A', linewidth=1.4, alpha=0.95)
b2_sum_pure_son = ax2.bar(x_summary[0] + bar_width/2, mean_pure_son_z, bar_width,
                          yerr=sem_pure_son_z, capsize=4, error_kw=dict(lw=1.2, capthick=1.2, ecolor='#0F172A'),
                          color=c_pure_son, edgecolor='#0F172A', linewidth=1.4, alpha=0.95, hatch='//')

b2_sum_iod_jja = ax2.bar(x_summary[1] - bar_width/2, mean_iod_jja_z, bar_width,
                         yerr=sem_iod_jja_z, capsize=4, error_kw=dict(lw=1.2, capthick=1.2, ecolor='#78350F'),
                         color=c_iod_jja, edgecolor='#78350F', linewidth=1.4, alpha=0.95)
b2_sum_iod_son = ax2.bar(x_summary[1] + bar_width/2, mean_iod_son_z, bar_width,
                         yerr=sem_iod_son_z, capsize=4, error_kw=dict(lw=1.2, capthick=1.2, ecolor='#450A0A'),
                         color=c_iod_son, edgecolor='#450A0A', linewidth=1.4, alpha=0.95, hatch='//')

# Zero line and Meteorological Dryness Threshold (Z = -1.0)
ax2.axhline(0, color='black', linewidth=1.0)
thresh_line = ax2.axhline(-1.0, color=c_thresh, linestyle='--', linewidth=1.3,
                          label='Meteorological Dryness Threshold (Z = \u22121.0)')

ax2.set_ylabel('Standardized Anomaly (Z-score)', fontsize=11, fontweight='bold')
ax2.set_ylim(-1.85, 0.30)
ax2.grid(True, linestyle=':', alpha=0.6)

# Value annotations for Panel 2 with white background halo to prevent collision with Z = -1.0 threshold line
def annotate_bars_p2(bars, values):
    for bar, val in zip(bars, values):
        ax2.annotate(f'\u2212{abs(val):.2f}',
                     xy=(bar.get_x() + bar.get_width() / 2, val),
                     xytext=(0, -14), textcoords="offset points",
                     ha='center', va='top', fontsize=8.0, fontweight='bold', color='#0F172A',
                     bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.92))

annotate_bars_p2(b2_pure_jja, pure['jja_z'])
annotate_bars_p2(b2_pure_son, pure['son_z'])
annotate_bars_p2(b2_iod_jja, iod['jja_z'])
annotate_bars_p2(b2_iod_son, iod['son_z'])

# Summary bar annotations in Panel 2 with protective background badge
ax2.annotate(f'\u2212{abs(mean_pure_jja_z):.2f}',
             xy=(x_summary[0] - bar_width/2, mean_pure_jja_z),
             xytext=(0, -14), textcoords="offset points",
             ha='center', va='top', fontsize=8.0, fontweight='bold', color='#1E3A8A',
             bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.92))
ax2.annotate(f'\u2212{abs(mean_pure_son_z):.2f}',
             xy=(x_summary[0] + bar_width/2, mean_pure_son_z),
             xytext=(0, -18), textcoords="offset points",
             ha='center', va='top', fontsize=8.0, fontweight='bold', color='#0F172A',
             bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.92))

ax2.annotate(f'\u2212{abs(mean_iod_jja_z):.2f}',
             xy=(x_summary[1] - bar_width/2, mean_iod_jja_z),
             xytext=(0, -14), textcoords="offset points",
             ha='center', va='top', fontsize=8.0, fontweight='bold', color='#78350F',
             bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.92))
ax2.annotate(f'\u2212{abs(mean_iod_son_z):.2f}',
             xy=(x_summary[1] + bar_width/2, mean_iod_son_z),
             xytext=(0, -22), textcoords="offset points",
             ha='center', va='top', fontsize=8.0, fontweight='bold', color='#450A0A',
             bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.92))


# Section Dividers in Panel 2
ax2.axvline(4.65, color='#64748B', linestyle='--', linewidth=1.2, alpha=0.8)
ax2.axvline(8.05, color='#64748B', linestyle='-', linewidth=1.4, alpha=0.9)

# Panel tag (b)
ax2.text(0.015, 0.94, '(b) Standardized Meteorological Anomaly (Z-score relative to Neutral Baseline Climatology)',
         transform=ax2.transAxes, fontsize=11, fontweight='bold', va='top')

ax2.legend(loc='lower left', fontsize=8.5, frameon=True, framealpha=0.95)

# =========================================================================
# X-AXIS TICK LABELS & ANNOTATIONS
# =========================================================================
all_x = np.concatenate([x_pure, x_iod, x_summary])
xticklabels = []

for yr, intensity in zip(pure['years'], pure['intensities']):
    xticklabels.append(f"{yr}\n({intensity})")

for yr, intensity in zip(iod['years'], iod['intensities']):
    xticklabels.append(f"{yr}\n({intensity})\n[+IOD]")

xticklabels.append("Pure Mean\n(n = 5)")
xticklabels.append("Compound Mean\n(n = 3)")

ax2.set_xticks(all_x)
ax2.set_xticklabels(xticklabels, fontsize=9.0, fontweight='bold')
ax2.set_xlabel('El Niño Episodes (2001–2025) Classified by Pacific & Indian Ocean SSTA Forcing', fontsize=11, fontweight='bold', labelpad=10)

# Main Title & Subtitle
fig.suptitle('East Java Provincial Precipitation Response Across 25 Years of El Niño Episodes (2001–2025)',
             fontsize=13.5, fontweight='bold', y=0.98)

# Explanatory caption box at the bottom
footnote = (
    "Dataset: UCSB CHIRPS v2.0 (0.05° resolution resampled to 1 km). "
    "Baseline Climatology: 6 neutral ENSO years (2001, 2003, 2012, 2013, 2019, 2025) within the 2001–2025 multi-sensor domain. "
    "ENSO: NOAA CPC ONI ≥ +0.5°C (≥5 consecutive seasons). IOD+: BoM/NOAA DMI ≥ +0.4°C (JJA/SON). "
    "Error bars indicate ±1 standard error of the mean (SEM). Threshold Z = −1.0 corresponds to moderate-to-severe meteorological dryness."
)
fig.text(0.5, 0.015, footnote, ha='center', fontsize=7.2, color='#475569',
         bbox=dict(boxstyle='square,pad=0.4', fc='#F1F5F9', ec='#CBD5E1', lw=0.6))

plt.tight_layout(rect=[0, 0.04, 1, 0.96])

# Save high-resolution publication PNG and vector PDF
plot_path_png = os.path.join(OUTPUT_DIR, 'm2_elnino_rainfall_anomalies.png')
plot_path_pdf = os.path.join(OUTPUT_DIR, 'm2_elnino_rainfall_anomalies.pdf')

plt.savefig(plot_path_png, dpi=300, bbox_inches='tight')
plt.savefig(plot_path_pdf, bbox_inches='tight')
print(f"[OK] High-resolution publication chart saved to: {plot_path_png}")
print(f"[OK] Vector publication PDF saved to: {plot_path_pdf}")
