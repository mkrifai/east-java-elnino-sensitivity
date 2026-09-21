"""
Milestone 2 Visualization: East Java El Niño Rainfall Response
==============================================================
Generates publication-quality charts from m2_rainfall_statistics.json:
  1. Per-event rainfall anomalies (mm & z-score) for JJA & SON
  2. Pure El Niño vs Compound El Niño+IOD+ contrast
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm2_rainfall_statistics.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

jja_events = data['jja_per_event']
son_events = data['son_per_event']

years = [e['year'] for e in jja_events]
intensities = [e['intensity'] for e in jja_events]
iod_flags = [e['iod_positive'] == 'Yes' for e in jja_events]

jja_anom = [e['anomaly_mm'] for e in jja_events]
jja_z = [e['z_score'] for e in jja_events]
son_anom = [e['anomaly_mm'] for e in son_events]
son_z = [e['z_score'] for e in son_events]

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5), sharex=True, dpi=300)

x = np.arange(len(years))
width = 0.36

# Colors: Pure El Nino vs Compound (El Nino + IOD+)
c_pure_jja = '#e67e22'
c_iod_jja  = '#c0392b'
c_pure_son = '#d35400'
c_iod_son  = '#962d22'

colors_jja = [c_iod_jja if iod else c_pure_jja for iod in iod_flags]
colors_son = [c_iod_son if iod else c_pure_son for iod in iod_flags]

# Panel 1: Rainfall Anomaly (mm)
bars1 = ax1.bar(x - width/2, jja_anom, width, label='JJA (Jun-Aug)', color=colors_jja, edgecolor='black', linewidth=0.7, alpha=0.85)
bars2 = ax1.bar(x + width/2, son_anom, width, label='SON (Sep-Nov)', color=colors_son, edgecolor='black', linewidth=0.7, alpha=0.85, hatch='//')

ax1.axhline(0, color='black', linewidth=1)
ax1.set_ylabel('Rainfall Anomaly (mm)', fontsize=12, fontweight='bold')
ax1.set_title('East Java Provincial Mean Rainfall Anomaly during El Niño Episodes (2001–2025)\nUCSB CHIRPS v2.0 vs Neutral-Year Baseline (2001, 2003, 2012, 2013, 2019, 2025)', fontsize=13, fontweight='bold', pad=12)
ax1.grid(True, linestyle='--', alpha=0.5)

# Value annotations on bars
for bar in bars1:
    yval = bar.get_height()
    ax1.annotate(f'{yval:.0f}',
                 xy=(bar.get_x() + bar.get_width() / 2, yval),
                 xytext=(0, -11), textcoords="offset points",
                 ha='center', va='top', fontsize=9, fontweight='bold', color='#7f1d1d')

for bar in bars2:
    yval = bar.get_height()
    ax1.annotate(f'{yval:.0f}',
                 xy=(bar.get_x() + bar.get_width() / 2, yval),
                 xytext=(0, -11), textcoords="offset points",
                 ha='center', va='top', fontsize=9, fontweight='bold', color='#450a0a')

# Legend for panel 1
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=c_pure_jja, edgecolor='black', label='JJA (Pure El Niño)'),
    Patch(facecolor=c_iod_jja, edgecolor='black', label='JJA (El Niño + IOD+)'),
    Patch(facecolor=c_pure_son, edgecolor='black', hatch='//', label='SON (Pure El Niño)'),
    Patch(facecolor=c_iod_son, edgecolor='black', hatch='//', label='SON (El Niño + IOD+)'),
]
ax1.legend(handles=legend_elements, loc='lower left', frameon=True, framealpha=0.9)

# Panel 2: Standardized Anomaly (Z-score)
bars3 = ax2.bar(x - width/2, jja_z, width, color=colors_jja, edgecolor='black', linewidth=0.7, alpha=0.85)
bars4 = ax2.bar(x + width/2, son_z, width, color=colors_son, edgecolor='black', linewidth=0.7, alpha=0.85, hatch='//')

ax2.axhline(0, color='black', linewidth=1)
ax2.axhline(-1.0, color='red', linestyle=':', linewidth=1.2, label='Drought Threshold (Z = -1.0)')
ax2.set_ylabel('Standardized Anomaly (Z-score)', fontsize=12, fontweight='bold')
ax2.set_xlabel('El Niño Event Year & Intensity', fontsize=12, fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.5)

# Value annotations for Z-score
for bar in bars3:
    yval = bar.get_height()
    ax2.annotate(f'{yval:.2f}',
                 xy=(bar.get_x() + bar.get_width() / 2, yval),
                 xytext=(0, -11), textcoords="offset points",
                 ha='center', va='top', fontsize=9, fontweight='bold')

for bar in bars4:
    yval = bar.get_height()
    ax2.annotate(f'{yval:.2f}',
                 xy=(bar.get_x() + bar.get_width() / 2, yval),
                 xytext=(0, -11), textcoords="offset points",
                 ha='center', va='top', fontsize=9, fontweight='bold')

ax2.legend(loc='lower left', frameon=True, framealpha=0.9)

# X-axis tick labels
xticklabels = []
for yr, intensity, iod in zip(years, intensities, iod_flags):
    tag = '+ IOD' if iod else 'Pure'
    xticklabels.append(f"{yr}\n({intensity})\n[{tag}]")

ax2.set_xticks(x)
ax2.set_xticklabels(xticklabels, fontsize=10, fontweight='bold')

plt.tight_layout()

# Save figure
plot_path = os.path.join(OUTPUT_DIR, 'm2_elnino_rainfall_anomalies.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"[OK] Plot saved to {plot_path}")

