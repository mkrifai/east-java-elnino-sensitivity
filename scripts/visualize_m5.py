"""
Milestone 5 Visualization: Landscape Sensitivity Atlas & Regimes
================================================================
Generates publication-quality radar and bar comparison charts from
outputs/m5_sensitivity_statistics.json:
  1. Multi-dimensional Landscape Response Signatures (LRS) across 5 Regimes
  2. Spatial distribution & vulnerability hierarchy of East Java landscapes
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm5_sensitivity_statistics.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

regimes = data['cluster_regimes']

regime_ids = [r['regime_id'] for r in regimes]
regime_names = [r['regime_name'] for r in regimes]
areas_pct = [r['area_pct'] for r in regimes]
lsi_vals = [r['mean_lsi'] for r in regimes]

z_p = [r['z_p'] for r in regimes]
z_sm = [r['z_sm'] for r in regimes]
z_lst = [r['z_lst'] for r in regimes]
z_ndvi = [r['z_ndvi'] for r in regimes]
z_ndmi = [r['z_ndmi'] for r in regimes]

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), dpi=300)

# Colors for regimes (from Resilient green to Critical Vulnerability red)
regime_colors = ['#27ae60', '#2980b9', '#f39c12', '#e67e22', '#c0392b']

# Panel 1: Bar Chart of Multi-Variable Profiles per Regime
features = ['Rainfall (Z_P)', 'Soil Moisture (Z_SM)', 'Daytime LST (Z_LST)', 'Greenness (Z_NDVI)', 'Canopy Water (Z_NDMI)']
x = np.arange(len(features))
width = 0.15

for i, r in enumerate(regimes):
    vals = [r['z_p'], r['z_sm'], r['z_lst'], r['z_ndvi'], r['z_ndmi']]
    ax1.bar(x + (i - 2)*width, vals, width, label=f"R{r['regime_id']}: {r['regime_name'][:32]}... ({r['area_pct']}%)",
            color=regime_colors[i], edgecolor='black', linewidth=0.6, alpha=0.85)

ax1.axhline(0, color='black', linewidth=1)
ax1.set_xticks(x)
ax1.set_xticklabels(features, fontsize=11, fontweight='bold')
ax1.set_ylabel('Standardized Anomaly (Z-score)', fontsize=12, fontweight='bold')
ax1.set_title('Landscape Response Signatures (LRS) Across 5 Clustered Regimes\nPhase 7 & 8: Machine Learning Centroid Profiling', fontsize=12, fontweight='bold', pad=12)
ax1.legend(loc='lower left', fontsize=8.5, frameon=True, framealpha=0.95)
ax1.grid(True, linestyle='--', alpha=0.5)

# Panel 2: Landscape Sensitivity Index (LSI) & Area Distribution
y_pos = np.arange(len(regimes))
bars = ax2.barh(y_pos, lsi_vals, color=regime_colors, edgecolor='black', linewidth=0.8, alpha=0.85, height=0.55)

ax2.set_yticks(y_pos)
ax2.set_yticklabels([f"Regime {r['regime_id']}\n({r['area_pct']}%)" for r in regimes], fontsize=10, fontweight='bold')
ax2.set_xlabel('Composite Landscape Sensitivity Index (LSI: 0 to 1)', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 1.0)
ax2.set_title('Hierarchical Landscape Vulnerability Ranking (Deliverable B)\nFrom Buffered Highlands (0.45) to Hyper-Sensitive Plains (0.66)', fontsize=12, fontweight='bold', pad=12)
ax2.grid(True, linestyle='--', alpha=0.5)

# Annotations
for bar, r in zip(bars, regimes):
    width_val = bar.get_width()
    ax2.text(width_val + 0.02, bar.get_y() + bar.get_height()/2,
             f"LSI: {r['mean_lsi']:.2f} | Area: {r['area_km2']:.0f} km²\n{r['regime_name'][:40]}",
             va='center', fontsize=9, fontweight='bold')

plt.tight_layout()

# Save figure
plot_path = os.path.join(OUTPUT_DIR, 'm5_landscape_sensitivity.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"[OK] Plot saved to {plot_path}")

