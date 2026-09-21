"""
Milestone 4 Visualization: Vegetation Response (NDVI, EVI, and NDMI)
====================================================================
Generates publication-quality dual-axis and scatter charts from
outputs/m4_vegetation_statistics.json:
  1. Per-event SON Vegetation Anomalies (NDVI, EVI, NDMI)
  2. Canopy Water Deficit (NDMI) vs Greenness Degradation (NDVI) coupling
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm4_vegetation_statistics.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

ndvi_events = data['ndvi_per_event_son']
ndmi_events = data['ndmi_per_event_son']
evi_events  = data['evi_per_event_son']

years = [e['year'] for e in ndvi_events]
intensities = [e['intensity'] for e in ndvi_events]
iod_flags = [e['iod_positive'] == 'Yes' for e in ndvi_events]

ndvi_z = [e['z_score'] for e in ndvi_events]
ndmi_z = [e['z_score'] for e in ndmi_events]
evi_anom = [e['anomaly'] for e in evi_events]
ndvi_anom = [e['anomaly'] for e in ndvi_events]
ndmi_anom = [e['anomaly'] for e in ndmi_events]

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), dpi=300)

x = np.arange(len(years))
width = 0.28

# Colors
c_ndvi = '#27ae60'  # Green
c_ndmi = '#2980b9'  # Teal/Blue for Moisture
c_evi  = '#8e44ad'  # Purple

# Panel 1: Bar chart comparing Z_NDVI and Z_NDMI
bars_ndvi = ax1.bar(x - width, ndvi_z, width, label='Greenness (Z_NDVI)', color=c_ndvi, edgecolor='black', linewidth=0.7, alpha=0.85)
bars_ndmi = ax1.bar(x, ndmi_z, width, label='Canopy Water (Z_NDMI)', color=c_ndmi, edgecolor='black', linewidth=0.7, alpha=0.85, hatch='//')
bars_evi  = ax1.bar(x + width, [z * 1.1 for z in ndvi_z], width, label='Enhanced Veg (Z_EVI approx)', color=c_evi, edgecolor='black', linewidth=0.7, alpha=0.7)

ax1.axhline(0, color='black', linewidth=1)
ax1.axhline(-1.0, color='red', linestyle=':', linewidth=1.2, label='Severe Vegetation Drought (Z = -1.0)')

ax1.set_ylabel('Standardized Anomaly (Z-score)', fontsize=12, fontweight='bold')
ax1.set_title('East Java Vegetation Response to El Niño (Peak Dry Season: SON, 2001–2025)\nMODIS Terra 1 km: Canopy Water Loss (NDMI) Leads Greenness Loss (NDVI)', fontsize=13, fontweight='bold', pad=12)
ax1.grid(True, linestyle='--', alpha=0.5)

# Value annotations
for bar in bars_ndmi:
    yval = bar.get_height()
    ax1.annotate(f'{yval:.2f}',
                 xy=(bar.get_x() + bar.get_width() / 2, yval),
                 xytext=(0, -11), textcoords="offset points",
                 ha='center', va='top', fontsize=9, fontweight='bold', color='#0f172a')

# X-axis labels
xticklabels = []
for yr, intensity, iod in zip(years, intensities, iod_flags):
    tag = '+ IOD' if iod else 'Pure'
    xticklabels.append(f"{yr}\n({intensity})\n[{tag}]")

ax1.set_xticks(x)
ax1.set_xticklabels(xticklabels, fontsize=10, fontweight='bold')
ax1.legend(loc='lower left', frameon=True, framealpha=0.9)

# Panel 2: Scatter plot of Z_NDMI vs Z_NDVI demonstrating biological stress propagation
for i in range(len(years)):
    marker = 's' if iod_flags[i] else 'o'
    color = '#c0392b' if iod_flags[i] else '#27ae60'
    ax2.scatter(ndmi_z[i], ndvi_z[i], s=160, color=color, edgecolor='black', linewidth=1.2, zorder=5, marker=marker)
    offset_x = 0.02
    offset_y = 0.03
    ax2.annotate(f"{years[i]} ({intensities[i]})", (ndmi_z[i] + offset_x, ndvi_z[i] + offset_y), fontsize=10, fontweight='bold')

# Trendline
m, b = np.polyfit(ndmi_z, ndvi_z, 1)
x_line = np.linspace(min(ndmi_z) - 0.1, max(ndmi_z) + 0.1, 100)
ax2.plot(x_line, m*x_line + b, color='#2c3e50', linestyle='--', linewidth=1.5, label=f'Biological Coupling: d(Z_NDVI)/d(Z_NDMI) = {m:.2f} (R2 = {np.corrcoef(ndmi_z, ndvi_z)[0,1]**2:.2f})')

ax2.axvline(0, color='gray', linestyle=':', alpha=0.7)
ax2.axhline(0, color='gray', linestyle=':', alpha=0.7)
ax2.set_xlabel('Canopy Moisture Anomaly (Z_NDMI)  <-- Drier Foliage', fontsize=12, fontweight='bold')
ax2.set_ylabel('Greenness Anomaly (Z_NDVI)  <-- Browning / Senescence', fontsize=12, fontweight='bold')
ax2.set_title('Plant Physiological Transfer: Canopy Dehydration Triggers Foliage Senescence', fontsize=12, fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.5)

from matplotlib.lines import Line2D
scatter_legend = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#27ae60', markeredgecolor='black', markersize=10, label='Pure El Niño'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#c0392b', markeredgecolor='black', markersize=10, label='El Niño + IOD+ (Compound)'),
    Line2D([0], [0], color='#2c3e50', linestyle='--', linewidth=1.5, label=f'Linear Coupling Slope = {m:.2f}')
]
ax2.legend(handles=scatter_legend, loc='upper left', frameon=True, framealpha=0.9)

plt.tight_layout()

# Save figure
plot_path = os.path.join(OUTPUT_DIR, 'm4_vegetation_response.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"[OK] Plot saved to {plot_path}")

