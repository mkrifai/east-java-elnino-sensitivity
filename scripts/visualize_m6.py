"""
Milestone 6 Visualization: Agricultural Sensitivity & Policy Translation Atlas
==============================================================================
Publication-grade composite visualization adhering to Milestone 5 standards:
  - Panel (a): Spatial Distribution of Agricultural Sensitivity Index (ASI)
  - Panel (b): Policy Decision-Support Matrix: Regency Level (n = 39 Units)
  - Panel (c): Policy Decision-Support Matrix: Subdistrict Level (n = 582 Units)
  - Panel (d): Regency Agricultural Vulnerability & Intra-Regency Disparity (Dumbbell Plot, n = 39)
  - Two-Column Explanatory Footer Box with LaTeX formulations and policy actions
  - Dual Output: 300 DPI PNG + Vector Publication PDF
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle, Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea

# --- Path Configuration ---
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
GEOTIFF_DIR = os.path.join(OUTPUT_DIR, 'geotiffs', 'm6')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm6_agriculture_policy_statistics.json')
CSV_KEC_PATH = os.path.join(OUTPUT_DIR, 'm6_hierarchical_asi_kecamatan.csv')
SHP_PATH = os.path.join(PROJECT_DIR, 'Batas Administrasi Kecamatan di Jawa Timur', 'administrasi_ar_kec_jatim.shp')

# Load quantitative statistical results
with open(JSON_PATH, 'r') as f:
    stats_data = json.load(f)

all_districts = stats_data['district_rankings']
total_districts = stats_data.get('total_districts', len(all_districts))

# Load subdistrict level dataset (n = 582)
df_kec = pd.read_csv(CSV_KEC_PATH)
total_kecamatan = len(df_kec)

# Global typography and styling system
plt.rcParams['font.sans-serif'] = ['Inter', 'Roboto', 'Arial', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'DejaVu Sans'
plt.rcParams['mathtext.it'] = 'DejaVu Sans:italic'
plt.rcParams['mathtext.bf'] = 'DejaVu Sans:bold'

# Text outline halos for cartographic legibility
map_stroke = [pe.withStroke(linewidth=2.8, foreground='white')]
text_stroke = [pe.withStroke(linewidth=2.4, foreground='white')]

# --- Load Geospatial Data ---
raster_path = os.path.join(GEOTIFF_DIR, 'M6_Agricultural_Sensitivity_Index.tif')
with rasterio.open(raster_path) as src:
    asi_raw = src.read(1)
    raster_bounds = src.bounds
    raster_trans = src.transform
    raster_crs = src.crs
    raster_extent = [raster_bounds.left, raster_bounds.right, raster_bounds.bottom, raster_bounds.top]

has_shp = os.path.exists(SHP_PATH)
if has_shp:
    import geopandas as gpd
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        gdf_raw = gpd.read_file(SHP_PATH)
        if gdf_raw.crs != raster_crs:
            gdf_raw = gdf_raw.to_crs(raster_crs)
        gdf_kab = gdf_raw.dissolve(by='NAMA_KABUP')
        gdf_prov = gdf_raw.dissolve()

        prov_geom = gdf_prov.geometry.iloc[0]
        prov_mask = ~geometry_mask([prov_geom], out_shape=asi_raw.shape, transform=raster_trans, invert=False)
        asi_display = np.where(prov_mask & ~np.isinf(asi_raw) & (asi_raw >= 0), asi_raw, np.nan)
else:
    asi_display = np.where(~np.isinf(asi_raw) & (asi_raw >= 0), asi_raw, np.nan)


# --- Custom Colormap for Agricultural Sensitivity ---
cmap_colors = [
    (0.00, '#F1F5F9'),  # Non-Crop / Buffered Landscape (Slate 100)
    (0.05, '#FEF0D9'),  # Minimal Agricultural Sensitivity
    (0.20, '#FDD49E'),  # Low-Moderate Sensitivity
    (0.35, '#FDBB84'),  # Moderate Sensitivity
    (0.50, '#FC8D59'),  # High Sensitivity
    (0.68, '#E34A33'),  # Severe Agricultural Vulnerability
    (0.85, '#B30000'),  # Critical Vulnerability
    (1.00, '#67000D'),  # Hyper-Sensitive Hotspot Epicenter
]
asi_cmap = LinearSegmentedColormap.from_list('ASI_Hazard_Ramp', [(pos, col) for pos, col in cmap_colors], N=256)


# =============================================================================
# MASTER FIGURE & EXPLICIT GEOMETRIC ARCHITECTURE (17.0 x 16.5 inches, 300 DPI)
# =============================================================================
fig = plt.figure(figsize=(17.0, 16.5), dpi=300)

# Explicit geometric layout parameters:
x0_left = 0.052
w_left = 0.435
x1_left = x0_left + w_left  # 0.487

# User Requirement 3: Ample horizontal gap so Panel (d) does not collide with left column
gap_h = 0.108  # 1.84 inches (generous breathing room for regency names, zero collision)
x0_right = x1_left + gap_h  # 0.595
x1_right = 0.975
w_right = x1_right - x0_right  # 0.380 (6.46 inches)

# User Requirement 2: Position panel (c) & (d) bottoms with matched gap to footer box
y_bottom = 0.134
h_c = 0.160
y0_c = y_bottom  # 0.134
y1_c = y0_c + h_c  # 0.294

# User Requirement 1: Ample gap between (b) and (c) for balanced 4-row WMO legend
gap_bc = 0.086  # 1.42 inches for 4-row WMO legend + generous breathing room
y0_b = y1_c + gap_bc  # 0.380
h_b = 0.160
y1_b = y0_b + h_b  # 0.540

# Compact vertical gap between (a) and (b)
gap_ab = 0.042  # 0.69 inches (tight!)
y0_a = y1_b + gap_ab  # 0.582
h_a = (w_left * 17.0) / (1.3158 * 16.5)  # 0.3406 (exact aspect match 5.25/3.99, zero auto-shrink)
y1_a = y0_a + h_a  # 0.9226 (leaves generous distance to main subtitle at 0.966)

ax_map = fig.add_axes([x0_left, y0_a, w_left, h_a])      # Panel (a): Spatial ASI Distribution
ax_mat_reg = fig.add_axes([x0_left, y0_b, w_left, h_b])  # Panel (b): Policy Matrix: Regency Level (n = 39)
ax_mat_kec = fig.add_axes([x0_left, y0_c, w_left, h_c])  # Panel (c): Policy Matrix: Subdistrict Level (n = 582)

h_disp = y1_a - y0_c  # 0.7926 (mathematically spans from bottom of c to top of a)
ax_disp = fig.add_axes([x0_right, y0_c, w_right, h_disp])     # Panel (d): Regency Disparity Dumbbell Chart (All 39 Regencies)


# =============================================================================
# PANEL (a): SPATIAL DISTRIBUTION OF AGRICULTURAL SENSITIVITY INDEX (ASI)
# =============================================================================
ax_map.set_facecolor('#F8FAFC')

# Base provincial background fill
if has_shp:
    gdf_prov.plot(ax=ax_map, facecolor='#F1F5F9', edgecolor='none', zorder=1)

# Render continuous ASI raster
im = ax_map.imshow(asi_display, extent=raster_extent, origin='upper',
                   cmap=asi_cmap, vmin=0.0, vmax=1.0, zorder=2, interpolation='nearest')

# Administrative vector boundaries
if has_shp:
    gdf_kab.boundary.plot(ax=ax_map, color='#475569', linewidth=0.5, alpha=0.65, zorder=3)
    gdf_prov.boundary.plot(ax=ax_map, color='#0F172A', linewidth=1.1, zorder=4)

# User Requirement 2: Expanded vertical limits for generous non-overlapping callout space
# Geographic bounds matching exact axes aspect ratio (5.25 deg lon / 3.99 deg lat = 1.316)
ax_map.set_xlim(110.80, 116.05)
ax_map.set_ylim(-9.14, -5.15)

# Cartographic Grid & Tick Labels with comfortable labelpad
ax_map.set_xticks([111, 112, 113, 114, 115])
ax_map.set_xticklabels(['111\u00b0E', '112\u00b0E', '113\u00b0E', '114\u00b0E', '115\u00b0E'],
                       fontsize=8.2, fontweight='bold', color='#1E293B')
ax_map.set_yticks([-8.5, -8.0, -7.5, -7.0, -6.5, -6.0, -5.5])
ax_map.set_yticklabels(['8.5\u00b0S', '8.0\u00b0S', '7.5\u00b0S', '7.0\u00b0S', '6.5\u00b0S', '6.0\u00b0S', '5.5\u00b0S'],
                       fontsize=8.2, fontweight='bold', color='#1E293B')
ax_map.set_xlabel('Longitude', fontsize=9.0, fontweight='bold', color='#1E293B', labelpad=7)
ax_map.set_ylabel('Latitude', fontsize=9.0, fontweight='bold', color='#1E293B', labelpad=4)
ax_map.grid(True, linestyle=':', alpha=0.55, color='#94A3B8', zorder=3)

# User Requirement 1: Color bar shifted higher up for balanced top & left margins
cbar_w = 0.280 * 0.90  # 0.252
cbar_h = 0.026 * 0.90  # 0.0234
cbar_ax = ax_map.inset_axes([0.040, 0.902, cbar_w, cbar_h], transform=ax_map.transAxes)
cb = plt.colorbar(im, cax=cbar_ax, orientation='horizontal')
cb.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
cb.set_ticklabels(['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=6.2, fontweight='bold', color='#1E293B')
cb.ax.tick_params(size=2.0, pad=2)
cbar_ax.set_title('Agricultural Sensitivity Index', fontsize=7.0, fontweight='bold', color='#0F172A', pad=2.5)
cbar_ax.set_zorder(7)

# User Requirement 1 & 2: Reorganized regional callouts - 0% overlapping, clear of left spine & coastline
rank_callouts = [
    # Top 3 ASI (Red / Crimson tones) -> Java Sea North
    (111.81, -7.20, 'Bojonegoro (#3, ASI: 0.34)', '#991B1B', (-35, 48)),
    (112.30, -7.13, 'Lamongan (#1, ASI: 0.48)', '#7F0000', (0, 56)),
    (112.60, -7.15, 'Gresik (#2, ASI: 0.36)', '#991B1B', (28, 44)),
    # Mid 3 ASI (Amber tones) -> Java Sea & Madura/Bali Strait
    (113.25, -7.05, 'Sampang (#19, ASI: 0.14)', '#B45309', (48, 48)),
    (114.05, -7.70, 'Situbondo (#20, ASI: 0.13)', '#B45309', (35, 14)),
    # Ponorogo & Bottom 3 ASI -> Indian Ocean South (swapped Batu & Malang, 0% overlap, clear of coastline)
    (111.18, -8.15, 'Pacitan (#39, ASI: 0.00)', '#047857', (-15, -60)),
    (111.45, -7.90, 'Ponorogo (#21, ASI: 0.13)', '#B45309', (55, -85)),
    (112.65, -8.15, 'Malang (#37, ASI: 0.04)', '#047857', (-5, -75)),
    (112.53, -7.87, 'Kota Batu (#38, ASI: 0.01)', '#047857', (95, -85)),
]

for lon, lat, label, c_txt, (dx, dy) in rank_callouts:
    ax_map.plot(lon, lat, marker='o', markersize=3.6, color='#0F172A',
                markeredgecolor='white', markeredgewidth=0.8, zorder=5)
    ax_map.annotate(label, xy=(lon, lat), xytext=(dx, dy), textcoords='offset points',
                    fontsize=6.8, fontweight='bold', color=c_txt, path_effects=map_stroke,
                    arrowprops=dict(arrowstyle='->', lw=0.7, color='#334155'), zorder=5)

# Scale Ratio Box in lower-right corner (Indian Ocean off Bali Strait)
scale_box = AnchoredOffsetbox(
    loc='lower right',
    child=TextArea('Scale  1 : 2,500,000',
                   textprops=dict(fontsize=7.6, fontweight='bold', color='#0F172A')),
    pad=0.35, frameon=True,
    bbox_to_anchor=(0.970, 0.050),
    bbox_transform=ax_map.transAxes, borderpad=0.0
)
scale_box.patch.set_boxstyle('round,pad=0.32,rounding_size=0.15')
scale_box.patch.set_facecolor('white')
scale_box.patch.set_edgecolor('#94A3B8')
scale_box.patch.set_linewidth(0.85)
scale_box.patch.set_alpha(0.96)
scale_box.set_zorder(6)
ax_map.add_artist(scale_box)

# Vector Cartographic Compass Rose in upper-right corner
cx, cy = 115.35, -5.65
ax_map.add_patch(Circle((cx, cy), 0.22, facecolor='white', edgecolor='#CBD5E1', lw=0.6, alpha=0.92, zorder=5))
ax_map.add_patch(Circle((cx, cy), 0.12, facecolor='none', edgecolor='#475569', lw=0.6, linestyle=':', zorder=6))
ax_map.add_patch(Polygon([(cx, cy), (cx, cy + 0.25), (cx - 0.045, cy)], facecolor='#0F172A', edgecolor='#0F172A', lw=0.4, zorder=6))
ax_map.add_patch(Polygon([(cx, cy), (cx, cy + 0.25), (cx + 0.045, cy)], facecolor='white', edgecolor='#0F172A', lw=0.4, zorder=6))
ax_map.add_patch(Polygon([(cx, cy), (cx, cy - 0.16), (cx - 0.035, cy)], facecolor='white', edgecolor='#0F172A', lw=0.4, zorder=6))
ax_map.add_patch(Polygon([(cx, cy), (cx, cy - 0.16), (cx + 0.035, cy)], facecolor='#0F172A', edgecolor='#0F172A', lw=0.4, zorder=6))
ax_map.add_patch(Polygon([(cx, cy), (cx + 0.16, cy), (cx, cy + 0.035)], facecolor='#0F172A', edgecolor='#0F172A', lw=0.4, zorder=6))
ax_map.add_patch(Polygon([(cx, cy), (cx + 0.16, cy), (cx, cy - 0.035)], facecolor='white', edgecolor='#0F172A', lw=0.4, zorder=6))
ax_map.add_patch(Polygon([(cx, cy), (cx - 0.16, cy), (cx, cy + 0.035)], facecolor='white', edgecolor='#0F172A', lw=0.4, zorder=6))
ax_map.add_patch(Polygon([(cx, cy), (cx - 0.16, cy), (cx, cy - 0.035)], facecolor='#0F172A', edgecolor='#0F172A', lw=0.4, zorder=6))
ax_map.add_patch(Circle((cx, cy), 0.018, facecolor='#0F172A', edgecolor='white', lw=0.4, zorder=7))
ax_map.text(cx, cy + 0.32, 'N', ha='center', va='center', fontsize=9.0, fontweight='bold', color='#0F172A',
            path_effects=map_stroke, zorder=7)

ax_map.set_title('(a) Spatial Distribution of Agricultural Sensitivity Index (ASI = LSI \u00d7 Cropland Fraction)',
                 fontsize=10.0, fontweight='bold', pad=8, loc='left')


# =============================================================================
# HELPER: DRAW ROUNDED CORNER BADGES & 4-ROW WMO-STYLE EXTERNAL LEGEND
# =============================================================================
def draw_zone_corner_badges(ax):
    """User Requirement 3: Corner zone labels inside rounded badge boxes (scale box style)."""
    badges = [
        (0.965, 0.938, 'Zone 1', '#DC2626', '#FFFFFF', '#DC2626', 'right', 'top'),
        (0.965, 0.062, 'Zone 2', '#2563EB', '#FFFFFF', '#2563EB', 'right', 'bottom'),
        (0.035, 0.938, 'Zone 3', '#D97706', '#FFFFFF', '#D97706', 'left', 'top'),
        (0.035, 0.062, 'Zone 4', '#16A34A', '#FFFFFF', '#16A34A', 'left', 'bottom'),
    ]
    for x, y, label, c_txt, fc, ec, ha, va in badges:
        bbox_props = dict(boxstyle='round,pad=0.32,rounding_size=0.20',
                          facecolor=fc, edgecolor=ec, linewidth=0.90, alpha=0.96)
        ax.text(x, y, label, transform=ax.transAxes,
                ha=ha, va=va, fontsize=7.6, fontweight='bold', color=c_txt,
                bbox=bbox_props, zorder=6)

def draw_wmo_zone_legend(ax, n_counts, y_top=-0.2205):
    """
    User Requirement 1: 4-Row External Zone Legend with strictly equal visual spacing:
      - Clean vertical margin between x-axis label and color strip
      - Row 1: Elongated color strip bar (equal width, full span)
      - Visual gap(color strip -> Zone text) == gap(Zone text -> Type) == gap(Type -> n value)
    """
    zones_data = [
        ('Zone 1', 'Critical Emergency', n_counts[0], '#EF4444'),
        ('Zone 2', 'Hydrologic Conveyance', n_counts[1], '#3B82F6'),
        ('Zone 3', 'Rain-Shadow & Fodder', n_counts[2], '#F59E0B'),
        ('Zone 4', 'Ecological Catchment', n_counts[3], '#10B981'),
    ]
    
    n_zones = len(zones_data)
    gap = 0.016
    total_gaps = (n_zones - 1) * gap
    block_w = (1.000 - total_gaps) / n_zones
    strip_h = 0.022
    
    # Mathematically equal vertical gaps between every element (g_row = 0.0200 transAxes units)
    g_row = 0.0200
    h_z = 0.0366
    h_t = 0.0328
    h_n = 0.0328
    
    yc_z = y_top - g_row - h_z / 2.0                 # -0.2588
    yc_t = y_top - 2 * g_row - h_z - h_t / 2.0        # -0.3135
    yc_n = y_top - 3 * g_row - h_z - h_t - h_n / 2.0  # -0.3663
    
    for i, (z_name, z_type, z_count, z_col) in enumerate(zones_data):
        bx0 = i * (block_w + gap)
        xc = bx0 + block_w / 2.0
        
        # Row 1: Elongated Color Bar Strip of equal length, fulfilling full width of box plot
        rect = Rectangle((bx0, y_top), block_w, strip_h,
                         facecolor=z_col, edgecolor='none',
                         transform=ax.transAxes, clip_on=False, zorder=4)
        ax.add_patch(rect)
        
        # Row 2: Zone Name (gap = g_row from color bar)
        ax.text(xc, yc_z, z_name, transform=ax.transAxes,
                ha='center', va='center', fontsize=7.4, fontweight='bold',
                color='#0F172A', clip_on=False, zorder=4)
        
        # Row 3: Zone Type Description (gap = g_row from Zone name)
        ax.text(xc, yc_t, z_type, transform=ax.transAxes,
                ha='center', va='center', fontsize=6.6,
                color='#475569', clip_on=False, zorder=4)
        
        # Row 4: Unit Count (gap = g_row from Zone type)
        ax.text(xc, yc_n, f"n = {z_count}", transform=ax.transAxes,
                ha='center', va='center', fontsize=6.6, fontweight='bold',
                color='#1E293B', clip_on=False, zorder=4)


# =============================================================================
# PANEL (b): POLICY DECISION-SUPPORT MATRIX: REGENCY LEVEL (n = 39)
# =============================================================================
ax_mat_reg.set_facecolor('#FFFFFF')

# Background Quadrant Policy Intervention Zones Shading
ax_mat_reg.fill_between([0.60, 0.90], 30.0, 82.0, color='#FEF2F2', alpha=0.75, zorder=0)
ax_mat_reg.fill_between([0.60, 0.90], -4.0, 30.0, color='#EFF6FF', alpha=0.75, zorder=0)
ax_mat_reg.fill_between([0.30, 0.60], 30.0, 82.0, color='#FFFBEB', alpha=0.75, zorder=0)
ax_mat_reg.fill_between([0.30, 0.60], -4.0, 30.0, color='#F0FDF4', alpha=0.75, zorder=0)

# Quadrant Threshold Divider Lines
ax_mat_reg.axvline(0.60, color='#DC2626', linestyle='--', linewidth=1.1, zorder=2)
ax_mat_reg.axhline(30.0, color='#2563EB', linestyle='--', linewidth=1.1, zorder=2)

# User Requirement 3: Corner zone labels inside rounded badge boxes
draw_zone_corner_badges(ax_mat_reg)

# Extract district scatter coordinates
lsi_vals = np.array([d['mean_lsi'] for d in all_districts])
crop_vals = np.array([d['crop_fraction'] * 100 for d in all_districts])
asi_vals = np.array([d['mean_asi'] for d in all_districts])

# Scatter plot: bubble size & color mapped to ASI (calibrated 0.0 to 1.0)
bubble_sizes = 50 + asi_vals * 650
ax_mat_reg.scatter(lsi_vals, crop_vals, s=bubble_sizes, c=asi_vals, cmap=asi_cmap,
                   vmin=0.0, vmax=1.0, edgecolor='#0F172A', linewidth=0.85, alpha=0.92, zorder=5)

# User Requirement 2 & 5: Priority District Badges strictly inside box plot area (0% overlap, 0% spillover)
matrix_offsets = {
    'Lamongan': (-15, 14),   # points UP into empty quadrant space at Crop 75%
    'Gresik': (-75, 16),     # points UP-LEFT into LSI 0.50-0.58, Crop 51%
    'Kediri': (-75, -2),     # points LEFT into LSI 0.50-0.58, Crop 43% (clear of Magetan!)
    'Magetan': (-75, -20),   # points DOWN-LEFT into LSI 0.50-0.58, Crop 35% (clear of Kediri!)
    'Tuban': (-45, 18),      # points UP-LEFT into LSI 0.59-0.67, Crop 51% (clear of Gresik & Bojonegoro!)
    'Jombang': (12, 16),     # points UP-RIGHT into LSI 0.71, Crop 54%
    'Bojonegoro': (14, 14),  # points UP-RIGHT into LSI 0.78-0.86, Crop 49% (clear of Tuban!)
    'Nganjuk': (14, -6),     # points DOWN-RIGHT into LSI 0.66-0.74, Crop 41%
    'Mojokerto': (14, -18),  # points DOWN-RIGHT into LSI 0.63-0.71, Crop 35%
    'Ngawi': (14, -10),      # points RIGHT into LSI 0.78-0.86, Crop 34%
}

for d in all_districts[:10]:
    d_name = d['district_name']
    ox, oy = matrix_offsets.get(d_name, (10, 6))
    rank_str = f"#{d['priority_rank']} {d_name} ({d['mean_asi']:.2f})"
    ax_mat_reg.annotate(rank_str, xy=(d['mean_lsi'], d['crop_fraction'] * 100),
                        xytext=(ox, oy), textcoords='offset points',
                        fontsize=6.5, fontweight='bold', color='#0F172A', path_effects=text_stroke,
                        bbox=dict(boxstyle='round,pad=0.18', fc='#FEF9C3', ec='#CA8A04', lw=0.6, alpha=0.92),
                        arrowprops=dict(arrowstyle='->', lw=0.65, color='#334155'), zorder=6)

ax_mat_reg.set_xlim(0.30, 0.90)
ax_mat_reg.set_ylim(-4.0, 82.0)
ax_mat_reg.set_xticks([0.35, 0.40, 0.50, 0.60, 0.70, 0.80])
ax_mat_reg.set_xticklabels(['0.35', '0.40', '0.50', '0.60', '0.70', '0.80'], fontsize=7.8)
ax_mat_reg.set_yticks([0, 15, 30, 45, 60, 75])
ax_mat_reg.set_yticklabels(['0%', '15%', '30%', '45%', '60%', '75%'], fontsize=7.8)
ax_mat_reg.set_xlabel('Mean Landscape Sensitivity Index (LSI)', fontsize=8.6, fontweight='bold', color='#0F172A', labelpad=6)
ax_mat_reg.set_ylabel('Cropland Density (%)', fontsize=8.6, fontweight='bold', color='#0F172A', labelpad=5)
ax_mat_reg.grid(True, linestyle='--', alpha=0.45, zorder=1)

# User Requirement 1: 4-Row External WMO-Style Zone Legend with strictly equal visual spacing
draw_wmo_zone_legend(ax_mat_reg, n_counts=[10, 8, 4, 17], y_top=-0.2205)

ax_mat_reg.set_title('(b) Policy Decision-Support Matrix: Regency Level (n = 39 Administrative Units)',
                     fontsize=9.8, fontweight='bold', pad=7, loc='left')


# =============================================================================
# PANEL (c): POLICY DECISION-SUPPORT MATRIX: SUBDISTRICT LEVEL (n = 582)
# =============================================================================
ax_mat_kec.set_facecolor('#FFFFFF')

# Background Quadrant Shading for Subdistricts (using full range from -0.02 to 1.04)
ax_mat_kec.fill_between([0.60, 1.04], 30.0, 110.0, color='#FEF2F2', alpha=0.75, zorder=0)
ax_mat_kec.fill_between([0.60, 1.04], -4.0, 30.0, color='#EFF6FF', alpha=0.75, zorder=0)
ax_mat_kec.fill_between([-0.02, 0.60], 30.0, 110.0, color='#FFFBEB', alpha=0.75, zorder=0)
ax_mat_kec.fill_between([-0.02, 0.60], -4.0, 30.0, color='#F0FDF4', alpha=0.75, zorder=0)

# Quadrant Threshold Divider Lines
ax_mat_kec.axvline(0.60, color='#DC2626', linestyle='--', linewidth=1.1, zorder=2)
ax_mat_kec.axhline(30.0, color='#2563EB', linestyle='--', linewidth=1.1, zorder=2)

# User Requirement 3: Corner zone labels inside rounded badge boxes
draw_zone_corner_badges(ax_mat_kec)

# Scatter plot: 582 kecamatan points
lsi_kec = df_kec['mean_lsi'].values
crop_kec = df_kec['crop_density_pct'].values
asi_kec = df_kec['mean_asi'].values

bubble_sizes_kec = 18 + asi_kec * 230
ax_mat_kec.scatter(lsi_kec, crop_kec, s=bubble_sizes_kec, c=asi_kec, cmap=asi_cmap,
                   vmin=0.0, vmax=1.0, edgecolor='#0F172A', linewidth=0.35, alpha=0.76, zorder=5)

# User Requirement 5: Micro-hotspot callouts strictly inside box plot area (0% overlap, 0% spillover)
top_kec_callouts = [
    ('Balongpanggang', 'Gresik', 0.7517, 98.63, 0.7414, (-85, 10)),
    ('Tikung', 'Lamongan', 0.7448, 96.55, 0.7302, (12, -18)),
    ('Damarblandong', 'Mojokerto', 0.8606, 82.05, 0.7075, (-96, -16)),
    ('Tenggarang', 'Bondowoso', 0.9787, 69.57, 0.6743, (-90, -16)),
]

for kec_n, kab_n, lsi_k, crop_k, asi_k, (ox, oy) in top_kec_callouts:
    label_k = f"{kec_n} ({kab_n}, {asi_k:.2f})"
    ax_mat_kec.annotate(label_k, xy=(lsi_k, crop_k), xytext=(ox, oy), textcoords='offset points',
                        fontsize=6.3, fontweight='bold', color='#0F172A', path_effects=text_stroke,
                        bbox=dict(boxstyle='round,pad=0.16', fc='#FEF9C3', ec='#CA8A04', lw=0.55, alpha=0.92),
                        arrowprops=dict(arrowstyle='->', lw=0.60, color='#334155'), zorder=6)

ax_mat_kec.set_xlim(-0.02, 1.04)
ax_mat_kec.set_ylim(-4.0, 110.0)
ax_mat_kec.set_xticks([0.00, 0.20, 0.40, 0.60, 0.80, 1.00])
ax_mat_kec.set_xticklabels(['0.00', '0.20', '0.40', '0.60', '0.80', '1.00'], fontsize=7.8)
ax_mat_kec.set_yticks([0, 25, 50, 75, 100])
ax_mat_kec.set_yticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize=7.8)
ax_mat_kec.set_xlabel('Mean Landscape Sensitivity Index (LSI)', fontsize=8.6, fontweight='bold', color='#0F172A', labelpad=6)
ax_mat_kec.set_ylabel('Cropland Density (%)', fontsize=8.6, fontweight='bold', color='#0F172A', labelpad=5)
ax_mat_kec.grid(True, linestyle='--', alpha=0.45, zorder=1)

# User Requirement 1: 4-Row External WMO-Style Zone Legend with strictly equal visual spacing
draw_wmo_zone_legend(ax_mat_kec, n_counts=[166, 94, 116, 206], y_top=-0.2205)

ax_mat_kec.set_title('(c) Policy Decision-Support Matrix: Subdistrict Level (n = 582 Kecamatan Units)',
                     fontsize=9.8, fontweight='bold', pad=7, loc='left')


# =============================================================================
# PANEL (d): ALL 39 ADMINISTRATIVE UNITS - INTRA-REGENCY DISPARITY DUMBBELL CHART
# =============================================================================
ax_disp.set_facecolor('#FFFFFF')

n_total_reg = len(all_districts)  # 39 districts

# Extract subdistrict distribution for ALL 39 regencies
reg_data = []
for d in all_districts:
    d_name = d['district_name']
    sub = df_kec[df_kec['kabupaten'].str.lower() == d_name.lower()]
    if len(sub) == 0:
        sub = df_kec[df_kec['kabupaten'].str.lower().str.contains(d_name.lower())]
    min_asi = float(sub['mean_asi'].min()) if len(sub) > 0 else 0.0
    max_asi = float(sub['mean_asi'].max()) if len(sub) > 0 else 0.0
    delta = max_asi - min_asi
    n_count = len(sub)
    reg_data.append({
        'district_name': d_name,
        'priority_rank': d['priority_rank'],
        'regency_mean': d['mean_asi'],
        'min_kec': min_asi,
        'max_kec': max_asi,
        'delta': delta,
        'count': n_count
    })

# Ordering: Rank 1 (Lamongan) at the TOP (y = 38) down to Rank 39 (Pacitan) at the BOTTOM (y = 0)
rank_indices = np.arange(n_total_reg)[::-1]
names_ranked = [f"{r['district_name']} (#{r['priority_rank']})" for r in reg_data]

# Background Tier Matrix Division (Shaded Horizontal Bands across all 39)
# Tier 1: ASI >= 0.28 (Ranks 1 to 9, indices 30 to 38)
ax_disp.axhspan(29.5, 38.8, facecolor='#FEF2F2', alpha=0.55, zorder=0)
ax_disp.axhline(29.5, color='#FCA5A5', linestyle='--', lw=0.9, zorder=1)
ax_disp.text(0.865, 34.0, 'TIER 1: CRITICAL EXPOSURE\n(ASI \u2265 0.28, n = 9)',
             ha='right', va='center', fontsize=6.8, fontweight='bold', color='#991B1B', alpha=0.85, zorder=1)

# Tier 2: 0.22 <= ASI < 0.28 (Ranks 10 to 13, indices 26 to 29)
ax_disp.axhspan(25.5, 29.5, facecolor='#FFFBEB', alpha=0.55, zorder=0)
ax_disp.axhline(25.5, color='#FDE68A', linestyle='--', lw=0.9, zorder=1)
ax_disp.text(0.865, 27.5, 'TIER 2: HIGH PRIORITY\n(0.22 \u2264 ASI < 0.28, n = 4)',
             ha='right', va='center', fontsize=6.8, fontweight='bold', color='#B45309', alpha=0.85, zorder=1)

# Tier 3: 0.13 <= ASI < 0.22 (Ranks 14 to 20, indices 19 to 25)
ax_disp.axhspan(18.5, 25.5, facecolor='#EFF6FF', alpha=0.55, zorder=0)
ax_disp.axhline(18.5, color='#93C5FD', linestyle='--', lw=0.9, zorder=1)
ax_disp.text(0.865, 22.0, 'TIER 3: MODERATE RISK\n(0.13 \u2264 ASI < 0.22, n = 7)',
             ha='right', va='center', fontsize=6.8, fontweight='bold', color='#1E40AF', alpha=0.85, zorder=1)

# Tier 4: ASI < 0.13 (Ranks 21 to 39, indices 0 to 18)
ax_disp.axhspan(-0.75, 18.5, facecolor='#F8FAFC', alpha=0.55, zorder=0)
ax_disp.text(0.865, 9.2, 'TIER 4: LOW / BUFFERED\n(ASI < 0.13, n = 19)',
             ha='right', va='center', fontsize=6.8, fontweight='bold', color='#475569', alpha=0.85, zorder=1)

# Provincial Mean reference line
prov_mean_asi = 0.201
ax_disp.axvline(prov_mean_asi, color='#334155', linestyle='--', linewidth=1.1, zorder=3)
ax_disp.text(prov_mean_asi, 38.3,
             f'Prov. Mean\n{prov_mean_asi:.3f}',
             ha='center', va='center', fontsize=6.2, fontweight='bold',
             color='#1E293B', path_effects=text_stroke, zorder=7)

# Draw Horizontal Dumbbell Rows
for y_idx, r in zip(rank_indices, reg_data):
    # 1. Connecting horizontal bar
    ax_disp.plot([r['min_kec'], r['max_kec']], [y_idx, y_idx], color='#94A3B8', lw=1.8, zorder=3)
    
    # 2. Min
    ax_disp.scatter(r['min_kec'], y_idx, color='#10B981', s=40, edgecolor='#065F46', lw=0.9,
                    zorder=5, label='Min' if y_idx == rank_indices[0] else "")
    
    # 3. Mean
    ax_disp.scatter(r['regency_mean'], y_idx, color='#F59E0B', s=46, marker='D', edgecolor='#B45309', lw=0.9,
                    zorder=6, label='Mean' if y_idx == rank_indices[0] else "")
    
    # 4. Max
    ax_disp.scatter(r['max_kec'], y_idx, color='#EF4444', s=40, edgecolor='#991B1B', lw=0.9,
                    zorder=5, label='Max' if y_idx == rank_indices[0] else "")
    
    # 5. Right text label: Disparity Gap and Subdistrict Count
    label_txt = f"\u0394 = {r['delta']:.3f} (n={r['count']})"
    ax_disp.text(r['max_kec'] + 0.014, y_idx, label_txt,
                 va='center', ha='left', fontsize=5.8, color='#1E293B', fontweight='bold',
                 path_effects=text_stroke, zorder=7)

# Vertical axis ticks (District Names with rank)
ax_disp.set_yticks(rank_indices)
ax_disp.set_yticklabels(names_ranked, fontsize=6.4, fontweight='bold', color='#0F172A')
ax_disp.tick_params(axis='y', pad=6)

ax_disp.set_xlim(-0.02, 0.88)
ax_disp.set_xticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
ax_disp.set_xticklabels(['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8'], fontsize=7.6)
ax_disp.set_ylim(-0.75, 38.75)

# User Requirement 7: Removed "Min, Mean, Max" from horizontal label
ax_disp.set_xlabel('Agricultural Sensitivity Index Range',
                   fontsize=8.8, fontweight='bold', color='#0F172A', labelpad=7)
ax_disp.grid(True, axis='x', linestyle='--', alpha=0.50, zorder=1)

# User Requirement 6: Single-row horizontal legend at lower-right, roughly level with Pacitan (y ~ 0)
leg = ax_disp.legend(loc='lower right', bbox_to_anchor=(0.970, 0.012), ncol=3, fontsize=7.2,
                     framealpha=0.96, facecolor='white', edgecolor='#CBD5E1', columnspacing=1.1)
leg.get_frame().set_boxstyle('round,pad=0.32,rounding_size=0.15')
leg.set_zorder(8)

ax_disp.set_title('(d) Regency Agricultural Vulnerability & Intra-Regency Disparity (n = 39 Administrative Units)',
                  fontsize=10.0, fontweight='bold', pad=8, loc='left')


# =============================================================================
# MASTER FIGURE HEADERS
# =============================================================================
# User Requirement 4: Generous vertical distance between main subtitle and top panels
fig.suptitle('East Java Agricultural Drought Sensitivity & Policy Translation Atlas',
             fontsize=13.5, fontweight='bold', y=0.985)

fig.text(0.50, 0.966,
         (f'Peak Dry Season (SON) Exposure Across Historical El Ni\u00f1o Episodes (2001\u20132025)  |  '
          f'Compound Metric: ASI = LSI \u00d7 Cropland Fraction  |  '
          f'Total Landscape: 44,528 km\u00b2  |  Evaluated Units: n = {total_districts} Regencies, n = {total_kecamatan} Subdistricts'),
         ha='center', fontsize=8.4, color='#475569')


# =============================================================================
# SAFE EXPORT PIPELINE & GEOMETRIC ALIGNMENT
# =============================================================================
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

# User Requirement 2: Footer distance to panel (c) exactly equals distance from LSI label to color bar
# LSI label bottom: -0.1505, color bar top: -0.1985 -> gap_lsi_cbar = 0.0480 * h_c = 0.00768 fig units
# Panel (c) lowest text (n bottom): y0_c + (-0.3827) * h_c = 0.07277 fig units
# footer_top = n_bot_fig - gap_lsi_cbar_fig = 0.06509 fig units
gap_lsi_cbar_fig = 0.0480 * h_c
n_bot_fig = y0_c + (-0.3827) * h_c
footer_top_fig = n_bot_fig - gap_lsi_cbar_fig

box_x0 = x0_left
box_w = x1_right - x0_left
box_h = 0.046
box_y0 = footer_top_fig - box_h  # 0.0191 fig units (exact match to gap_lsi_cbar_fig!)

rect = FancyBboxPatch((box_x0, box_y0), box_w, box_h,
                      boxstyle='round,pad=0.0,rounding_size=0.008',
                      transform=fig.transFigure,
                      fc='#F8FAFC', ec='#CBD5E1', lw=0.9, alpha=0.95, zorder=1)
fig.patches.append(rect)

# Divider line sits in the exact middle between the two columns
div_x = x1_left + (x0_right - x1_left) / 2.0
div_line = Line2D([div_x, div_x], [box_y0 + 0.005, box_y0 + box_h - 0.005],
                  transform=fig.transFigure, color='#CBD5E1', lw=0.9, linestyle='-', zorder=2)
fig.add_artist(div_line)

col1_lines = [
    r"• Metric Formulation: $\mathrm{ASI} = \mathrm{LSI} \times f_{\mathrm{crop}}$, weighting physical drought sensitivity by 10 m ESA WorldCover cropland density.",
    r"• Multi-Scale Decision Matrix: Cross-scale evaluation across 39 Regencies (Panel b) and 582 Subdistricts (Panel c) delineating 4 operational intervention zones.",
    r"• Risk Concentration: Top 10 districts account for 68.4% of provincial critical agricultural hotspots (Epicenter: Kab. Lamongan, ASI = 0.479, n = 25 kecamatan)."
]

col2_lines = [
    r"• Complete 39-Regency Disparity ($\Delta$): Micro-disparities reach $\Delta = 0.741$ in Gresik & Lamongan, demanding targeted intra-regency resource mobilization.",
    r"• Tier 1 Emergency Action: Coordinated reservoir release (Waduk Pacal & Gondang) and subsidized AUTP crop insurance for Zone 1 high-exposure subdistricts.",
    r"• Basin Quotas & Diversification: Trans-boundary canal scheduling across Bengawan Solo & Brantas basins; Zone 2–3 transition to palawija and embung."
]

col1_x = box_x0 + 0.010
col2_x = div_x + 0.012

for i in range(3):
    y_pos_f = box_y0 + box_h * (0.75 - i * 0.25)
    fig.text(col1_x, y_pos_f, col1_lines[i], fontsize=6.8, color='#334155', va='center', zorder=2)
    fig.text(col2_x, y_pos_f, col2_lines[i], fontsize=6.8, color='#334155', va='center', zorder=2)

plot_path_png = os.path.join(OUTPUT_DIR, 'm6_agriculture_policy.png')
plot_path_pdf = os.path.join(OUTPUT_DIR, 'm6_agriculture_policy.pdf')

safe_savefig(plot_path_png, dpi=300, bbox_inches='tight')
safe_savefig(plot_path_pdf, bbox_inches='tight')
plt.close(fig)

print(f"[OK] High-resolution publication chart saved to: {plot_path_png}")
print(f"[OK] Vector publication PDF saved to: {plot_path_pdf}")
