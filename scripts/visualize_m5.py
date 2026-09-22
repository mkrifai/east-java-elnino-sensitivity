"""
Milestone 5 Visualization: Landscape Sensitivity Atlas & Regimes (Deliverable B) - Layout Version 2
===================================================================================================
New Portrait Layout Variant (without modifying the original visualize_m5.py):

Key Architectural Features:
  1. Panel (a) Spatial Map:
     - Vector choropleth of dominant regimes across 582 sub-districts (kecamatan).
     - Title cleaned: "(a) Spatial Distribution of 5 Landscape Response Regimes Across East Java".
     - Scale Ratio Box ("Scale 1 : 2,500,000") moved to lower-right corner (Bali Strait / Indian Ocean).
     - Vector cartographic Compass Rose moved to upper-right corner.
     - Northernmost Island Callout added for Pulau Bawean (Kab. Gresik: Kec. Sangkapura & Tambak)
       identifying its classification as Regime 5 (Hyper-Sensitive Lowland & Karst).
     - Added explicit axis labels: "Longitude" and "Latitude".
  2. Panel (b) Hierarchical LSI Ranking:
     - Relocated directly beneath Panel (a), sharing the exact same column width.
     - Percentage removed from vertical y-axis labels (clean "Regime 1" to "Regime 5").
     - In-bar LSI values removed; detailed annotations kept outside the bars.
     - Sub-axis label "[<- Buffered Zone | Elevated Vulnerability ->]" styled in unbolded gray.
     - Generous horizontal limits (xlim 0.0 to 1.20) ensuring zero text overflow.
  3. Panel (c) Portrait Multidimensional Response Signatures (LRS):
     - Relocated to the right column, spanning the full height of Panel (a) + Panel (b).
     - Grouped horizontal bars across the 5 biophysical features (ZP, ZSM, ZLST, ZNDVI, ZNDMI).
     - Full within-cluster spatial variability error bars (+/- 1 SD across 45,205 pixels).
     - Bounded vertical threshold lines, baseline SEM band, zero line, and unified 3-row top legend card.
     - Two-line y-axis labels preventing any encroachment on the left column.
  4. Footer Box:
     - Explanatory two-column scientific methodology and policy notes spanning the full base.
  5. High-resolution exports to outputs/m5_landscape_sensitivity.png (300 DPI) and .pdf.
"""

import os
import json
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, VPacker, DrawingArea, TextArea

