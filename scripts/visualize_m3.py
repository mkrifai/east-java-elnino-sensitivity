"""
Milestone 3 Visualization: Physical Response (Soil Moisture & LST)
==================================================================
Generates publication-quality dual-axis and scatter charts from
outputs/m3_physical_statistics.json:
  1. Per-event SON Soil Moisture Anomaly (m3/m3) vs LST Anomaly (deg C)
  2. Standardized anomalies (Z_SM vs Z_LST) demonstrating land-atmosphere coupling
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm3_physical_statistics.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

sm_events = data['sm_per_event_son']
lst_events = data['lst_per_event_son']

years = [e['year'] for e in sm_events]
intensities = [e['intensity'] for e in sm_events]
iod_flags = [e['iod_positive'] == 'Yes' for e in sm_events]

sm_anom = [e['anomaly'] for e in sm_events]
sm_z = [e['z_score'] for e in sm_events]
lst_anom = [e['anomaly'] for e in lst_events]
lst_z = [e['z_score'] for e in lst_events]

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), dpi=300)

x = np.arange(len(years))
width = 0.36

# Colors
c_sm = '#2980b9'      # Blue for soil moisture
c_sm_iod = '#1a5276'  # Darker blue for compound
c_lst = '#d35400'     # Orange/Red for LST
c_lst_iod = '#922b21' # Darker red for compound

colors_sm = [c_sm_iod if iod else c_sm for iod in iod_flags]
colors_lst = [c_lst_iod if iod else c_lst for iod in iod_flags]

# Panel 1: Bar chart comparing Z_SM (soil drying) and Z_LST (thermal heating)
bars_sm = ax1.bar(x - width/2, sm_z, width, label='Soil Moisture (Z_SM)', color=colors_sm, edgecolor='black', linewidth=0.7, alpha=0.85)
bars_lst = ax1.bar(x + width/2, lst_z, width, label='Daytime LST (Z_LST)', color=colors_lst, edgecolor='black', linewidth=0.7, alpha=0.85, hatch='//')

ax1.axhline(0, color='black', linewidth=1)
ax1.axhline(-1.0, color='blue', linestyle=':', linewidth=1.2, label='Severe Soil Drought (Z = -1.0)')
ax1.axhline(1.0, color='red', linestyle=':', linewidth=1.2, label='Severe Thermal Heating (Z = +1.0)')

ax1.set_ylabel('Standardized Anomaly (Z-score)', fontsize=12, fontweight='bold')
ax1.set_title('East Java Physical Response to El Niño (Peak Dry Season: SON, 2001–2025)\nERA5-Land Root-Zone Soil Moisture (0–28 cm) & MODIS Terra Daytime LST (1 km)', fontsize=13, fontweight='bold', pad=12)
ax1.grid(True, linestyle='--', alpha=0.5)

# Value annotations
for bar in bars_sm:
    yval = bar.get_height()
    ax1.annotate(f'{yval:.2f}',
                 xy=(bar.get_x() + bar.get_width() / 2, yval),
                 xytext=(0, -11), textcoords="offset points",
                 ha='center', va='top', fontsize=9, fontweight='bold', color='#1e3a8a')

for bar in bars_lst:
    yval = bar.get_height()
    ax1.annotate(f'{yval:+.2f}',
                 xy=(bar.get_x() + bar.get_width() / 2, yval),
                 xytext=(0, 4), textcoords="offset points",
                 ha='center', va='bottom', fontsize=9, fontweight='bold', color='#7f1d1d')

# X-axis labels
xticklabels = []
for yr, intensity, iod in zip(years, intensities, iod_flags):
    tag = '+ IOD' if iod else 'Pure'
    xticklabels.append(f"{yr}\n({intensity})\n[{tag}]")

ax1.set_xticks(x)
ax1.set_xticklabels(xticklabels, fontsize=10, fontweight='bold')
ax1.legend(loc='lower left', frameon=True, framealpha=0.9)

# Panel 2: Scatter plot of Z_SM vs Z_LST demonstrating Land-Atmosphere Coupling
for i in range(len(years)):
    marker = 's' if iod_flags[i] else 'o'
    color = '#c0392b' if iod_flags[i] else '#e67e22'
    ax2.scatter(sm_z[i], lst_z[i], s=160, color=color, edgecolor='black', linewidth=1.2, zorder=5, marker=marker)
    offset_x = 0.02
    offset_y = 0.04
    ax2.annotate(f"{years[i]} ({intensities[i]})", (sm_z[i] + offset_x, lst_z[i] + offset_y), fontsize=10, fontweight='bold')

# Trendline (coupling slope)
m, b = np.polyfit(sm_z, lst_z, 1)
x_line = np.linspace(min(sm_z) - 0.1, max(sm_z) + 0.1, 100)
ax2.plot(x_line, m*x_line + b, color='#2c3e50', linestyle='--', linewidth=1.5, label=f'Coupling Fit: d(Z_LST)/d(Z_SM) = {m:.2f} (Evaporative Shutdown)')

ax2.axvline(0, color='gray', linestyle=':', alpha=0.7)
ax2.axhline(0, color='gray', linestyle=':', alpha=0.7)
ax2.set_xlabel('Root-Zone Soil Moisture Anomaly (Z_SM)  <-- Drier', fontsize=12, fontweight='bold')
ax2.set_ylabel('Daytime LST Anomaly (Z_LST)  Hotter -->', fontsize=12, fontweight='bold')
ax2.set_title('Land-Atmosphere Coupling: Evaporative Cooling Breakdown across El Niño Episodes', fontsize=12, fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.5)

from matplotlib.lines import Line2D
scatter_legend = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#e67e22', markeredgecolor='black', markersize=10, label='Pure El Niño'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#c0392b', markeredgecolor='black', markersize=10, label='El Niño + IOD+ (Compound)'),
    Line2D([0], [0], color='#2c3e50', linestyle='--', linewidth=1.5, label=f'Linear Coupling Slope = {m:.2f}')
]
ax2.legend(handles=scatter_legend, loc='upper left', frameon=True, framealpha=0.9)

plt.tight_layout()

# Save figure
plot_path = os.path.join(OUTPUT_DIR, 'm3_physical_response.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"[OK] Plot saved to {plot_path}")

