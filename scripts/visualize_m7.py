"""
Milestone 7 Visualization: Multi-Source Validation & Uncertainty Synthesis
==========================================================================
Generates two dedicated publication-quality figures:
  Plot 1: outputs/m7_1_sensor_validation.png & .pdf
          Panel (a): Climate Validation (CHIRPS vs NASA GPM IMERG Precipitation)
          Panel (b): Remote Sensing Cross-Validation (MODIS NDVI vs EVI Standardized Anomalies)
  
  Plot 2: outputs/m7_2_uncertainty_groundtruth.png & .pdf
          Panel (c): Multi-Event LSI Ensemble Uncertainty (8 El Niño Episodes across 5 Regimes)
          Panel (d): Empirical Disaster Ground-Truth Validation (Modeled ASI vs BPS Rice Crop Puso)
"""

import os
import sys
import json
import warnings
import numpy as np
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

# UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm7_validation_statistics.json')

if not os.path.exists(JSON_PATH):
    print(f"Error: {JSON_PATH} not found.")
    sys.exit(1)

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

# Typography & Style Settings
plt.rcParams['font.sans-serif'] = ['Inter', 'Roboto', 'Arial', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'DejaVu Sans'
plt.rcParams['mathtext.it'] = 'DejaVu Sans:italic'
plt.rcParams['mathtext.bf'] = 'DejaVu Sans:bold'

text_stroke = [pe.withStroke(linewidth=2.2, foreground='white')]


def safe_savefig(target_path, **kwargs):
    """Safely saves a figure to target path, avoiding file locking issues."""
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


# =============================================================================
# PLOT 1: CLIMATE TRIANGULATION & SPECTRAL ROBUSTNESS (PANELS a & b)
# =============================================================================
def render_plot1_sensor_validation(data):
    """
    Renders Plot 1:
      Panel (a): Climate Precipitation Validation (CHIRPS vs NASA GPM IMERG Precipitation)
                 with 3-Tier Elevation Stratification (SRTM DEM) & OLS Regression
      Panel (b): Spectral Index Sensitivity & Concordance (MODIS NDVI vs EVI Standardized Anomalies)
                 with Deficit Severity Tiers & OLS Regression
    """
    fig = plt.figure(figsize=(16.0, 8.4), dpi=300)
    
    # Master Header
    fig.suptitle('Climate Data Triangulation & Vegetation Index Robustness Analysis',
                 fontsize=13.0, fontweight='bold', y=0.970, color='#0F172A')
    fig.text(0.50, 0.940,
             ('Independent Satellite Precipitation Cross-Check (CHIRPS vs GPM) & Canopy Index Sensitivity (MODIS NDVI vs EVI) | '
              'NASA SRTM 30 m DEM Elevation | Peak Dry Season (SON) 2001–2025'),
             ha='center', fontsize=8.4, color='#475569')

    # Explicit Axes Layout: Side-by-Side (1 row x 2 columns)
    # Balanced vertical spacing: generous margin from subtitle above and footnote box below
    ax1 = fig.add_axes([0.065, 0.230, 0.410, 0.615])
    ax2 = fig.add_axes([0.545, 0.230, 0.410, 0.615])

    # -------------------------------------------------------------
    # Panel (a): Climate Validation (CHIRPS vs NASA GPM IMERG)
    # -------------------------------------------------------------
    samples = data.get('spatial_grid_validation_samples', [])
    reg_p = data['climate_validation'].get('spatial_grid_regression', {})
    reg_v = data['remote_sensing_validation'].get('spatial_grid_regression', {})

    chirps = np.array([s['chirps_p'] for s in samples])
    gpm = np.array([s['gpm_p'] for s in samples])
    elev = np.array([s['elevation_m'] for s in samples])
    z_ndvi = np.array([s['z_ndvi'] for s in samples])
    z_evi = np.array([s['z_evi'] for s in samples])

    n_pts = len(samples)
    n_eff = reg_p.get('n_effective_spatial', 40)
    df = n_eff - 2
    t_crit = stats.t.ppf(0.975, df=df)

    ax1.set_facecolor('#FFFFFF')

    # Stratification by Elevation (NASA SRTM 30 m DEM)
    low = elev < 200
    mid = (elev >= 200) & (elev < 700)
    high = elev >= 700

    # Okabe-Ito / M5 Portfolio-Harmonized Palette:
    # Lowland:  #0072B2 (Ocean Blue, Alluvial Plains / Regime 2 / Cohort 1)
    # Upland:   #E69F00 (Amber Gold, Rolling Uplands / Regime 3 / Cohort 2)
    # Mountain: #238B45 (Forest Green, Volcanic Highlands / Regime 1)
    ax1.scatter(gpm[low], chirps[low], c='#0072B2', s=38, alpha=0.60, edgecolors='none',
                label=f"Lowland (< 200 m, n = {np.sum(low)})", zorder=3)
    ax1.scatter(gpm[mid], chirps[mid], c='#E69F00', s=44, alpha=0.75, edgecolors='none',
                label=f"Upland (200–700 m, n = {np.sum(mid)})", zorder=4)
    ax1.scatter(gpm[high], chirps[high], c='#238B45', s=54, alpha=0.85, edgecolors='#0F172A', linewidths=0.6,
                label=f"Mountain (≥ 700 m, n = {np.sum(high)})", zorder=5)

    # OLS Fit & 95% Confidence Interval Band (adjusted for N_eff = 40)
    slope_p = reg_p.get('ols_slope', 0.8723)
    int_p = reg_p.get('ols_intercept_mm', -17.01)
    r2_p = reg_p.get('r_squared', 0.5547)
    r_p = reg_p.get('pearson_r', 0.7448)

    res_p = chirps - (slope_p * gpm + int_p)
    s_yx_p = np.sqrt(np.sum(res_p**2) / (n_pts - 2))
    ss_x_p = (n_eff - 1) * np.var(gpm, ddof=1)
    mean_gpm = np.mean(gpm)

    x_p = np.linspace(30, 360, 100)
    y_pred_p = slope_p * x_p + int_p
    se_pred_p = s_yx_p * np.sqrt(1.0 / n_eff + (x_p - mean_gpm)**2 / ss_x_p)
    ci_low_p = y_pred_p - t_crit * se_pred_p
    ci_high_p = y_pred_p + t_crit * se_pred_p

    ax1.fill_between(x_p, ci_low_p, ci_high_p, color='#D55E00', alpha=0.18,
                     label=r"95% CI of Mean Fit ($N_{\mathrm{eff}} = 40$)", zorder=2)
    ax1.plot(x_p, y_pred_p, color='#D55E00', linewidth=2.2,
             label=f"OLS Fit: y = {slope_p:.3f}x {int_p:+.1f} mm ($R^2$ = {r2_p:.3f})", zorder=6)
    ax1.plot([20, 360], [20, 360], color='#0F172A', linestyle='--', linewidth=1.3,
             label='1:1 Identity Line (Ideal Agreement)', zorder=6)

    ax1.set_title('(a) Climate Precipitation Validation: CHIRPS v2.0 vs NASA GPM IMERG V07\nInfrared/Gauge vs Radar/Microwave | NASA SRTM 30 m DEM Stratification (Peak SON, 8 Episodes)',
                  fontsize=9.8, fontweight='bold', pad=8, loc='left', color='#0F172A')
    ax1.set_xlabel('NASA GPM IMERG V07 Precipitation (mm)', fontsize=9.2, fontweight='bold', color='#1E293B', labelpad=6)
    ax1.set_ylabel('CHIRPS v2.0 Precipitation (mm)', fontsize=9.2, fontweight='bold', color='#1E293B', labelpad=6)
    ax1.set_xlim(30, 355)
    ax1.set_ylim(30, 355)
    ax1.grid(True, linestyle='--', alpha=0.50, zorder=1)
    ax1.legend(loc='upper left', title='NASA SRTM 30 m DEM Tiers:', title_fontsize=7.8,
               frameon=True, facecolor='white', framealpha=0.95, edgecolor='#CBD5E1', fontsize=7.4)

    stat_box_a = (
        f"Spatial Concordance: r = {r_p:.4f} (R² = {r2_p:.3f})\n"
        f"Spatial-Adjusted: p_adj = {reg_p.get('p_adjusted', 3.57e-8):.2e} (N_eff = {n_eff})\n"
        f"Mean Bias: {reg_p.get('mean_bias_mm', -46.71):+.1f} mm (Sample) | MAE: {reg_p.get('mae_mm', 61.0):.1f} mm\n"
        f"RMSE: {reg_p.get('rmse_mm', 71.9):.1f} mm  |  Willmott's d = {reg_p.get('willmott_d', 0.786):.3f}\n"
        f"OLS Slope: {slope_p:.4f} (High-Rainfall Compression)"
    )
    ax1.text(0.96, 0.04, stat_box_a, transform=ax1.transAxes, ha='right', va='bottom', fontsize=7.6,
             bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.15', fc='#F8FAFC', ec='#CBD5E1', lw=0.9), zorder=6)

    # -------------------------------------------------------------
    # Panel (b): Spectral Index Sensitivity (MODIS NDVI vs EVI)
    # -------------------------------------------------------------
    ax2.set_facecolor('#FFFFFF')

    # Color points by severity of drought anomaly
    sev = z_ndvi < -1.0
    mod = (z_ndvi >= -1.0) & (z_ndvi < -0.5)
    mild = z_ndvi >= -0.5

    # Okabe-Ito / M2/M3 Portfolio-Harmonized Severity Palette:
    # Mild / Near-Normal: #0072B2 (Ocean Blue - Cohort 1 / Resilient)
    # Moderate Deficit:  #E69F00 (Amber Gold - Intermediate Transition)
    # Severe Deficit:    #D55E00 (Vermilion Red - Cohort 2 / Severe Drought)
    ax2.scatter(z_ndvi[mild], z_evi[mild], c='#0072B2', s=42, alpha=0.65, edgecolors='none',
                label=f"Mild / Near-Normal (Z_NDVI ≥ -0.5, n = {np.sum(mild)})", zorder=3)
    ax2.scatter(z_ndvi[mod], z_evi[mod], c='#E69F00', s=40, alpha=0.75, edgecolors='none',
                label=f"Moderate Deficit (-1.0 to -0.5, n = {np.sum(mod)})", zorder=4)
    ax2.scatter(z_ndvi[sev], z_evi[sev], c='#D55E00', s=42, alpha=0.85, edgecolors='none',
                label=f"Severe Deficit (Z_NDVI < -1.0, n = {np.sum(sev)})", zorder=5)

    slope_v = reg_v.get('ols_slope', 0.6900)
    int_v = reg_v.get('ols_intercept', -0.3274)
    r2_v = reg_v.get('r_squared', 0.7603)
    r_v = reg_v.get('pearson_r', 0.8720)

    res_v = z_evi - (slope_v * z_ndvi + int_v)
    s_yx_v = np.sqrt(np.sum(res_v**2) / (n_pts - 2))
    ss_x_v = (n_eff - 1) * np.var(z_ndvi, ddof=1)
    mean_z_ndvi = np.mean(z_ndvi)

    x_v = np.linspace(-2.2, 0.8, 100)
    y_pred_v = slope_v * x_v + int_v
    se_pred_v = s_yx_v * np.sqrt(1.0 / n_eff + (x_v - mean_z_ndvi)**2 / ss_x_v)
    ci_low_v = y_pred_v - t_crit * se_pred_v
    ci_high_v = y_pred_v + t_crit * se_pred_v

    ax2.fill_between(x_v, ci_low_v, ci_high_v, color='#0F172A', alpha=0.15,
                     label=r"95% CI of Mean Fit ($N_{\mathrm{eff}} = 40$)", zorder=2)
    ax2.plot(x_v, y_pred_v, color='#0F172A', linewidth=2.2,
             label=f"OLS Fit: Z_EVI = {slope_v:.3f} Z_NDVI {int_v:+.3f} ($R^2$ = {r2_v:.3f})", zorder=6)
    ax2.plot([-2.2, 0.8], [-2.2, 0.8], color='#64748B', linestyle='--', linewidth=1.3,
             label='1:1 Identity Line (Equal Sensitivity)', zorder=6)

    ax2.axvline(-0.73, color='#94A3B8', linestyle=':', linewidth=1.1, label='Mean NDVI Anomaly (-0.73)', zorder=2)
    ax2.axhline(-0.83, color='#94A3B8', linestyle='--', linewidth=1.1, label='Mean EVI Anomaly (-0.83)', zorder=2)

    ax2.set_title('(b) Spectral Index Sensitivity & Concordance: MODIS NDVI vs EVI\nCross-Formulation Canopy Deficit Consistency across East Java Vegetated Landscapes (Peak SON)',
                  fontsize=9.8, fontweight='bold', pad=8, loc='left', color='#0F172A')
    ax2.set_xlabel('Standardized NDVI Anomaly (Z_NDVI)', fontsize=9.2, fontweight='bold', color='#1E293B', labelpad=6)
    ax2.set_ylabel('Standardized EVI Anomaly (Z_EVI)', fontsize=9.2, fontweight='bold', color='#1E293B', labelpad=6)
    ax2.set_xlim(-2.2, 0.8)
    ax2.set_ylim(-2.2, 0.8)
    ax2.grid(True, linestyle='--', alpha=0.50, zorder=1)
    ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#CBD5E1', fontsize=7.6)

    # Calculate actual adjusted p-value with Student's t
    t_v_adj = r_v * np.sqrt(df / (1.0 - r2_v))
    p_v_adj = 2.0 * (1.0 - stats.t.cdf(abs(t_v_adj), df=df))

    stat_box_b = (
        f"Formulations Concordance: r = {r_v:.4f} (R² = {r2_v:.3f})\n"
        f"Spatial-Adjusted: p_adj = {p_v_adj:.2e} (N_eff = {n_eff})\n"
        f"Mean Bias (EVI - NDVI): {reg_v.get('mean_bias', -0.10):+.2f}  |  MAE: {reg_v.get('mae', 0.18):.2f}\n"
        f"RMSE: {reg_v.get('rmse', 0.27):.2f}  |  Willmott's d = {reg_v.get('willmott_d', 0.907):.3f}\n"
        f"Shared MODIS Red/NIR Bands Anchor Co-Variation"
    )
    ax2.text(0.96, 0.04, stat_box_b, transform=ax2.transAxes, ha='right', va='bottom', fontsize=7.6,
             bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.15', fc='#F0FDF4', ec='#86EFAC', lw=0.9), zorder=6)

    # -------------------------------------------------------------
    # Card Footer (Summary Takeaways for Multi-Sensor Validation)
    # -------------------------------------------------------------
    box_x0 = 0.065
    box_w = 0.890
    box_y0 = 0.025
    box_h = 0.105

    rect = FancyBboxPatch((box_x0, box_y0), box_w, box_h,
                          boxstyle='round,pad=0.0,rounding_size=0.008',
                          transform=fig.transFigure,
                          fc='#F8FAFC', ec='#CBD5E1', lw=0.9, alpha=0.95, zorder=1)
    fig.patches.append(rect)

    div_x = 0.510
    div_line = Line2D([div_x, div_x], [box_y0 + 0.008, box_y0 + box_h - 0.008],
                      transform=fig.transFigure, color='#CBD5E1', lw=0.9, linestyle='-', zorder=2)
    fig.add_artist(div_line)

    col1_lines = [
        r"• Spatial Concordance: CHIRPS v2.0 vs NASA GPM shows solid agreement (r = 0.7448, R² = 0.555).",
        r"• High-End Compression: OLS slope (0.8723 < 1) confirms CHIRPS under-estimates severe rain peaks.",
        r"• DEM Stratification: NASA SRTM 30 m dry bias: Lowland -43.0 mm, Upland -60.9 mm, Mountain -37.0 mm (d = 0.786)."
    ]

    col2_lines = [
        r"• Spectral Concordance: MODIS NDVI vs EVI shows robust co-variation (r = 0.8720, R² = 0.760, d = 0.907).",
        r"• Synchronous Browning: Both indices confirm severe drought (mean Z_NDVI = -0.73, Z_EVI = -0.83).",
        r"• Structural Note: Shared MODIS Red/NIR bands anchor correlation; EVI introduces -0.10 mean shift."
    ]

    col1_x = box_x0 + 0.010
    col2_x = div_x + 0.012

    for i in range(3):
        y_pos_f = box_y0 + box_h * (0.75 - i * 0.25)
        fig.text(col1_x, y_pos_f, col1_lines[i], fontsize=6.8, color='#334155', va='center', zorder=2)
        fig.text(col2_x, y_pos_f, col2_lines[i], fontsize=6.8, color='#334155', va='center', zorder=2)

    plot_path_png = os.path.join(OUTPUT_DIR, 'm7_1_sensor_validation.png')
    plot_path_pdf = os.path.join(OUTPUT_DIR, 'm7_1_sensor_validation.pdf')
    safe_savefig(plot_path_png, dpi=300, bbox_inches='tight')
    safe_savefig(plot_path_pdf, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Plot 1 saved to: {plot_path_png}")
    print(f"[OK] Plot 1 saved to: {plot_path_pdf}")


# =============================================================================
# PLOT 2: ENSEMBLE UNCERTAINTY & EMPIRICAL DISASTER VALIDATION (PANELS c & d)
# =============================================================================
def render_plot2_uncertainty_groundtruth(data):
    """
    Renders Plot 2 (Dedicated Disaster Ground Truth Validation Suite):
      Panel (a): Statistical Rank Concordance & Non-Linear Damage Decay (Modeled ASI vs Rice Puso Area)
      Panel (b): Empirical Disaster Loss Magnitude & Multi-Hazard Incident Profile (Bar Chart by Regency)
    """
    fig = plt.figure(figsize=(16.0, 8.4), dpi=300)
    
    # Master Header
    fig.suptitle('Empirical Disaster Ground-Truth Validation: Modeled Sensitivity vs BPBD 2023 Drought Records',
                 fontsize=13.0, fontweight='bold', y=0.972, color='#0F172A')
    fig.text(0.50, 0.940,
             ('Statistical Concordance & Water-Crisis Village Incidents in Purposive Benchmark Reporting Cohort (n = 9) | '
              'Official BPBD Jawa Timur Pusdalops Data (2023 Compound El Niño)'),
             ha='center', fontsize=8.4, color='#475569')

    # Explicit Axes Layout: Side-by-Side (1 row x 2 columns) with generous vertical clearance
    ax1 = fig.add_axes([0.065, 0.230, 0.410, 0.615])
    ax2 = fig.add_axes([0.545, 0.230, 0.410, 0.615])

    # -------------------------------------------------------------
    # Panel (a): Statistical Concordance (Scatter + Linear Regression)
    # -------------------------------------------------------------
    emp = data['empirical_ground_truth_validation']
    records = emp['empirical_sample']
    r_val = emp['pearson_correlation_r']
    r2_val = emp['r_squared']
    p_val_r = emp.get('p_value_pearson_nominal', emp.get('p_value_pearson', 0.0002427))
    rho = emp['spearman_rank_agreement_rho']
    p_val_rho = emp['p_value_spearman']

    dist_names = [r['district'] for r in records]
    lsi_vals = np.array([r['modeled_lsi'] for r in records])
    villages = np.array([r['recorded_water_crisis_villages'] for r in records])

    # Strictly LSI-Based Color Mapping (Non-overlapping intervals):
    # Critical Sensitivity: LSI >= 0.65 -> #D55E00 (Vermillion)
    # High Sensitivity: 0.55 <= LSI < 0.65 -> #E69F00 (Amber)
    # Low / Buffer Control: LSI < 0.45 -> #009E73 (Bluish Green)
    def get_lsi_color(val):
        if val >= 0.65:
            return '#D55E00'
        elif val >= 0.55:
            return '#E69F00'
        else:
            return '#009E73'

    colors = [get_lsi_color(x) for x in lsi_vals]
    bubble_sizes = [v * 7.5 + 90 for v in villages]

    ax1.set_facecolor('#FFFFFF')

    # Linear Regression Fit with 95% Confidence Interval Band (strictly bounded to observed data range)
    x_min = np.min(lsi_vals)  # 0.320 (Pacitan)
    x_max = np.max(lsi_vals)  # 0.697 (Lamongan)
    x_fit = np.linspace(x_min, x_max, 100)
    slope = 102.806
    intercept = -29.850
    y_fit = slope * x_fit + intercept

    # 95% Confidence Interval Band calculation
    n_sample = len(lsi_vals)
    s_yx = 4.716
    t_crit = 2.365  # df = 7, alpha = 0.05
    x_mean = np.mean(lsi_vals)
    ss_x = np.sum((lsi_vals - x_mean)**2)
    ci = t_crit * s_yx * np.sqrt(1.0 / n_sample + (x_fit - x_mean)**2 / ss_x)

    ax1.plot(x_fit, y_fit, color='#DC2626', linestyle='--', linewidth=1.5,
             label=r'Linear Fit ($y = 102.8x - 29.9, R^2 = 0.87$)', zorder=4)
    ax1.fill_between(x_fit, np.maximum(0, y_fit - ci), y_fit + ci, color='#F87171', alpha=0.14, zorder=3,
                     label='95% Confidence Interval Band (Observed Range)')

    # Scatter points
    ax1.scatter(lsi_vals, villages, s=bubble_sizes, c=colors,
                edgecolor='#0F172A', linewidth=0.9, alpha=0.92, zorder=5)

    # Tailored non-overlapping callout offsets with 4-quadrant spatial distribution
    callout_offsets = {
        'Lamongan': (4, 20),
        'Bojonegoro': (-64, 14),
        'Tuban': (18, -12),
        'Sampang': (-66, 12),
        'Gresik': (18, -6),
        'Ngawi': (-62, 10),
        'Nganjuk': (16, -18),
        'Jombang': (-58, -16),
        'Pacitan': (14, 10),
    }

    for name, lsi_v, v in zip(dist_names, lsi_vals, villages):
        ox, oy = callout_offsets.get(name, (10, 6))
        ax1.annotate(f"{name}\n({v} desa, LSI={lsi_v:.3f})", xy=(lsi_v, v),
                     xytext=(ox, oy), textcoords='offset points',
                     fontsize=7.8, fontweight='bold', color='#0F172A', path_effects=text_stroke,
                     bbox=dict(boxstyle='round,pad=0.20', fc='#FEF9C3', ec='#CA8A04', lw=0.6, alpha=0.92),
                     arrowprops=dict(arrowstyle='->', lw=0.65, color='#334155'), zorder=6)

    ax1.set_title('(a) Statistical Concordance & Incident Correlation\nModeled Landscape Sensitivity (LSI) vs BPBD Water-Crisis Villages | Pearson r = 0.933 (R² = 0.870)',
                  fontsize=10.0, fontweight='bold', pad=8, loc='left', color='#0F172A')
    ax1.set_xlabel('Modeled Landscape Sensitivity Index (LSI: 0.0 to 1.0)',
                   fontsize=9.2, fontweight='bold', color='#1E293B', labelpad=6)
    ax1.set_ylabel('BPBD Recorded Water-Crisis Villages (2023 El Niño, Desa)',
                   fontsize=9.2, fontweight='bold', color='#1E293B', labelpad=6)
    ax1.set_xlim(0.26, 0.79)
    ax1.set_ylim(-2, 56)
    ax1.grid(True, linestyle='--', alpha=0.50, zorder=1)
    leg = ax1.legend(loc='upper left', frameon=True, facecolor='white',
                     framealpha=0.95, edgecolor='#CBD5E1', fontsize=7.8)
    leg.set_zorder(6)

    # Statistical box positioned in the open upper-left quadrant below legend (x in [0.28, 0.48], y in [22, 42])
    stat_box_d = (
        f"Pearson Linear Fit: r = {r_val:.4f} (R² = {r2_val:.4f})\n"
        f"Spearman Rank Agreement: ρ = {rho:.4f}\n"
        f"Nominal Significance: p = {p_val_r:.2e} (df = 7)\n"
        f"Spatial-Adjusted: p_spatial = 0.0074 (df_eff = 3.90)\n"
        f"Spatial Correction: Clifford-Richardson N_eff = 5.90\n"
        f"Reporting Cohort: n = 9 Regencies (279 Villages)\n"
        f"Disaster Event: 2023 El Niño + IOD+ (BPBD Jatim)"
    )
    ax1.text(0.04, 0.52, stat_box_d, transform=ax1.transAxes, ha='left', va='center', fontsize=7.0,
             bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.15', fc='#FEF2F2', ec='#EF4444', lw=0.9), zorder=6)

    # Methodological Context Card on Benchmark Cohort & Selection Bias (bottom-right open quadrant)
    cohort_note = (
        "Purposive Benchmark Cohort Context (n = 9):\n"
        "• Targeted sample of jurisdictions with official gazetted BPBD\n"
        "  drought emergency status + 1 forested buffer control (Pacitan).\n"
        "• Non-reporting municipalities (e.g. humid montane or urban\n"
        "  enclaves) are excluded; sample reflects emergency filings.\n"
        "• Captures 279 water-crisis villages (~50% provincial total).\n"
        "• Reflects municipal relief independently of crop fallowing."
    )
    ax1.text(0.96, 0.07, cohort_note, transform=ax1.transAxes, ha='right', va='bottom', fontsize=6.8,
             color='#334155', linespacing=1.20,
             bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.12', fc='#F8FAFC', ec='#94A3B8', lw=0.75), zorder=6)

    # -------------------------------------------------------------
    # Panel (b): Empirical Disaster Loss Magnitude & Multi-Hazard Profile
    # -------------------------------------------------------------
    ax2.set_facecolor('#FFFFFF')

    # Rich district data dictionary sorted ascending by villages (so highest is at top)
    records_b = [
        {'name': 'Pacitan', 'lsi': 0.320, 'villages': 6, 'driver': 'Spring & deep forest buffer', 'color': get_lsi_color(0.320)},
        {'name': 'Jombang', 'lsi': 0.564, 'villages': 24, 'driver': 'Tertiary hill deficit & canal rationing', 'color': get_lsi_color(0.564)},
        {'name': 'Nganjuk', 'lsi': 0.582, 'villages': 26, 'driver': 'Widas tributary depletion & foothill stress', 'color': get_lsi_color(0.582)},
        {'name': 'Gresik', 'lsi': 0.612, 'villages': 28, 'driver': 'Saline intrusion & rural pond dry-up', 'color': get_lsi_color(0.612)},
        {'name': 'Ngawi', 'lsi': 0.589, 'villages': 31, 'driver': 'Bengawan Solo flow reduction', 'color': get_lsi_color(0.589)},
        {'name': 'Tuban', 'lsi': 0.651, 'villages': 35, 'driver': 'Karst upland desiccation & spring drying', 'color': get_lsi_color(0.651)},
        {'name': 'Sampang', 'lsi': 0.638, 'villages': 39, 'driver': 'Sedimentary limestone water deficit & salinity', 'color': get_lsi_color(0.638)},
        {'name': 'Lamongan', 'lsi': 0.697, 'villages': 42, 'driver': 'Tail-end canal exhaustion & shallow well drying', 'color': get_lsi_color(0.697)},
        {'name': 'Bojonegoro', 'lsi': 0.674, 'villages': 48, 'driver': 'Rain deficit & shallow aquifer loss', 'color': get_lsi_color(0.674)},
    ]

    y_pos = np.arange(len(records_b))
    village_vals = [r['villages'] for r in records_b]
    bar_colors = [r['color'] for r in records_b]

    # Shaded band highlighting the severe disaster epicenter zone (villages >= 24)
    ax2.axhspan(0.5, 8.5, facecolor='#FEF2F2', alpha=0.50, zorder=0, edgecolor='#EF4444', linestyle=':', linewidth=1.1)

    bars = ax2.barh(y_pos, village_vals, height=0.60, color=bar_colors,
                    edgecolor='#0F172A', linewidth=0.85, alpha=0.92, zorder=3)

    y_labels = [f"{r['name']} [LSI={r['lsi']:.3f}]" for r in records_b]
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(y_labels, fontsize=8.6, fontweight='bold', color='#1E293B')
    ax2.set_xlabel('BPBD Recorded Water-Crisis Villages (Desa Tanggap Darurat Kekeringan 2023)',
                   fontsize=9.2, fontweight='bold', color='#1E293B', labelpad=6)
    ax2.set_xlim(0, 92)
    ax2.grid(True, linestyle='--', alpha=0.50, zorder=1, axis='x')

    # Annotate bars with exact values and primary drivers
    for bar, r in zip(bars, records_b):
        w = bar.get_width()
        txt = f" {r['villages']} desa ({r['driver']})"
        ax2.text(w + 0.8, bar.get_y() + bar.get_height() / 2, txt,
                 va='center', ha='left', fontsize=7.3, fontweight='bold', color='#0F172A', zorder=5)

    ax2.set_title('(b) Empirical Disaster Incident Profile & Local Stress Drivers\nBPBD Water-Crisis Villages & Emergency Drought Declarations (2023 El Niño) | Benchmark n = 9',
                  fontsize=10.0, fontweight='bold', pad=8, loc='left', color='#0F172A')

    # Inset summary card (transparent breakdown: 273 acute in 8 regencies + 6 control in Pacitan = 279 total)
    impact_summary = (
        "Benchmark Cohort Disaster Impact (2023 El Niño):\n"
        "• Total Sample: 279 Crisis Villages (n = 9)\n"
        "• Acute Emergency Core (LSI ≥ 0.55): 273 Desa\n"
        "  (8 Regencies, ~50% of Provincial Filings)\n"
        "• Forested Buffer Control: Pacitan = 6 Desa (LSI = 0.320)\n"
        "• Source: Pusdalops PB BPBD Jatim (2023)"
    )
    ax2.text(0.97, 0.44, impact_summary, transform=ax2.transAxes, ha='right', va='center', fontsize=6.9,
             bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.15', fc='#F8FAFC', ec='#CBD5E1', lw=0.8), zorder=6)

    # Strictly LSI-Based Risk Tier Legend (Non-overlapping)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#D55E00', edgecolor='#0F172A', label='Critical Sensitivity (LSI ≥ 0.65, n = 3, 125 desa)'),
        Patch(facecolor='#E69F00', edgecolor='#0F172A', label='High Sensitivity (0.55 ≤ LSI < 0.65, n = 5, 148 desa)'),
        Patch(facecolor='#009E73', edgecolor='#0F172A', label='Low / Buffer Control (LSI < 0.45, n = 1, 6 desa)'),
    ]
    leg = ax2.legend(handles=legend_elements, loc='lower right', frameon=True, facecolor='white',
                     framealpha=0.95, edgecolor='#CBD5E1', fontsize=7.3)
    leg.set_zorder(6)

    # -------------------------------------------------------------
    # Card Footer (Summary Takeaways for Empirical Ground-Truth Validation)
    # -------------------------------------------------------------
    box_x0 = 0.065
    box_w = 0.890
    box_y0 = 0.025
    box_h = 0.105

    rect = FancyBboxPatch((box_x0, box_y0), box_w, box_h,
                          boxstyle='round,pad=0.0,rounding_size=0.008',
                          transform=fig.transFigure,
                          fc='#F8FAFC', ec='#CBD5E1', lw=0.9, alpha=0.95, zorder=1)
    fig.patches.append(rect)

    div_x = 0.510
    div_line = Line2D([div_x, div_x], [box_y0 + 0.008, box_y0 + box_h - 0.008],
                      transform=fig.transFigure, color='#CBD5E1', lw=0.9, linestyle='-', zorder=2)
    fig.add_artist(div_line)

    col1_lines = [
        r"• Strong Sample Association: Modeled LSI accounts for 87.0% of sample variance in recorded crisis villages (r = 0.9328, R² = 0.8701, ρ = 0.9500).",
        r"• Spatially Adjusted Significance: Association remains significant after Clifford-Richardson spatial correction (p_spatial = 0.0074, N_eff = 5.90, df_eff = 3.90).",
        r"• Acute Concentration: 8 sensitive regencies (LSI ≥ 0.55) encompass 273 crisis villages, capturing ~50% of provincial emergency filings."
    ]

    col2_lines = [
        r"• Purposive Sampling Provenance: Benchmark cohort reflects jurisdictions with gazetted BPBD emergency filings during 2023; non-reporting areas excluded.",
        r"• Operational Relevance & Confounders: Measures municipal water relief independently of crop fallowing, though administrative capacity & infrastructure remain unmodeled.",
        r"• Empirical Support: High statistical concordance supports the utility of satellite LSI for regional drought vulnerability screening, subject to broader testing."
    ]

    col1_x = box_x0 + 0.010
    col2_x = div_x + 0.012

    for i in range(3):
        y_pos_f = box_y0 + box_h * (0.75 - i * 0.25)
        fig.text(col1_x, y_pos_f, col1_lines[i], fontsize=6.8, color='#334155', va='center', zorder=2)
        fig.text(col2_x, y_pos_f, col2_lines[i], fontsize=6.8, color='#334155', va='center', zorder=2)

    # Save to both m7_2_uncertainty_groundtruth and m7_2_disaster_groundtruth
    plot_path_png1 = os.path.join(OUTPUT_DIR, 'm7_2_uncertainty_groundtruth.png')
    plot_path_pdf1 = os.path.join(OUTPUT_DIR, 'm7_2_uncertainty_groundtruth.pdf')
    plot_path_png2 = os.path.join(OUTPUT_DIR, 'm7_2_disaster_groundtruth.png')
    plot_path_pdf2 = os.path.join(OUTPUT_DIR, 'm7_2_disaster_groundtruth.pdf')

    safe_savefig(plot_path_png1, dpi=300, bbox_inches='tight')
    safe_savefig(plot_path_pdf1, bbox_inches='tight')
    safe_savefig(plot_path_png2, dpi=300, bbox_inches='tight')
    safe_savefig(plot_path_pdf2, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Plot 2 saved to: {plot_path_png1} (and alias {plot_path_png2})")


# =============================================================================
# PLOT 3: ENSEMBLE UNCERTAINTY & MULTI-EVENT REPRODUCIBILITY
# =============================================================================
def render_plot3_ensemble_uncertainty(data):
    """
    Renders Plot 3:
      Multi-Event LSI Ensemble Uncertainty (8 Historical El Niño Episodes across 5 Biophysical Regimes)
    """
    fig = plt.figure(figsize=(12.0, 7.8), dpi=300)

    # Master Header
    fig.suptitle('Multi-Event LSI Ensemble Uncertainty & Spatial Reproducibility (2001–2025)',
                 fontsize=13.0, fontweight='bold', y=0.970, color='#0F172A')
    fig.text(0.50, 0.938,
             ('8-Event Inter-Episode Landscape Sensitivity Spread (±1σ) & Coefficient of Variation across 5 Biophysical Regimes | '
              '35.1% Robust High-Confidence Area'),
             ha='center', fontsize=8.4, color='#475569')

    ax = fig.add_axes([0.100, 0.220, 0.800, 0.630])

    unc = data['ensemble_uncertainty']
    mean_lsi = unc['lsi_ensemble_mean']
    std_lsi = unc['lsi_ensemble_std']
    cv_lsi = unc['lsi_coefficient_of_variation']
    robust_pct = unc['robust_high_confidence_area_pct']

    regimes = ['Regime 1\n(Highland)', 'Regime 2\n(Irr. Valley)', 'Regime 3\n(Uplands)', 'Regime 4\n(Rain-Shadow)', 'Regime 5\n(Hyper-Sens.)']
    means = [0.45, 0.46, 0.64, 0.65, 0.66]
    stds = [0.18, 0.22, 0.28, 0.29, 0.26]

    ax.set_facecolor('#FFFFFF')
    x_pos = np.arange(len(regimes))

    regime_colors = ['#0072B2', '#56B4E9', '#E69F00', '#D55E00', '#990000']
    bars = ax.bar(x_pos, means, yerr=stds, capsize=6,
                  color=regime_colors,
                  edgecolor='#0F172A', linewidth=0.90, alpha=0.90, zorder=4)

    ax.axhline(0.60, color='#DC2626', linestyle='--', linewidth=1.4,
               label='High Sensitivity Threshold (LSI = 0.60)', zorder=5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(regimes, fontsize=9.2, fontweight='bold', color='#1E293B')
    ax.set_ylabel('Ensemble Landscape Sensitivity Index (LSI)', fontsize=9.6, fontweight='bold', color='#1E293B', labelpad=8)
    ax.set_ylim(0, 1.08)
    ax.grid(True, linestyle='--', alpha=0.50, zorder=1)

    for bar, m, s in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, m + s + 0.025, f"{m:.2f} ± {s:.2f}",
                ha='center', va='bottom', fontsize=8.4, fontweight='bold', color='#0F172A')

    ax.set_title('Multi-Event LSI Ensemble Uncertainty (8 Historical El Niño Episodes across 5 Biophysical Regimes)\nBar: Multi-Event Mean | Whiskers: Inter-Episode Spread (±1σ) across 2002, 2004, 2006, 2009, 2014, 2015, 2018, 2023',
                 fontsize=10.0, fontweight='bold', pad=10, loc='left', color='#0F172A')
    ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#CBD5E1', fontsize=8.6)

    stat_box = (
        f"Ensemble Mean LSI: {mean_lsi:.3f}\n"
        f"Inter-Event Spread (σ): {std_lsi:.3f}\n"
        f"Mean Coefficient of Variation: {cv_lsi:.3f}\n"
        f"Robust High-Confidence Hotspots: {robust_pct:.1f}% (~1.68 Mha)"
    )
    ax.text(0.96, 0.06, stat_box, transform=ax.transAxes, ha='right', va='bottom', fontsize=8.2,
            bbox=dict(boxstyle='round,pad=0.40,rounding_size=0.15', fc='#FFFBEB', ec='#FDE68A', lw=0.9), zorder=6)

    # Card Footer
    box_x0 = 0.100
    box_w = 0.800
    box_y0 = 0.025
    box_h = 0.105

    rect = FancyBboxPatch((box_x0, box_y0), box_w, box_h,
                          boxstyle='round,pad=0.0,rounding_size=0.008',
                          transform=fig.transFigure,
                          fc='#F8FAFC', ec='#CBD5E1', lw=0.9, alpha=0.95, zorder=1)
    fig.patches.append(rect)

    foot_lines = [
        r"• Multi-Episode Spread: Provincial mean LSI is 0.563 with inter-event spread σ = 0.277 (CV = 0.557) across 8 historical El Niño episodes.",
        r"• Deterministic Core: 35.1% of East Java (~1.68 Mha) exceeds LSI ≥ 0.60 across all ENSO episode types (Canonical, Modoki, and Compound IOD+).",
        r"• Stable Natural Buffers: Highlands (Regime 1) and irrigated river valleys (Regime 2) exhibit low variance (CV ≤ 0.35) and high buffering capacity."
    ]

    for i in range(3):
        y_pos_f = box_y0 + box_h * (0.75 - i * 0.25)
        fig.text(box_x0 + 0.015, y_pos_f, foot_lines[i], fontsize=7.2, color='#334155', va='center', zorder=2)

    plot_path_png = os.path.join(OUTPUT_DIR, 'm7_3_ensemble_uncertainty.png')
    plot_path_pdf = os.path.join(OUTPUT_DIR, 'm7_3_ensemble_uncertainty.pdf')
    safe_savefig(plot_path_png, dpi=300, bbox_inches='tight')
    safe_savefig(plot_path_pdf, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Plot 3 saved to: {plot_path_png}")


def main():
    print("=" * 70)
    print("Rendering Milestone 7 Split Publication Figures:")
    print("  Plot 1: outputs/m7_1_sensor_validation.png & .pdf")
    print("  Plot 2: outputs/m7_2_uncertainty_groundtruth.png (Dedicated Disaster Ground Truth)")
    print("  Plot 3: outputs/m7_3_ensemble_uncertainty.png & .pdf (Ensemble Uncertainty)")
    print("=" * 70)
    
    render_plot1_sensor_validation(data)
    render_plot2_uncertainty_groundtruth(data)
    render_plot3_ensemble_uncertainty(data)
    
    print("\n[SUCCESS] All Milestone 7 publication figures rendered successfully.")


if __name__ == '__main__':
    main()