# --- Path setup ---
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'outputs')
GEOTIFF_DIR = os.path.join(OUTPUT_DIR, 'geotiffs', 'm5')
JSON_PATH = os.path.join(OUTPUT_DIR, 'm5_sensitivity_statistics.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

regimes = data['cluster_regimes']
provincial_mean_lsi = data.get('provincial_mean_lsi', 0.576)
total_area_km2 = data.get('total_area_km2', 44528.2)

# Sort regimes by regime_id (1 to 5)
regimes = sorted(regimes, key=lambda x: x['regime_id'])

# Okabe-Ito & ColorBrewer Scientific Palette for Landscape Regimes
regime_colors = [
    '#238B45',  # Regime 1: Forest Green (Buffered Highlands / Resilient)
    '#0072B2',  # Regime 2: Ocean Blue (Irrigated Alluvial Basins)
    '#E69F00',  # Regime 3: Amber Gold (Rolling Uplands & Mixed Croplands)
    '#D55E00',  # Regime 4: Vermilion (Arid Rain-Shadow Corridors)
    '#B2182B',  # Regime 5: Deep Crimson (Hyper-Sensitive Lowlands / Karst)
]

regime_edges = [
    '#00441B',  # R1 edge: Deepest Pine
    '#0F172A',  # R2 edge: Deep Slate
    '#78350F',  # R3 edge: Deep Amber/Brown
    '#450A0A',  # R4 edge: Deep Rust
    '#5C0000',  # R5 edge: Deep Maroon
]

# Load spatial GeoTIFF data and compute within-cluster standard deviations
raster_path = os.path.join(GEOTIFF_DIR, 'M5_Landscape_Response_Regimes.tif')
with rasterio.open(raster_path) as src:
    regimes_grid = src.read(1)
    bounds = src.bounds
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    raster_trans = src.transform
    raster_crs = src.crs
    raster_meta = src.meta.copy()

feature_tif_names = [
    'M5_LRS_ZP_SON.tif',
    'M5_LRS_ZSM_SON.tif',
    'M5_LRS_ZLST_SON.tif',
    'M5_LRS_ZNDVI_SON.tif',
    'M5_LRS_ZNDMI_SON.tif'
]

features_data = []
for fname in feature_tif_names:
    fpath = os.path.join(GEOTIFF_DIR, fname)
    with rasterio.open(fpath) as src_f:
        features_data.append(src_f.read(1))

# Compute within-cluster standard deviations (+/- 1 SD) across all valid pixels
within_cluster_sds = []
for r in range(1, 6):
    r_mask = (regimes_grid == r)
    sds_r = [float(np.nanstd(f[r_mask])) for f in features_data]
    within_cluster_sds.append(sds_r)

within_cluster_sds = np.array(within_cluster_sds)  # shape: (5 regimes, 5 features)

# Load administrative vector boundaries from SHP and compute dominant regime per kecamatan
SHP_PATH = os.path.join(PROJECT_DIR, 'Batas Administrasi Kecamatan di Jawa Timur', 'administrasi_ar_kec_jatim.shp')
has_shp = os.path.exists(SHP_PATH)
if has_shp:
    import geopandas as gpd
    import warnings
    from scipy.ndimage import distance_transform_edt
    from rasterio.features import geometry_mask
    from rasterio.mask import mask
    from scipy.stats import mode
    import rasterio.io

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        gdf_raw = gpd.read_file(SHP_PATH)
        if gdf_raw.crs != raster_crs:
            gdf_raw = gdf_raw.to_crs(raster_crs)

        gdf_kab = gdf_raw.dissolve(by='NAMA_KABUP')
        gdf_prov = gdf_raw.dissolve()

        # Seamless domain filling for NoData pixels inside official provincial boundary
        prov_geom = gdf_prov.geometry.iloc[0]
        prov_mask = ~geometry_mask([prov_geom], out_shape=regimes_grid.shape, transform=raster_trans, invert=False)
        valid_mask = (regimes_grid >= 1) & (regimes_grid <= 5)
        indices = distance_transform_edt(~valid_mask, return_distances=False, return_indices=True)
        filled_grid = regimes_grid[tuple(indices)]
        display_regimes = np.where(prov_mask, filled_grid, np.nan)

        # Compute dominant regime per kecamatan (majority mode across all 582 kecamatan)
        mem_meta = raster_meta.copy()
        mem_meta.update({'driver': 'GTiff', 'dtype': 'int16', 'nodata': -9999})
        with rasterio.io.MemoryFile() as memfile:
            with memfile.open(**mem_meta) as mem_src:
                mem_src.write(filled_grid.astype(np.int16), 1)
                dom_regimes = []
                for geom in gdf_raw.geometry:
                    try:
                        out_img, _ = mask(mem_src, [geom], crop=True)
                        vals = out_img[0]
                        valid = vals[(vals >= 1) & (vals <= 5)]
                        if len(valid) > 0:
                            m = mode(valid, keepdims=False).mode
                            dom_regimes.append(int(m))
                        else:
                            dom_regimes.append(1)
                    except Exception:
                        dom_regimes.append(1)

        gdf_raw['dom_regime'] = dom_regimes
else:
    display_regimes = np.ma.masked_where((regimes_grid < 1) | (regimes_grid > 5), regimes_grid)

# =============================================================================
# CONFIGURE MASTER FIGURE & 2-COLUMN GRIDSPEC (PORTRAIT RIGHT COLUMN)
# =============================================================================
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig = plt.figure(figsize=(16.2, 13.5), dpi=300)

# Layout:
# Left column: row 0 (Map), row 1 (LSI horizontal bars) -> exactly identical width!
# Right column: ax_lrs (Portrait LRS bars spanning both rows 0 & 1)
# hspace=0.14 and wspace=0.11 compact both vertical and horizontal inter-panel spacing
gs = gridspec.GridSpec(2, 2, height_ratios=[1.18, 0.82], width_ratios=[1.22, 1.0],
                       hspace=0.14, wspace=0.11,
                       top=0.916, bottom=0.138, left=0.065, right=0.975)

ax_map = fig.add_subplot(gs[0, 0])
ax_lsi = fig.add_subplot(gs[1, 0])
ax_lrs = fig.add_subplot(gs[:, 1])

text_stroke = [pe.withStroke(linewidth=2.8, foreground='white')]
map_stroke = [pe.withStroke(linewidth=2.5, foreground='white')]


# =============================================================================
# PANEL (a): SPATIAL DISTRIBUTION OF 5 LANDSCAPE RESPONSE REGIMES
# =============================================================================
ax_map.set_facecolor('#F1F5F9')

if has_shp:
    for r_id in range(1, 6):
        sub = gdf_raw[gdf_raw['dom_regime'] == r_id]
        if not sub.empty:
            sub.plot(ax=ax_map, facecolor=regime_colors[r_id - 1],
                     edgecolor='#475569', linewidth=0.20, alpha=0.92, zorder=2)

    # Regency / Kabupaten internal boundaries
    gdf_kab.boundary.plot(ax=ax_map, color='#0F172A', linewidth=0.75, alpha=0.85, zorder=3)
    # Provincial outer perimeter
    gdf_prov.boundary.plot(ax=ax_map, color='#0F172A', linewidth=1.1, zorder=4)
else:
    cmap_regimes = ListedColormap(regime_colors)
    im_map = ax_map.imshow(display_regimes, cmap=cmap_regimes, extent=extent,
                           vmin=1, vmax=5, interpolation='nearest', zorder=2)

# Geographic framing & coordinates (Y-lim extended to -5.25 to fully include Pulau Bawean)
ax_map.set_xlim(110.8, 116.0)
ax_map.set_ylim(-8.9, -5.25)

ax_map.set_xticks([111.0, 112.0, 113.0, 114.0, 115.0])
ax_map.set_xticklabels(['111\u00b0E', '112\u00b0E', '113\u00b0E', '114\u00b0E', '115\u00b0E'],
                       fontsize=8.2, fontweight='bold', color='#1E293B')
ax_map.set_yticks([-8.5, -8.0, -7.5, -7.0, -6.5, -6.0, -5.5])
ax_map.set_yticklabels(['8.5\u00b0S', '8.0\u00b0S', '7.5\u00b0S', '7.0\u00b0S', '6.5\u00b0S', '6.0\u00b0S', '5.5\u00b0S'],
                       fontsize=8.2, fontweight='bold', color='#1E293B')

# Item 3: Add explicit Latitude and Longitude labels with enhanced labelpad
ax_map.set_xlabel('Longitude', fontsize=9.0, fontweight='bold', color='#1E293B', labelpad=9)
ax_map.set_ylabel('Latitude', fontsize=9.0, fontweight='bold', color='#1E293B', labelpad=4)
ax_map.grid(True, linestyle=':', color='#94A3B8', alpha=0.55, zorder=3)

# Key physiographic landmark callouts
landmarks = [
    (112.92, -7.94, 'Bromo-Semeru\n(R1: Highland)', '#00441B', (0, 18)),
    (114.24, -8.06, 'Ijen Complex\n(R1: Highland)', '#00441B', (15, 15)),
    (112.20, -7.50, 'Brantas River Basin\n(R2: Irrigated Alluvial)', '#003666', (-45, 18)),
    (111.60, -8.15, 'Southern Uplands\n(R3: Croplands)', '#78350F', (-35, -22)),
    (114.05, -7.70, 'Rain-Shadow Corridor\n(R4: Arid Plains)', '#450A0A', (20, 12)),
    (113.50, -7.02, 'Madura Island\n(R5: Lowland & Karst)', '#5C0000', (0, 16)),
    (111.85, -6.90, 'Northern Karst (Tuban)\n(R5: Hyper-Sensitive)', '#5C0000', (-45, 18)),
]

for lon, lat, label, c_txt, (dx, dy) in landmarks:
    ax_map.plot(lon, lat, marker='o', markersize=3.5, color='#0F172A',
                markeredgecolor='white', markeredgewidth=0.8, zorder=5)
    ax_map.annotate(label, xy=(lon, lat), xytext=(dx, dy), textcoords='offset points',
                    fontsize=6.8, fontweight='bold', color=c_txt, path_effects=map_stroke,
                    arrowprops=dict(arrowstyle='->', lw=0.7, color='#334155'), zorder=5)

# Item 1c: Northernmost Island Callout (Pulau Bawean, Kab. Gresik)
bawean_lon, bawean_lat = 112.84, -5.42
ax_map.plot(bawean_lon, bawean_lat, marker='o', markersize=4.0, color='#0F172A',
            markeredgecolor='white', markeredgewidth=0.9, zorder=5)
ax_map.annotate('Pulau Bawean (Kab. Gresik)\n(R5: Hyper-Sensitive Karst)',
                xy=(bawean_lon, bawean_lat), xytext=(24, -6), textcoords='offset points',
                fontsize=7.2, fontweight='bold', color='#5C0000', path_effects=map_stroke,
                arrowprops=dict(arrowstyle='->', lw=0.8, color='#0F172A'), zorder=5)

# Item 1a: Scale Ratio Box in LOWER-RIGHT corner (open ocean south of Bali/Banyuwangi)
scale_box = AnchoredOffsetbox(
    loc='lower right',
    child=TextArea('Scale  1 : 2,500,000',
                   textprops=dict(fontsize=7.8, fontweight='bold', color='#0F172A')),
    pad=0.40, frameon=True,
    bbox_to_anchor=(0.970, 0.055),
    bbox_transform=ax_map.transAxes, borderpad=0.0
)
scale_box.patch.set_boxstyle('round,pad=0.35,rounding_size=0.15')
scale_box.patch.set_facecolor('white')
scale_box.patch.set_edgecolor('#94A3B8')
scale_box.patch.set_linewidth(0.85)
scale_box.patch.set_alpha(0.96)
scale_box.set_zorder(6)
ax_map.add_artist(scale_box)

# Item 1b: Vector Cartographic Compass Rose in UPPER-RIGHT corner (open sea north of Madura/Bali)
cx, cy = 115.35, -5.75
ax_map.add_patch(Circle((cx, cy), 0.22, facecolor='white', edgecolor='#CBD5E1', lw=0.6, alpha=0.92, zorder=5))
ax_map.add_patch(Circle((cx, cy), 0.12, facecolor='none', edgecolor='#475569', lw=0.6, linestyle=':', zorder=6))

# 4-point two-tone compass needle
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

# Item 2: Remove "... by Kecamatan (n = 582)" from Panel (a) title
ax_map.set_title('(a) Spatial Distribution of 5 Landscape Response Regimes Across East Java',
                 fontsize=10.5, fontweight='bold', pad=8, loc='left')


# =============================================================================
# PANEL (b): HIERARCHICAL LANDSCAPE SENSITIVITY RANKING (LSI) & EXPOSURE
# =============================================================================
y_pos = np.arange(len(regimes))
lsi_values = [r['mean_lsi'] for r in regimes]

# Background vulnerability zone shading
ax_lsi.axvspan(0.0, 0.50, color='#F0FDF4', alpha=0.50, zorder=0)  # Buffered Zone
ax_lsi.axvspan(0.50, 0.60, color='#FFFBEB', alpha=0.45, zorder=0)  # Transitional Zone
ax_lsi.axvspan(0.60, 1.22, color='#FEF2F2', alpha=0.50, zorder=0)  # Elevated Vulnerability Zone

# Watermark zone annotations at top
ax_lsi.text(0.25, 4.54, 'BUFFERED ZONE (39.2%)',
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#15803D', alpha=0.90)
ax_lsi.text(0.91, 4.54, 'ELEVATED VULNERABILITY (60.8%)',
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#B91C1C', alpha=0.90)

# Horizontal bars
hbars = ax_lsi.barh(y_pos, lsi_values, height=0.50,
                    color=regime_colors, edgecolor=regime_edges,
                    linewidth=0.9, alpha=0.92, zorder=2)

# Provincial mean benchmark reference line
ax_lsi.axvline(provincial_mean_lsi, color='#334155', linestyle='--', linewidth=1.2, zorder=3)
ax_lsi.text(provincial_mean_lsi, 4.54,
            f'Prov. Mean\n{provincial_mean_lsi:.3f}',
            ha='center', va='center', fontsize=7.0, fontweight='bold',
            color='#1E293B', path_effects=text_stroke, zorder=4)

# Item 5: Keep only outside text annotations (In-bar badges removed!)
for bar, r in zip(hbars, regimes):
    w_val = bar.get_width()
    y_val = bar.get_y() + bar.get_height() / 2

    regime_short = r['regime_name'].split(':')[1].strip()
    annot_line1 = f"LSI: {r['mean_lsi']:.3f}  |  {r['area_km2']:,.0f} km\u00b2 ({r['area_pct']}%)"
    annot_line2 = f"{regime_short}"

    ax_lsi.text(w_val + 0.016, y_val + 0.08, annot_line1,
                va='center', fontsize=7.4, fontweight='bold', color='#0F172A',
                path_effects=text_stroke, zorder=4)
    ax_lsi.text(w_val + 0.016, y_val - 0.11, annot_line2,
                va='center', fontsize=6.8, color='#475569',
                path_effects=text_stroke, zorder=4)

# Item 5: Vertical ticklabels without percentage (clean "Regime 1" to "Regime 5")
ax_lsi.set_yticks(y_pos)
ax_lsi.set_yticklabels([f"Regime {r['regime_id']}" for r in regimes],
                       fontsize=8.8, fontweight='bold', color='#0F172A')

# Item 1: Increased labelpad for LSI label; Item 2: Remove "[... Buffered Zone ...]" subtitle
ax_lsi.set_xlabel('Landscape Sensitivity Index (LSI: 0 to 1)',
                  fontsize=9.0, fontweight='bold', color='#0F172A', labelpad=9)

# Ensure all text strictly fits inside plot box without overflow
ax_lsi.set_xlim(0.0, 1.22)
ax_lsi.set_ylim(-0.55, 4.80)
ax_lsi.set_xticks([0.0, 0.2, 0.4, 0.576, 0.8, 1.0])
ax_lsi.set_xticklabels(['0.0', '0.2', '0.4', '0.576', '0.8', '1.0'], fontsize=8.0)
ax_lsi.grid(True, linestyle='--', alpha=0.45, zorder=0)

ax_lsi.set_title('(b) Hierarchical Landscape Sensitivity Ranking (LSI)',
                 fontsize=10.5, fontweight='bold', pad=8, loc='left')


# =============================================================================
# PANEL (c): PORTRAIT MULTI-DIMENSIONAL LANDSCAPE RESPONSE SIGNATURES (LRS)
# =============================================================================
# Features ordered top to bottom with 2-line formatting to prevent column overlap
features_portrait = [
    'Precipitation Deficit\n($Z_{\\mathrm{P}}$)',
    'Soil Moisture Deficit\n($Z_{\\mathrm{SM}}$)',
    'Surface Thermal Surge\n($Z_{\\mathrm{LST}}$)',
    'Canopy Greenness Loss\n($Z_{\\mathrm{NDVI}}$)',
    'Foliar Water Desiccation\n($Z_{\\mathrm{NDMI}}$)'
]

n_feat = len(features_portrait)
# Y-positions for groups (from top to bottom: 4 to 0)
group_y_centers = np.arange(n_feat)[::-1] * 1.35
bar_h = 0.16
# Regimes order: Regime 5 (top) to Regime 1 (bottom)
regime_offsets = np.array([-2, -1, 0, 1, 2]) * (bar_h + 0.035)

# Background Baseline SEM vertical ribbon (+/- 0.408 Z)
ax_lrs.axvspan(-0.408, 0.408, color='#94A3B8', alpha=0.12, zorder=1)
ax_lrs.axvline(0, color='#0F172A', linewidth=1.2, zorder=3)

# Horizontal group dividers
for gy in group_y_centers[:-1]:
    ax_lrs.axhline(gy - 0.675, color='#E2E8F0', linestyle='-', linewidth=0.8, zorder=1)

# Plot horizontal grouped bars for each feature
err_kwargs = dict(lw=0.8, capsize=2.2, capthick=0.8, ecolor='#334155')

for f_idx in range(n_feat):
    gy = group_y_centers[f_idx]
    for r_idx, r in enumerate(regimes):
        feat_vals = [r['z_p'], r['z_sm'], r['z_lst'], r['z_ndvi'], r['z_ndmi']]
        val = feat_vals[f_idx]
        sd = within_cluster_sds[r_idx, f_idx]
        y_coord = gy + regime_offsets[r_idx]

        bar = ax_lrs.barh(y_coord, val, height=bar_h, xerr=sd, error_kw=err_kwargs,
                          color=regime_colors[r_idx], edgecolor=regime_edges[r_idx],
                          linewidth=0.85, alpha=0.92, zorder=2)

        # Value label with halo
        v_str = f"{val:+.2f}".replace('-', '\u2212')
        if val >= 0:
            # Positive surge: placed to the right of error whisker
            x_annot = val + sd + 0.04
            ha = 'left'
        else:
            # Deficit: placed to the left of error whisker
            x_annot = val - sd - 0.04
            ha = 'right'

        ax_lrs.text(x_annot, y_coord, v_str,
                    ha=ha, va='center', fontsize=6.2, fontweight='bold',
                    color='#1E293B', path_effects=[pe.withStroke(linewidth=2.5, foreground='white')],
                    zorder=4)

# Segmented threshold vertical lines
# Deficit thresholds: across groups 0, 1 (P, SM) and 3, 4 (NDVI, NDMI)
y_span_top = [group_y_centers[1] - 0.50, group_y_centers[0] + 0.45]
y_span_bot = [group_y_centers[4] - 0.50, group_y_centers[3] + 0.50]

for y_sp in [y_span_top, y_span_bot]:
    ax_lrs.plot([-1.0, -1.0], y_sp, color='#DC2626', linestyle='--', linewidth=1.1, zorder=2)
    ax_lrs.plot([-0.5, -0.5], y_sp, color='#D97706', linestyle=':', linewidth=1.1, zorder=2)

# Thermal Surge threshold: across group 2 (LST)
y_span_lst = [group_y_centers[2] - 0.50, group_y_centers[2] + 0.50]
ax_lrs.plot([0.5, 0.5], y_span_lst, color='#9333EA', linestyle='-.', linewidth=1.1, zorder=2)

# Item 1: Rotated 90 deg clockwise, placed closer to panel (c) box spine (widening gap to panels a/b)
ax_lrs.set_yticks(group_y_centers)
ax_lrs.set_yticklabels(features_portrait, fontsize=7.8, fontweight='bold', color='#0F172A',
                       rotation=90, va='center', ha='center', multialignment='center')
ax_lrs.tick_params(axis='y', pad=10)
# Increased labelpad for SCA horizontal label
ax_lrs.set_xlabel('Standardized Centroid Anomaly (Z-score)', fontsize=9.0, fontweight='bold', color='#0F172A', labelpad=9)
ax_lrs.set_xlim(-1.95, 1.65)
ax_lrs.set_xticks([-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5])
ax_lrs.set_xticklabels(['\u22121.5', '\u22121.0', '\u22120.5', '0.0', '+0.5', '+1.0', '+1.5'], fontsize=8.0)
ax_lrs.set_ylim(group_y_centers[-1] - 0.65, group_y_centers[0] + 0.70)
ax_lrs.grid(True, linestyle='--', alpha=0.45, zorder=0)

# Item 3: Title without "Across ... spread"
ax_lrs.set_title('(c) Multi-Dimensional Landscape Response Signatures (LRS)',
                 fontsize=10.5, fontweight='bold', pad=8, loc='left')

# Item 3: Add percentage to Regime legend (ordered Regime 5 top down to Regime 1 bottom); Item 4: Enhanced margin
reg_items = []
for i, r in reversed(list(enumerate(regimes))):
    da = DrawingArea(12, 8, 0, 0)
    da.add_artist(Rectangle((0, 0), 12, 8, facecolor=regime_colors[i], edgecolor=regime_edges[i], lw=0.85))
    ta = TextArea(f"Regime {r['regime_id']} ({r['area_pct']}%)", textprops=dict(fontsize=6.8, color='#0F172A', fontweight='bold'))
    reg_items.append(HPacker(children=[da, ta], align='center', pad=0, sep=5))

reg_packer = VPacker(children=reg_items, align='left', pad=0, sep=3)
anchored_regimes = AnchoredOffsetbox(
    loc='upper right', child=reg_packer, pad=0.45, frameon=True,
    bbox_to_anchor=(0.965, 0.970), bbox_transform=ax_lrs.transAxes, borderpad=0.0
)
anchored_regimes.patch.set_boxstyle('round,pad=0.35,rounding_size=0.15')
anchored_regimes.patch.set_facecolor('white')
anchored_regimes.patch.set_edgecolor('#CBD5E1')
anchored_regimes.patch.set_linewidth(0.85)
anchored_regimes.patch.set_alpha(0.96)
anchored_regimes.set_zorder(6)
ax_lrs.add_artist(anchored_regimes)

# Item 4 & 5: Separate Thresholds & Baseline SEM card in LOWER-RIGHT corner with enhanced margin
da_t1 = DrawingArea(14, 8, 0, 0)
da_t1.add_artist(Line2D([0, 14], [4, 4], color='#DC2626', linestyle='--', lw=1.2))
ta_t1 = TextArea('Severe Deficit ($Z = \u22121.0$)', textprops=dict(fontsize=6.5, color='#DC2626', fontweight='bold'))
r_t1 = HPacker(children=[da_t1, ta_t1], align='center', pad=0, sep=5)

da_t2 = DrawingArea(14, 8, 0, 0)
da_t2.add_artist(Line2D([0, 14], [4, 4], color='#D97706', linestyle=':', lw=1.2))
ta_t2 = TextArea('Mod. Deficit ($Z = \u22120.5$)', textprops=dict(fontsize=6.5, color='#B45309', fontweight='bold'))
r_t2 = HPacker(children=[da_t2, ta_t2], align='center', pad=0, sep=5)

da_t3 = DrawingArea(14, 8, 0, 0)
da_t3.add_artist(Line2D([0, 14], [4, 4], color='#9333EA', linestyle='-.', lw=1.2))
ta_t3 = TextArea('Thermal Surge ($Z = +0.5$)', textprops=dict(fontsize=6.5, color='#9333EA', fontweight='bold'))
r_t3 = HPacker(children=[da_t3, ta_t3], align='center', pad=0, sep=5)

da_base = DrawingArea(14, 8, 0, 0)
da_base.add_artist(Rectangle((0, 0), 14, 8, facecolor='#94A3B8', alpha=0.30, edgecolor='#94A3B8', lw=0.6))
ta_base = TextArea('Baseline SEM (\u00b10.41 Z)', textprops=dict(fontsize=6.5, color='#475569', fontweight='bold'))
r_base = HPacker(children=[da_base, ta_base], align='center', pad=0, sep=5)

thresh_packer = VPacker(children=[r_t1, r_t2, r_t3, r_base], align='left', pad=0, sep=3)
anchored_thresh = AnchoredOffsetbox(
    loc='lower right', child=thresh_packer, pad=0.45, frameon=True,
    bbox_to_anchor=(0.965, 0.040), bbox_transform=ax_lrs.transAxes, borderpad=0.0
)
anchored_thresh.patch.set_boxstyle('round,pad=0.35,rounding_size=0.15')
anchored_thresh.patch.set_facecolor('white')
anchored_thresh.patch.set_edgecolor('#CBD5E1')
anchored_thresh.patch.set_linewidth(0.85)
anchored_thresh.patch.set_alpha(0.96)
anchored_thresh.set_zorder(6)
ax_lrs.add_artist(anchored_thresh)


# =============================================================================
# MASTER FIGURE HEADERS (EXPLICIT PERIOD & SAMPLING SPECIFICATION)
# =============================================================================
fig.suptitle('East Java Terrestrial Landscape Sensitivity & Response Regimes',
             fontsize=13.5, fontweight='bold', y=0.982)

fig.text(0.50, 0.958,
         (f'Peak Dry Season (SON) Response Across Historical El Ni\u00f1o Episodes (2001\u20132025)  |  '
          f'Weka k-Means (k = 5, n = 8,000 Spatial Samples, seed = 42)  |  '
          f'Composite LSI (0 to 1, Prov. Mean = {provincial_mean_lsi:.3f})  |  '
          f'Total Landscape: {total_area_km2:,.0f} km\u00b2'),
         ha='center', fontsize=8.4, color='#475569')


# Item 2: Shorten distance between footer and panels (b)/(c)
box_x0 = 0.065
box_w = 0.910
box_y0 = 0.033
box_h = 0.052

rect = FancyBboxPatch((box_x0, box_y0), box_w, box_h,
                      boxstyle='round,pad=0.004,rounding_size=0.008',
                      transform=fig.transFigure,
                      fc='#F8FAFC', ec='#CBD5E1', lw=0.9, alpha=0.95, zorder=1)
fig.patches.append(rect)

div_x = box_x0 + box_w * 0.50
div_line = Line2D([div_x, div_x], [box_y0 + 0.006, box_y0 + box_h - 0.006],
                  transform=fig.transFigure, color='#CBD5E1', lw=0.9, linestyle='-', zorder=2)
fig.add_artist(div_line)

col1_lines = [
    "\u2022 ML Pipeline: Unsupervised k-Means (k=5, n=8,000 spatial samples, seed=42) on 5 standardized anomaly layers (1 km grid).",
    r"• LSI Formulation: $\mathrm{LSI} = [(-Z_{\mathrm{P}}) + (-Z_{\mathrm{SM}}) + (Z_{\mathrm{LST}}) + (-Z_{\mathrm{NDVI}}) + (-Z_{\mathrm{NDMI}}) - P_{2}] / (P_{98} - P_{2})$, scaled to $[0, 1]$.",
    "\u2022 Within-Cluster Dispersion: Error bars denote \u00b11 SD across 45,205 pixels (uniform macro-climate vs heterogeneous canopy)."
]

col2_lines = [
    "\u2022 Biophysical Buffering: Volcanic orography & irrigation networks buffer R1\u2013R2 (39.2% area); shallow soils compound R4\u2013R5.",
    r"• Thermal-Moisture Coupling: R3 uplands exhibit peak thermal surge (+0.89 $Z_{\mathrm{LST}}$), driving severe foliar desiccation (−1.02 $Z_{\mathrm{NDMI}}$).",
    "\u2022 Policy Implications: Priority targeted water allocation, reservoir quotas, and crop insurance for 27,100 km\u00b2 in Regimes 3\u20135."
]

col1_x = box_x0 + 0.010
col2_x = div_x + 0.012

for i in range(3):
    y_pos_f = box_y0 + box_h * (0.75 - i * 0.25)
    fig.text(col1_x, y_pos_f, col1_lines[i], fontsize=7.1, color='#334155', va='center', zorder=2)
    fig.text(col2_x, y_pos_f, col2_lines[i], fontsize=7.1, color='#334155', va='center', zorder=2)


# =============================================================================
# SAFE EXPORT PIPELINE (NEW OUTPUT FILENAMES)
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

# Item 5: Perfect geometric alignment: Height of (c) equals exact visual span of (a) + (b)
fig.canvas.draw()
pos_map = ax_map.get_position()
pos_lsi = ax_lsi.get_position()
pos_lrs = ax_lrs.get_position()
ax_lrs.set_position([pos_lrs.x0, pos_lsi.y0, pos_lrs.width, pos_map.y1 - pos_lsi.y0])

plot_path_png = os.path.join(OUTPUT_DIR, 'm5_landscape_sensitivity.png')
plot_path_pdf = os.path.join(OUTPUT_DIR, 'm5_landscape_sensitivity.pdf')

safe_savefig(plot_path_png, dpi=300, bbox_inches='tight')
safe_savefig(plot_path_pdf, bbox_inches='tight')
plt.close(fig)

print(f"[OK] High-resolution publication chart saved to: {plot_path_png}")
print(f"[OK] Vector publication PDF saved to: {plot_path_pdf}")
