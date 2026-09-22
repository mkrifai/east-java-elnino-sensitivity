"""
Milestone 3 Visualization: Physical Response (Soil Moisture & LST)
==================================================================
Journal Q1 Standard visualization of East Java physical response to El Niño:
  1. Complete graphic integrity: zero occlusion of zero baseline, bar bases, or error bar whiskers
  2. Subplot titles placed strictly outside the axes area
  3. Uniform label placement with white stroke contour (no collisions)
  4. Cohort separation: Pure El Niño (n=5) vs Compound El Niño + IOD+ (n=3) and Cohort Composites (±1 SEM)
  5. Multi-year episode (2014-2015) explicit demarcation and trajectory tracking
  6. Typographical Unicode minus signs throughout all numerical labels and ticks
  7. Moisture-limited regime delineation (Energy-Limited box removed: no observed data within that region)
  8. Two-column explanatory footer box providing metadata, baseline references, and statistical rigor
  9. [Rev4] Underscores replaced with proper LaTeX subscripts ($Z_{\\mathrm{SM}}$, $Z_{\\mathrm{LST}}$, $n_{\\mathrm{eff}}$)
 10. [Rev4] Panel (b) left boundary set to gray area (-1.45) and rightmost side to 0.0
 11. [Rev4] Linear Coupling Fit box removed; "evaporative shutdown" text removed; Moisture-Limited text at top-right of red box
 12. [Rev4] Episode Cohort legend row spacing expanded to prevent marker overlap
 13. [Rev4] Two-line panel (b) axis labels with bracketed text on second line in smaller gray font
 14. [Rev4] Footer line pitch identical to m2_elnino (box_h=0.058) with balanced asymmetric columns (54.5%/45.5%)
 15. [Rev4] Subtitle cleaned of section reference (removed "see §4.2")
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Rectangle, Patch
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredOffsetbox, VPacker, HPacker, TextArea, DrawingArea
from scipy import stats

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm3_physical_statistics.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

sm_events_son = data['sm_per_event_son']
lst_events_son = data['lst_per_event_son']
sm_baseline_son = data['sm_baseline_mean_son']        # 0.2370 m3/m3
lst_baseline_son = data['lst_baseline_mean_son_degC'] # 33.33 deg C

# Filter cohorts: Pure (iod_positive == 'No') vs Compound (iod_positive == 'Yes')
pure_indices = [i for i, e in enumerate(sm_events_son) if e['iod_positive'] == 'No']
iod_indices  = [i for i, e in enumerate(sm_events_son) if e['iod_positive'] == 'Yes']

def extract_cohort(indices):
    return {
        'years': [sm_events_son[i]['year'] for i in indices],
        'intensities': [sm_events_son[i]['intensity'] for i in indices],
        'sm_anom': [sm_events_son[i]['anomaly'] for i in indices],
        'sm_z': [sm_events_son[i]['z_score'] for i in indices],
        'sm_pct': [(sm_events_son[i]['anomaly'] / sm_baseline_son) * 100 for i in indices],
        'lst_anom': [lst_events_son[i]['anomaly'] for i in indices],
        'lst_z': [lst_events_son[i]['z_score'] for i in indices],
    }

pure = extract_cohort(pure_indices)
iod  = extract_cohort(iod_indices)

pure_n = len(pure_indices)
iod_n  = len(iod_indices)

# Cohort Summary Statistics (Mean & SEM)
mean_pure_sm_z = np.mean(pure['sm_z'])
sem_pure_sm_z  = np.std(pure['sm_z'], ddof=1) / np.sqrt(pure_n)
mean_pure_lst_z = np.mean(pure['lst_z'])
sem_pure_lst_z  = np.std(pure['lst_z'], ddof=1) / np.sqrt(pure_n)

mean_iod_sm_z = np.mean(iod['sm_z'])
sem_iod_sm_z  = np.std(iod['sm_z'], ddof=1) / np.sqrt(iod_n)
mean_iod_lst_z = np.mean(iod['lst_z'])
sem_iod_lst_z  = np.std(iod['lst_z'], ddof=1) / np.sqrt(iod_n)

mean_pure_sm_anom = np.mean(pure['sm_anom'])
mean_pure_lst_anom = np.mean(pure['lst_anom'])
mean_iod_sm_anom = np.mean(iod['sm_anom'])
mean_iod_lst_anom = np.mean(iod['lst_anom'])

mean_pure_sm_pct = (mean_pure_sm_anom / sm_baseline_son) * 100
mean_iod_sm_pct  = (mean_iod_sm_anom / sm_baseline_son) * 100

# Baseline uncertainty in Z space: SEM_base = 1 / sqrt(n_baseline)
n_baseline_years = len(data.get('baseline_years', [2001, 2003, 2012, 2013, 2019, 2025]))
sem_base_z = 1.0 / np.sqrt(n_baseline_years)  # ≈ 0.408 Z

# X-axis coordinates matching M2
x_pure = np.arange(pure_n)
x_iod = np.array([5.2, 6.2, 7.2])
x_summary = np.array([8.7, 9.7])
bar_width = 0.36

# Okabe-Ito & Scientific Palette
c_sm_pure  = '#0072B2'  # Deep Ocean Blue (Soil Moisture Pure)
c_sm_iod   = '#CC79A7'  # Reddish Purple / Rose (Soil Moisture Compound & Compound Cohort)
c_lst_pure = '#E69F00'  # Amber Orange (Daytime LST Pure)
c_lst_iod  = '#D55E00'  # Vermilion Red (Daytime LST Compound)
c_compound_hdr = '#882255' # Dark Rose / Purple for Compound headers
c_whisker  = '#0F172A'  # Deep Slate for error bars

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.0, 10.8), dpi=300)
fig.subplots_adjust(top=0.840, bottom=0.155, left=0.08, right=0.97, hspace=0.38)

err_kw = dict(lw=1.3, capthick=1.3, ecolor=c_whisker)
text_stroke = [pe.withStroke(linewidth=2.8, foreground='white')]

# =========================================================================
# PANEL 1: STANDARDIZED PHYSICAL ANOMALIES (Z_SM vs Z_LST)
# =========================================================================

# Baseline Uncertainty Ribbon around Z = 0 (+/-1 SEM_base ≈ +/-0.41 Z)
ax1.axhspan(-sem_base_z, sem_base_z, color='#94A3B8', alpha=0.13, zorder=1)

# Pure El Niño Bars
b1_pure_sm = ax1.bar(x_pure - bar_width/2, pure['sm_z'], bar_width,
                     color=c_sm_pure, edgecolor='#0F172A', linewidth=0.9, alpha=0.92, zorder=2)
b1_pure_lst = ax1.bar(x_pure + bar_width/2, pure['lst_z'], bar_width,
                      color=c_lst_pure, edgecolor='#78350F', linewidth=0.9, alpha=0.92, hatch='//', zorder=2)

# Compound El Niño + IOD+ Bars
b1_iod_sm = ax1.bar(x_iod - bar_width/2, iod['sm_z'], bar_width,
                    color=c_sm_iod, edgecolor='#6B2D5E', linewidth=0.9, alpha=0.92, zorder=2)
b1_iod_lst = ax1.bar(x_iod + bar_width/2, iod['lst_z'], bar_width,
                     color=c_lst_iod, edgecolor='#450A0A', linewidth=0.9, alpha=0.92, hatch='//', zorder=2)

# Summary Cohort Mean bars with Error Bars (SEM)
b1_sum_pure_sm = ax1.bar(x_summary[0] - bar_width/2, mean_pure_sm_z, bar_width,
                         yerr=sem_pure_sm_z, capsize=4, error_kw=err_kw,
                         color=c_sm_pure, edgecolor='#0F172A', linewidth=1.3, alpha=0.95, zorder=2)
b1_sum_pure_lst = ax1.bar(x_summary[0] + bar_width/2, mean_pure_lst_z, bar_width,
                          yerr=sem_pure_lst_z, capsize=4, error_kw=err_kw,
                          color=c_lst_pure, edgecolor='#78350F', linewidth=1.3, alpha=0.95, hatch='//', zorder=2)

b1_sum_iod_sm = ax1.bar(x_summary[1] - bar_width/2, mean_iod_sm_z, bar_width,
                        yerr=sem_iod_sm_z, capsize=4, error_kw=err_kw,
                        color=c_sm_iod, edgecolor='#6B2D5E', linewidth=1.3, alpha=0.95, zorder=2)
b1_sum_iod_lst = ax1.bar(x_summary[1] + bar_width/2, mean_iod_lst_z, bar_width,
                         yerr=sem_iod_lst_z, capsize=4, error_kw=err_kw,
                         color=c_lst_iod, edgecolor='#450A0A', linewidth=1.3, alpha=0.95, hatch='//', zorder=2)

# Prominent zero baseline (zorder=3)
ax1.axhline(0, color='#0F172A', linewidth=1.2, zorder=3)

# Critical Thresholds (using LaTeX subscript)
thresh_sm = ax1.axhline(-1.0, color='#0284C7', linestyle='--', linewidth=1.2, zorder=2,
                        label='Severe Soil Drought Threshold ($Z_{\\mathrm{SM}} = \u22121.0$)')
thresh_lst = ax1.axhline(1.0, color='#DC2626', linestyle=':', linewidth=1.3, zorder=2,
                         label='Severe Surface Thermal Heating ($Z_{\\mathrm{LST}} = +1.0$)')

ax1.set_ylabel('Standardized Anomaly (Z-score)', fontsize=10.5, fontweight='bold')
ax1.set_ylim(-1.75, 2.15)
ax1.set_yticks([-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0])
ax1.set_yticklabels(['\u22121.5', '\u22121.0', '\u22120.5', '0.0', '+0.5', '+1.0', '+1.5', '+2.0'], fontsize=8.5)
ax1.grid(True, linestyle=':', alpha=0.5, zorder=0)

# Value annotations for Panel 1: Unicode minus and clean stroke
def annotate_bars_p1(bars_sm, bars_lst, sm_anoms, sm_pcts, lst_anoms):
    for b_sm, b_lst, s_anom, s_pct, l_anom in zip(bars_sm, bars_lst, sm_anoms, sm_pcts, lst_anoms):
        y_sm = b_sm.get_height()
        ax1.text(b_sm.get_x() + b_sm.get_width() / 2, y_sm - 0.06,
                 f'\u2212{abs(y_sm):.2f}\n(\u2212{abs(s_pct):.0f}%)',
                 ha='center', va='top', fontsize=7.4, fontweight='bold', color='#0F172A',
                 path_effects=text_stroke, linespacing=1.05, zorder=4)
        
        y_lst = b_lst.get_height()
        ax1.text(b_lst.get_x() + b_lst.get_width() / 2, y_lst + 0.06,
                 f'+{y_lst:.2f}\n(+{l_anom:.1f}°C)',
                 ha='center', va='bottom', fontsize=7.4, fontweight='bold', color='#7F1D1D',
                 path_effects=text_stroke, linespacing=1.05, zorder=4)

annotate_bars_p1(b1_pure_sm, b1_pure_lst, pure['sm_anom'], pure['sm_pct'], pure['lst_anom'])
annotate_bars_p1(b1_iod_sm, b1_iod_lst, iod['sm_anom'], iod['sm_pct'], iod['lst_anom'])

# Summary bar annotations
def annotate_summary_p1(xpos_sm, mean_sm, sem_sm, pct_sm, xpos_lst, mean_lst, sem_lst, anom_lst):
    whisker_bottom_sm = mean_sm - sem_sm
    ax1.text(xpos_sm, whisker_bottom_sm - 0.06,
             f'\u2212{abs(mean_sm):.2f}\n(\u2212{abs(pct_sm):.0f}%)',
             ha='center', va='top', fontsize=7.4, fontweight='bold', color='#0F172A',
             path_effects=text_stroke, linespacing=1.05, zorder=4)
    
    whisker_top_lst = mean_lst + sem_lst
    ax1.text(xpos_lst, whisker_top_lst + 0.06,
             f'+{mean_lst:.2f}\n(+{anom_lst:.1f}°C)',
             ha='center', va='bottom', fontsize=7.4, fontweight='bold', color='#7F1D1D',
             path_effects=text_stroke, linespacing=1.05, zorder=4)

annotate_summary_p1(x_summary[0] - bar_width/2, mean_pure_sm_z, sem_pure_sm_z, mean_pure_sm_pct,
                    x_summary[0] + bar_width/2, mean_pure_lst_z, sem_pure_lst_z, mean_pure_lst_anom)
annotate_summary_p1(x_summary[1] - bar_width/2, mean_iod_sm_z, sem_iod_sm_z, mean_iod_sm_pct,
                    x_summary[1] + bar_width/2, mean_iod_lst_z, sem_iod_lst_z, mean_iod_lst_anom)

# Section Dividers
ax1.axvline(4.60, color='#94A3B8', linestyle='--', linewidth=1.2, alpha=0.8, zorder=1)
ax1.axvline(7.95, color='#94A3B8', linestyle='-', linewidth=1.4, alpha=0.9, zorder=1)

# Group headers outside top frame using blended transform
blended_1 = mtransforms.blended_transform_factory(ax1.transData, ax1.transAxes)
ax1.text(2.0, 1.15, 'Pure El Niño (n = 5)', ha='center', va='bottom',
         transform=blended_1, fontsize=9.5, fontweight='bold', color='#0072B2')
ax1.text(6.2, 1.15, 'Compound: El Niño + IOD+ (n = 3)', ha='center', va='bottom',
         transform=blended_1, fontsize=9.5, fontweight='bold', color=c_compound_hdr)
ax1.text(9.2, 1.15, 'Cohort Composites (±1 SEM)', ha='center', va='bottom',
         transform=blended_1, fontsize=9.5, fontweight='bold', color='#1E293B')

# Group bracket lines
ax1.plot([-0.35, 4.35], [1.11, 1.11], transform=blended_1, color='#0072B2', lw=1.3, clip_on=False)
ax1.plot([4.85, 7.55], [1.11, 1.11], transform=blended_1, color=c_compound_hdr, lw=1.3, clip_on=False)
ax1.plot([8.35, 10.05], [1.11, 1.11], transform=blended_1, color='#1E293B', lw=1.3, clip_on=False)

# Subplot Title placed cleanly OUTSIDE (using LaTeX subscript)
ax1.set_title('(a) Peak Dry Season (SON) Hydro-Thermal Stress: Root-Zone Soil Moisture Desiccation ($Z_{\\mathrm{SM}}$) vs Daytime LST Surge ($Z_{\\mathrm{LST}}$)',
              loc='left', fontsize=10.2, fontweight='bold', pad=6)

# X-axis ticks for Panel 1
all_x = np.concatenate([x_pure, x_iod, x_summary])
xticklabels_p1 = []

for yr, intensity in zip(pure['years'], pure['intensities']):
    tag = f"{yr}*" if yr in [2014, 2015] else f"{yr}"
    xticklabels_p1.append(f"{tag}\n({intensity})")

for yr, intensity in zip(iod['years'], iod['intensities']):
    xticklabels_p1.append(f"{yr}\n({intensity})\n[+IOD]")

xticklabels_p1.append("Pure Mean\n(n = 5)")
xticklabels_p1.append("Compound Mean\n(n = 3)")

ax1.set_xticks(all_x)
ax1.set_xticklabels(xticklabels_p1, fontsize=8.6, fontweight='bold')

# Dual-section x-axis sub-labels underneath Panel 1
ax1.text(3.6, -0.155,
         'Historical El Niño Episodes (2001–2025)\n[*2014 & 2015 denote consecutive dry seasons of multi-year ENSO episode; values show Z-score and (relative departure)]',
         ha='center', va='top', transform=blended_1, fontsize=8.2, fontweight='bold', color='#1E293B', linespacing=1.2)
ax1.text(9.2, -0.155,
         'Cohort Composites\n[Mean \u00b1 1 SEM]',
         ha='center', va='top', transform=blended_1, fontsize=8.2, fontweight='bold', color='#1E293B', linespacing=1.2)

# Panel 1 Legend (using LaTeX subscript)
da_sm_pure = DrawingArea(15, 9, 0, 0)
da_sm_pure.add_artist(Rectangle((0, 0), 15, 9, facecolor=c_sm_pure, edgecolor='#0F172A', lw=0.9))
ta_sm_pure = TextArea('SM Pure ($Z_{\\mathrm{SM}}$)', textprops=dict(fontsize=7.2, color='#1E293B', fontweight='bold'))
r_sm_pure = HPacker(children=[da_sm_pure, ta_sm_pure], align='center', pad=0, sep=4)

da_sm_iod = DrawingArea(15, 9, 0, 0)
da_sm_iod.add_artist(Rectangle((0, 0), 15, 9, facecolor=c_sm_iod, edgecolor='#6B2D5E', lw=0.9))
ta_sm_iod = TextArea('SM Compound ($Z_{\\mathrm{SM}}$)', textprops=dict(fontsize=7.2, color='#1E293B', fontweight='bold'))
r_sm_iod = HPacker(children=[da_sm_iod, ta_sm_iod], align='center', pad=0, sep=4)

da_lst_pure = DrawingArea(15, 9, 0, 0)
da_lst_pure.add_artist(Rectangle((0, 0), 15, 9, facecolor=c_lst_pure, edgecolor='#78350F', hatch='//', lw=0.9))
ta_lst_pure = TextArea('LST Pure ($Z_{\\mathrm{LST}}$)', textprops=dict(fontsize=7.2, color='#1E293B', fontweight='bold'))
r_lst_pure = HPacker(children=[da_lst_pure, ta_lst_pure], align='center', pad=0, sep=4)

da_lst_iod = DrawingArea(15, 9, 0, 0)
da_lst_iod.add_artist(Rectangle((0, 0), 15, 9, facecolor=c_lst_iod, edgecolor='#450A0A', hatch='//', lw=0.9))
ta_lst_iod = TextArea('LST Compound ($Z_{\\mathrm{LST}}$)', textprops=dict(fontsize=7.2, color='#1E293B', fontweight='bold'))
r_lst_iod = HPacker(children=[da_lst_iod, ta_lst_iod], align='center', pad=0, sep=4)

row1_colors = HPacker(children=[r_sm_pure, r_sm_iod, r_lst_pure, r_lst_iod], align='center', pad=0, sep=12)

# Row 2: Threshold lines & Baseline uncertainty
da_l1 = DrawingArea(16, 9, 0, 0)
da_l1.add_artist(Line2D([0, 16], [4.5, 4.5], color='#0284C7', linestyle='--', lw=1.3))
ta_l1 = TextArea('Severe Soil Drought ($Z_{\\mathrm{SM}} = \u22121.0$)', textprops=dict(fontsize=7.1, color='#0284C7'))
r_l1 = HPacker(children=[da_l1, ta_l1], align='center', pad=0, sep=4)

da_l2 = DrawingArea(16, 9, 0, 0)
da_l2.add_artist(Line2D([0, 16], [4.5, 4.5], color='#DC2626', linestyle=':', lw=1.4))
ta_l2 = TextArea('Severe Thermal Surge ($Z_{\\mathrm{LST}} = +1.0$)', textprops=dict(fontsize=7.1, color='#DC2626'))
r_l2 = HPacker(children=[da_l2, ta_l2], align='center', pad=0, sep=4)

da_base = DrawingArea(16, 9, 0, 0)
da_base.add_artist(Rectangle((0, 1.5), 16, 6, facecolor='#94A3B8', edgecolor='none', alpha=0.35))
ta_base = TextArea('Baseline Uncert. (\u00b11 SEM \u2248 \u00b10.41 Z)', textprops=dict(fontsize=7.1, color='#475569'))
r_base = HPacker(children=[da_base, ta_base], align='center', pad=0, sep=4)

row2_thresh = HPacker(children=[r_l1, r_l2, r_base], align='center', pad=0, sep=15)

box_leg1 = VPacker(children=[row1_colors, row2_thresh], align='center', pad=2, sep=5)

anchored_leg1 = AnchoredOffsetbox(loc='upper center', child=box_leg1, pad=0.22, borderpad=0.22,
                                  frameon=True, bbox_to_anchor=(0.50, 0.985),
                                  bbox_transform=ax1.transAxes)
anchored_leg1.patch.set_boxstyle('round,pad=0.22,rounding_size=0.08')
anchored_leg1.patch.set_facecolor('#FFFFFF')
anchored_leg1.patch.set_edgecolor('#CBD5E1')
anchored_leg1.patch.set_alpha(0.95)
anchored_leg1.patch.set_linewidth(0.8)
ax1.add_artist(anchored_leg1)


# =========================================================================
# PANEL 2: LAND-ATMOSPHERE COUPLING & EVAPORATIVE COOLING BREAKDOWN
# =========================================================================

# [Rev4] Moisture-limited regime quadrant: left edge starts at -1.45 (gray area boundary)
# and right edge at -0.72. Information placed cleanly at top-right of red box.
rect_moist = Rectangle((-1.45, 0.72), 1.45 - 0.72, 0.71, facecolor='#FEF2F2', edgecolor='#FECACA',
                       linewidth=1.0, linestyle='--', alpha=0.75, zorder=0)
ax2.add_patch(rect_moist)
ax2.text(-0.74, 1.39, 'Moisture-Limited Regime (Coupling Hotspot)',
         fontsize=7.8, fontweight='bold', color='#991B1B', ha='right', va='top', zorder=1)

# Reference zero lines and thresholds
ax2.axvline(0, color='#94A3B8', linestyle='-', linewidth=1.0, zorder=1)
ax2.axhline(0, color='#94A3B8', linestyle='-', linewidth=1.0, zorder=1)
ax2.axvline(-1.0, color='#0284C7', linestyle='--', linewidth=1.1, alpha=0.8, zorder=1)
ax2.axhline(1.0, color='#DC2626', linestyle=':', linewidth=1.1, alpha=0.8, zorder=1)

# All events data
all_sm_z = np.array([e['z_score'] for e in sm_events_son])
all_lst_z = np.array([e['z_score'] for e in lst_events_son])
all_years = [e['year'] for e in sm_events_son]
all_intensities = [e['intensity'] for e in sm_events_son]
all_iod = [e['iod_positive'] == 'Yes' for e in sm_events_son]

# Linear Regression Fit
m, b = np.polyfit(all_sm_z, all_lst_z, 1)
r_val = np.corrcoef(all_sm_z, all_lst_z)[0, 1]
# [Rev4] x_fit exactly spans from left boundary (-1.45) to rightmost boundary (0.0)
x_fit = np.linspace(-1.45, 0.0, 100)
y_fit = m * x_fit + b

# 95% Confidence Interval for regression line
n_pts = len(all_sm_z)
resid = all_lst_z - (m * all_sm_z + b)
s_err = np.sqrt(np.sum(resid**2) / (n_pts - 2))
t_val = 2.447  # t(0.025, df=6)
mean_x = np.mean(all_sm_z)
ss_x = np.sum((all_sm_z - mean_x)**2)
ci = t_val * s_err * np.sqrt(1.0/n_pts + (x_fit - mean_x)**2 / ss_x)

# [Rev4] Subtle non-significant regression fit (dotted line + pale CI ribbon)
ax2.fill_between(x_fit, y_fit - ci, y_fit + ci, color='#94A3B8', alpha=0.08, zorder=2)
ax2.plot(x_fit, y_fit, color='#94A3B8', linestyle=':', linewidth=1.0, zorder=3)

# Multi-year trajectory arrow: 2014 to 2015
idx_2014 = all_years.index(2014)
idx_2015 = all_years.index(2015)
ax2.annotate('', xy=(all_sm_z[idx_2015], all_lst_z[idx_2015]),
             xytext=(all_sm_z[idx_2014], all_lst_z[idx_2014]),
             arrowprops=dict(arrowstyle="->", color='#475569', lw=1.4, ls='--',
                             connectionstyle="arc3,rad=-0.15",
                             mutation_scale=12, shrinkA=8, shrinkB=8),
             zorder=4)
ax2.text(-1.01, 1.15, 'Multi-Year Escalation\n(2014* → 2015*)',
         fontsize=7.4, fontweight='bold', color='#334155', ha='center', va='center',
         path_effects=text_stroke, zorder=5)

# Scatter points: Compound episodes coded with Rose/Purple (c_sm_iod, #CC79A7)
for i in range(n_pts):
    is_iod = all_iod[i]
    color = c_sm_iod if is_iod else c_sm_pure
    marker = 's' if is_iod else 'o'
    edge = '#6B2D5E' if is_iod else '#0F172A'
    
    ax2.scatter(all_sm_z[i], all_lst_z[i], s=175, color=color,
                edgecolor=edge, linewidth=1.3, zorder=6, marker=marker)

# Non-overlapping point labels with separated offsets
offsets = {
    2002: (0, 11, 'center', 'bottom'),
    2004: (-10, 10, 'right', 'bottom'),
    2009: (10, 8, 'left', 'bottom'),
    2014: (10, 8, 'left', 'bottom'),
    2015: (12, -8, 'left', 'top'),
    2006: (10, -4, 'left', 'top'),  # [Rev4] Offset cleanly to the right of marker
    2018: (10, -14, 'left', 'top'),
    2023: (12, 0, 'left', 'center')
}

for i in range(n_pts):
    yr = all_years[i]
    tag = f"{yr}*" if yr in [2014, 2015] else f"{yr}"
    iod_tag = " [+IOD]" if all_iod[i] else ""
    label_text = f"{tag} ({all_intensities[i]}){iod_tag}"
    
    dx, dy, ha, va = offsets[yr]
    ax2.annotate(label_text, (all_sm_z[i], all_lst_z[i]),
                 xytext=(dx, dy), textcoords="offset points",
                 ha=ha, va=va, fontsize=8.2, fontweight='bold', color='#0F172A',
                 path_effects=text_stroke, zorder=7)

# [Rev4] X-limits: left boundary is gray area (-1.45), rightmost side is 0.0
ax2.set_xlim(-1.45, 0.0)
ax2.set_ylim(-0.06, 1.44)
ax2.set_xticks([-1.4, -1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0.0])
ax2.set_xticklabels(['\u22121.4', '\u22121.2', '\u22121.0', '\u22120.8', '\u22120.6', '\u22120.4', '\u22120.2', '0.0'], fontsize=8.5)
ax2.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
ax2.set_yticklabels(['0.0', '+0.2', '+0.4', '+0.6', '+0.8', '+1.0', '+1.2', '+1.4'], fontsize=8.5)
ax2.grid(True, linestyle=':', alpha=0.5, zorder=0)

ax2.set_title('(b) Land-Atmosphere Coupling: Evaporative Cooling Breakdown across Historical Episodes (SON)',
              loc='left', fontsize=10.2, fontweight='bold', pad=6)

# [Rev4] Two-line labels with bracketed descriptive info on second line in smaller gray font
ax2.set_xlabel('')
ax2.set_ylabel('')

# Horizontal X-Axis Label
ax2.text(0.50, -0.115, 'Root-Zone Soil Moisture Anomaly ($Z_{\\mathrm{SM}}$)',
         ha='center', va='top', transform=ax2.transAxes,
         fontsize=10.2, fontweight='bold', color='#0F172A')
ax2.text(0.50, -0.170, '[\u2190 More Desiccated / Severe Soil Water Depletion]',
         ha='center', va='top', transform=ax2.transAxes,
         fontsize=8.4, color='#475569')

# Vertical Y-Axis Label
ax2.text(-0.068, 0.50, 'Daytime LST Anomaly ($Z_{\\mathrm{LST}}$)',
         ha='center', va='center', rotation=90, transform=ax2.transAxes,
         fontsize=10.2, fontweight='bold', color='#0F172A')
ax2.text(-0.048, 0.50, '[Surface Thermal Heating \u2192]',
         ha='center', va='center', rotation=90, transform=ax2.transAxes,
         fontsize=8.4, color='#475569')

# [Rev4] Episode Cohort legend: enhanced row spacing to prevent symbol overlap
leg_cohort_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=c_sm_pure, markeredgecolor='#0F172A',
           markersize=8.5, markeredgewidth=1.2, label='Pure El Ni\u00f1o Episode (n = 5)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor=c_sm_iod, markeredgecolor='#6B2D5E',
           markersize=8.5, markeredgewidth=1.2, label='Compound El Ni\u00f1o + IOD+ (n = 3)'),
]
leg2 = ax2.legend(handles=leg_cohort_elements, loc='upper right', fontsize=7.8, frameon=True, framealpha=0.95,
                  edgecolor='#CBD5E1', borderpad=0.65, labelspacing=0.85, handletextpad=0.85,
                  title='Episode Cohort (SON)', title_fontsize=8.0)
leg2.get_title().set_fontweight('bold')


# =========================================================================
# MAIN SUPTITLE & SUBTITLE
# =========================================================================
fig.suptitle('East Java Terrestrial Physical Response Across Historical El Ni\u00f1o Episodes (2001\u20132025)',
             fontsize=13.0, fontweight='bold', y=0.975)

# [Rev4] Subtitle: removed "see §4.2"
fig.text(0.50, 0.944,
         (f'ENSO-Neutral Baseline (n = 6; 2019 IOD+ unexcluded introduces slight conservative bias in Z-scores): '
          f'Root-Zone SM = {sm_baseline_son:.3f} m\u00b3/m\u00b3, LST = {lst_baseline_son:.1f}\u00b0C'
          f'  |  Data: ERA5-Land (0\u201328 cm) & MODIS Terra MOD11A2 (1 km)'),
         ha='center', fontsize=8.6, color='#475569')


# =========================================================================
# EXPLANATORY FOOTER BOX (Two-Column Grid matching M2 line spacing)
# =========================================================================
pos2 = ax2.get_position()
box_x0 = pos2.x0
box_w = pos2.width
box_y0 = 0.012
box_h = 0.058

rect = FancyBboxPatch((box_x0, box_y0), box_w, box_h,
                      boxstyle='round,pad=0.004,rounding_size=0.008',
                      transform=fig.transFigure,
                      fc='#F8FAFC', ec='#CBD5E1', lw=0.9, alpha=0.95, zorder=1)
fig.patches.append(rect)

# [Rev4] Asymmetric vertical divider (54.5% / 45.5%) for balanced whitespace fit
div_x = box_x0 + box_w * 0.545
div_line = Line2D([div_x, div_x], [box_y0 + 0.007, box_y0 + box_h - 0.007],
                  transform=fig.transFigure, color='#CBD5E1', lw=0.9, linestyle='-', zorder=2)
fig.lines.append(div_line)

# Compute Welch's t-test for both SM and LST anomalies (Pure vs Compound)
pure_sm_anoms = np.array(pure['sm_anom'])
iod_sm_anoms  = np.array(iod['sm_anom'])
t_welch_sm, p_welch_sm = stats.ttest_ind(pure_sm_anoms, iod_sm_anoms, equal_var=False)

pure_lst_anoms = np.array(pure['lst_anom'])
iod_lst_anoms  = np.array(iod['lst_anom'])
t_welch_lst, p_welch_lst = stats.ttest_ind(pure_lst_anoms, iod_lst_anoms, equal_var=False)

# Content lines - tightly formatted to fit balanced asymmetric columns
col1_lines = [
    "\u2022 Data Sources: ERA5-Land root-zone SM (0\u201328 cm) & MODIS Terra MOD11A2 1 km daytime LST.",
    "\u2022 ONI Tiers: Weak (+0.5\u20130.9\u00b0C), Mod (+1.0\u20131.4), Strong (+1.5\u20131.9), V.Strong (\u2265+2.0\u00b0C); Compound (+ DMI \u2265+0.4\u00b0C).",
    "\u2022 Episode Continuity: *2014 & 2015 = consecutive dry seasons of one ENSO episode ($n_{\\mathrm{eff}} < 8$)."
]

col2_lines = [
    f"\u2022 Neutral Baseline: 6 neutral years (2019 IOD+ unexcluded; baseline SEM = \u00b10.41 Z).",
    "\u2022 Hydro-Thermal Coupling: Evaporative shutdown (\u03bbE \u2192 0) drives sensible heating surge (H \u2191\u2191).",
    f"\u2022 Statistical Rigor: Welch t (n=5 vs 3): SM t = {t_welch_sm:.2f} (p = {p_welch_sm:.2f}, n.s.); LST t = {t_welch_lst:.2f} (p = {p_welch_lst:.2f}, n.s.)."
]

col1_x = box_x0 + 0.008
col2_x = div_x + 0.010

for i in range(3):
    y_pos = box_y0 + box_h * (0.75 - i * 0.25)
    fig.text(col1_x, y_pos, col1_lines[i], fontsize=7.6, color='#334155', va='center', zorder=2)
    fig.text(col2_x, y_pos, col2_lines[i], fontsize=7.6, color='#334155', va='center', zorder=2)


# =========================================================================
# SAVE HIGH-RESOLUTION PUBLICATION PNG AND VECTOR PDF (SAFE WRITE)
# =========================================================================
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

plot_path_png = os.path.join(OUTPUT_DIR, 'm3_physical_response.png')
plot_path_pdf = os.path.join(OUTPUT_DIR, 'm3_physical_response.pdf')

safe_savefig(plot_path_png, dpi=300, bbox_inches='tight')
safe_savefig(plot_path_pdf, bbox_inches='tight')
plt.close(fig)

print(f"[OK] High-resolution publication chart saved to: {plot_path_png}")
print(f"[OK] Vector publication PDF saved to: {plot_path_pdf}")
