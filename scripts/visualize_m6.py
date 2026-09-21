"""
Milestone 6 Visualization: Agricultural Sensitivity & Policy Translation
========================================================================
Generates publication-quality charts from outputs/m6_agriculture_policy_statistics.json:
  1. Top 15 Agricultural Drought Risk Regencies in East Java (Mean ASI & Hotspot Area %)
  2. Policy Intervention Zones Distribution and Priority Matrix
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm6_agriculture_policy_statistics.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

districts = data['district_rankings'][:15]  # Top 15

names = [d['district_name'] for d in districts][::-1]
asi_vals = [d['mean_asi'] for d in districts][::-1]
lsi_vals = [d['mean_lsi'] for d in districts][::-1]
crop_fracs = [d['crop_fraction'] * 100 for d in districts][::-1]
hotspot_pcts = [d['critical_hotspot_pct'] for d in districts][::-1]

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=300)

y_pos = np.arange(len(names))

# Colors based on ASI value
colors = ['#c0392b' if asi >= 0.30 else '#e67e22' if asi >= 0.25 else '#f39c12' for asi in asi_vals]

# Panel 1: Horizontal Bar Chart of Agricultural Sensitivity Index (ASI)
bars = ax1.barh(y_pos, asi_vals, color=colors, edgecolor='black', linewidth=0.7, height=0.6, alpha=0.85)

ax1.set_yticks(y_pos)
ax1.set_yticklabels(names, fontsize=10, fontweight='bold')
ax1.set_xlabel('Agricultural Sensitivity Index (ASI = LSI × Cropland Fraction)', fontsize=11, fontweight='bold')
ax1.set_title('Top 15 Most Vulnerable Agricultural Districts in East Java (Deliverable C)\nRanking by Compound Drought Sensitivity × Cropland Exposure', fontsize=12, fontweight='bold', pad=12)
ax1.set_xlim(0, 0.55)
ax1.grid(True, linestyle='--', alpha=0.5)

# Value labels on bars
for bar, asi, crop, lsi in zip(bars, asi_vals, crop_fracs, lsi_vals):
    w = bar.get_width()
    ax1.text(w + 0.008, bar.get_y() + bar.get_height()/2,
             f"ASI: {asi:.3f} (LSI: {lsi:.2f}, Rice/Crop: {crop:.0f}%)",
             va='center', fontsize=9, fontweight='bold')

# Panel 2: Scatter plot of Cropland Fraction vs Landscape Sensitivity (LSI)
all_districts = data['district_rankings']
all_lsi = [d['mean_lsi'] for d in all_districts]
all_crop = [d['crop_fraction'] * 100 for d in all_districts]
all_asi = [d['mean_asi'] for d in all_districts]
all_names = [d['district_name'] for d in all_districts]

sc = ax2.scatter(all_lsi, all_crop, s=[asi * 850 + 50 for asi in all_asi],
                 c=all_asi, cmap='YlOrRd', edgecolor='black', linewidth=0.8, alpha=0.9, zorder=5)

# Tailored annotation offsets to prevent overlap
offsets = {
    'Lamongan': (10, 8),
    'Gresik': (-65, 12),
    'Bojonegoro': (-85, -5),
    'Jombang': (12, 10),
    'Nganjuk': (-65, -15),
    'Tuban': (-45, 15),
    'Ngawi': (14, -8),
    'Kediri': (-55, -10),
    'Mojokerto': (12, -14)
}

for d in all_districts[:9]:
    name = d['district_name']
    ox, oy = offsets.get(name, (10, 5))
    ax2.annotate(f"{name} (#{d['priority_rank']})",
                 (d['mean_lsi'], d['crop_fraction']*100),
                 xytext=(ox, oy), textcoords='offset points',
                 fontsize=8.5, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.25', fc='#fef08a', alpha=0.9, ec='#854d0e', lw=0.6),
                 arrowprops=dict(arrowstyle='->', lw=0.6, color='black', alpha=0.7))

# Threshold lines dividing Policy Intervention Zones
ax2.axvline(0.60, color='#dc2626', linestyle='--', linewidth=1.4, label='High Sensitivity Threshold (LSI = 0.60)')
ax2.axhline(30.0, color='#2563eb', linestyle='--', linewidth=1.4, label='High Cropland Density Threshold (Crop = 30%)')

# Zone annotations
ax2.text(0.615, 62.0, 'ZONE 1: CRITICAL EMERGENCY\nINTERVENTION ZONE\n(Extreme LSI & Cropland)',
         fontsize=8.5, fontweight='bold', color='#991b1b',
         bbox=dict(boxstyle='round,pad=0.35', fc='#fee2e2', ec='#ef4444', lw=1.2, alpha=0.95))

ax2.text(0.62, 5.0, 'ZONE 2: HYDROLOGIC VULNERABILITY\n& CANAL CONVEYANCE ZONE',
         fontsize=8, fontweight='bold', color='#1e3a8a',
         bbox=dict(boxstyle='round,pad=0.3', fc='#dbeafe', ec='#3b82f6', lw=1, alpha=0.95))

ax2.text(0.33, 62.0, 'ZONE 3: RAIN-SHADOW &\nFODDER/ORCHARD ZONE',
         fontsize=8, fontweight='bold', color='#854d0e',
         bbox=dict(boxstyle='round,pad=0.3', fc='#fef9c3', ec='#ca8a04', lw=1, alpha=0.95))

ax2.text(0.33, 5.0, 'ZONE 4: ECOLOGICAL\nCATCHMENT PROTECTION',
         fontsize=8, fontweight='bold', color='#166534',
         bbox=dict(boxstyle='round,pad=0.3', fc='#dcfce7', ec='#22c55e', lw=1, alpha=0.95))

ax2.set_xlabel('Mean Landscape Sensitivity Index (LSI)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Cropland Fraction of District Area (%)', fontsize=11, fontweight='bold')
ax2.set_title('Policy Decision-Support Matrix: Sensitivity × Exposure Grid (Deliverable D)\nBubble size and color represent Agricultural Sensitivity Index (ASI)', fontsize=12, fontweight='bold', pad=12)
ax2.set_xlim(0.31, 0.82)
ax2.set_ylim(-2, 77)
ax2.grid(True, linestyle='--', alpha=0.5)

cbar = plt.colorbar(sc, ax=ax2, pad=0.03, fraction=0.045)
cbar.set_label('Agricultural Sensitivity Index (ASI)', fontsize=10, fontweight='bold')

plt.tight_layout()

# Save figure
plot_path = os.path.join(OUTPUT_DIR, 'm6_agriculture_policy.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"[OK] Plot saved to {plot_path}")

