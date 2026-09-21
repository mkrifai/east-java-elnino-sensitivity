"""
Milestone 5: Landscape Sensitivity Atlas (Deliverable B)
========================================================
Phase 6 -- Lag Analysis
Phase 7 -- Landscape Response Signatures (LRS)
Phase 8 -- Spatial Clustering & Regime Delineation

Integrates:
  - Climate response (P' & Z_P from CHIRPS)
  - Physical response (SM' & Z_SM from ERA5-Land, LST' & Z_LST from MODIS)
  - Vegetation response (NDVI', NDMI' & z-scores from MODIS)
  - Response lag analysis (optimal lag between rainfall and vegetation)

Computes, exports to Drive, and duplicates locally:
  1. Landscape Response Signatures (LRS) 5-dimensional feature stack
  2. Optimal Response Lag map (tau in months: 0, 1, 2)
  3. Continuous Landscape Sensitivity Index (LSI: normalized 0 to 1)
  4. 5 Landscape Response Regimes via unsupervised machine learning clustering (Weka k-Means)
  5. Centroid profiling and area breakdown per regime
  6. Direct download of local GeoTIFF duplicates to outputs/geotiffs/m5/

Output -> Deliverable B: Landscape Sensitivity Atlas of East Java

Usage:
  python scripts/m5_landscape_sensitivity.py
"""

import os
import sys
import json
import time
from datetime import datetime

# Configure UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import ee

# --- Path setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from config import (
    get_east_java,
    START_YEAR, END_YEAR,
    EL_NINO_ALL, EL_NINO_ONLY, EL_NINO_IOD,
    LA_NINA, NEUTRAL, ALL_YEARS,
    ENSO_INTENSITY, IOD_POSITIVE,
    JJA, SON, DRY_SEASON,
    CHIRPS_SCALE, EXPORT_SCALE, DRIVE_FOLDER,
    build_seasonal_collection,
    export_image, download_image_local, compute_region_stats,
)
from m2_climate_response_atlas import (
    compute_climatology as m2_compute_climatology,
    compute_anomaly_collection as m2_compute_anomaly,
    enso_composite as m2_composite,
)
from m3_physical_response import (
    build_seasonal_sm_collection,
    build_seasonal_lst_collection,
    compute_climatology as m3_compute_climatology,
    compute_anomalies as m3_compute_anomalies,
    enso_composite as m3_composite,
)
from m4_vegetation_response import (
    build_seasonal_veg_collection,
    compute_climatology as m4_compute_climatology,
    compute_anomalies as m4_compute_anomalies,
    enso_composite as m4_composite,
)


def compute_lag_surface(p_jja_col, p_son_col, ndvi_son_col, aoi_geom):
    """
    Compute optimal lag between rainfall and peak dry-season vegetation decline.
    Compares:
      - r0: correlation(P_SON, NDVI_SON) -> immediate / concurrent response (lag = 0)
      - r2: correlation(P_JJA, NDVI_SON) -> cumulative / delayed response (lag = 2 months)
    Returns:
      lag_map: integer image (0 for immediate, 2 for delayed onset control)
      lag_ratio: continuous indicator of memory / storage buffering
    """
    years = ee.List.sequence(START_YEAR, END_YEAR)

    def _pair_images(y):
        y = ee.Number(y)
        p_jja = p_jja_col.filter(ee.Filter.eq('year', y)).first().select('precipitation').rename('p_jja')
        p_son = p_son_col.filter(ee.Filter.eq('year', y)).first().select('precipitation').rename('p_son')
        v_son = ndvi_son_col.filter(ee.Filter.eq('year', y)).first().select('ndvi').rename('v_son')
        return p_jja.addBands(p_son).addBands(v_son)

    paired_col = ee.ImageCollection(years.map(_pair_images))

    # Compute Pearson correlation using pearsonsCorrelation reducer
    corr_son = paired_col.select(['p_son', 'v_son']).reduce(ee.Reducer.pearsonsCorrelation()).select('correlation').rename('r_son')
    corr_jja = paired_col.select(['p_jja', 'v_son']).reduce(ee.Reducer.pearsonsCorrelation()).select('correlation').rename('r_jja')

    # Where JJA correlation is stronger than SON correlation, lag is 2 months; otherwise immediate (0)
    # Higher positive correlation means vegetation strongly tracks that period's rain
    lag_map = ee.Image(0).where(corr_jja.gt(corr_son), 2).rename('optimal_lag_months')
    lag_diff = corr_jja.subtract(corr_son).rename('lag_memory_index')

    return lag_map, lag_diff


def main():
    print()
    print('=' * 65)
    print('   MILESTONE 5: LANDSCAPE SENSITIVITY ATLAS')
    print('   Deliverable B: Multi-Dimensional Sensitivity & Regimes')
    print('   ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
    print('=' * 65)

    ee.Initialize()
    print('\n[OK] Google Earth Engine initialized')

    aoi = get_east_java()
    aoi_geom = aoi.geometry()
    print('[OK] Study area: Jawa Timur (East Java)')

    # ----------------------------------------------------------
    # Step 1: Reconstructing Multi-Dimensional Standardized Anomalies
    # ----------------------------------------------------------
    print('\n--- Step 1: Building Multi-Variable Feature Stack (SON El Nino) ---')

    # 1. Climate: Rainfall (CHIRPS)
    print('  Loading CHIRPS rainfall anomaly...')
    chirps_son_col = build_seasonal_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    chirps_jja_col = build_seasonal_collection(JJA, START_YEAR, END_YEAR, aoi_geom)
    p_son_mean, p_son_std = m2_compute_climatology(chirps_son_col, NEUTRAL)
    p_son_anom_col = m2_compute_anomaly(chirps_son_col, p_son_mean, p_son_std)
    z_p = m2_composite(p_son_anom_col, EL_NINO_ALL, 'z_score').rename('z_p')

    # 2. Physical: Soil Moisture (ERA5-Land)
    print('  Loading ERA5-Land root-zone soil moisture anomaly...')
    sm_son_col = build_seasonal_sm_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    sm_son_mean, sm_son_std = m3_compute_climatology(sm_son_col, 'sm', NEUTRAL, min_std=0.005)
    sm_son_anom_col = m3_compute_anomalies(sm_son_col, 'sm', sm_son_mean, sm_son_std)
    z_sm = m3_composite(sm_son_anom_col, 'sm_zscore', EL_NINO_ALL).rename('z_sm')

    # 3. Physical: LST (MODIS Terra)
    print('  Loading MODIS daytime LST anomaly...')
    lst_son_col = build_seasonal_lst_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    lst_son_mean, lst_son_std = m3_compute_climatology(lst_son_col, 'lst', NEUTRAL, min_std=0.1)
    lst_son_anom_col = m3_compute_anomalies(lst_son_col, 'lst', lst_son_mean, lst_son_std)
    z_lst = m3_composite(lst_son_anom_col, 'lst_zscore', EL_NINO_ALL).rename('z_lst')

    # 4. Vegetation: NDVI & NDMI (MODIS Terra)
    print('  Loading MODIS NDVI and NDMI canopy moisture anomaly...')
    veg_son_col = build_seasonal_veg_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    ndvi_son_mean, ndvi_son_std = m4_compute_climatology(veg_son_col, 'ndvi', NEUTRAL)
    ndmi_son_mean, ndmi_son_std = m4_compute_climatology(veg_son_col, 'ndmi', NEUTRAL)

    veg_son_anom_col = m4_compute_anomalies(veg_son_col, 'ndvi', ndvi_son_mean, ndvi_son_std)
    veg_son_anom_col = m4_compute_anomalies(veg_son_anom_col, 'ndmi', ndmi_son_mean, ndmi_son_std)

    z_ndvi = m4_composite(veg_son_anom_col, 'ndvi_zscore', EL_NINO_ALL).rename('z_ndvi')
    z_ndmi = m4_composite(veg_son_anom_col, 'ndmi_zscore', EL_NINO_ALL).rename('z_ndmi')

    print('  [OK] Standardized anomaly layers assembled: [Z_P, Z_SM, Z_LST, Z_NDVI, Z_NDMI]')

    # ----------------------------------------------------------
    # Step 2: Response Lag Analysis (Phase 6)
    # ----------------------------------------------------------
    print('\n--- Step 2: Optimal Response Lag Analysis (Phase 6) ---')
    lag_map, lag_diff = compute_lag_surface(chirps_jja_col, chirps_son_col, veg_son_col, aoi_geom)
    print('  [OK] Optimal response lag surface computed')

    # ----------------------------------------------------------
    # Step 3: Continuous Landscape Sensitivity Index (LSI)
    # ----------------------------------------------------------
    print('\n--- Step 3: Formulating Composite Landscape Sensitivity Index (LSI) ---')

    # LSI formula:
    # High sensitivity occurs where:
    #   - Rainfall deficit is deep (-Z_P is high)
    #   - Soil moisture deficit is deep (-Z_SM is high)
    #   - Land surface temperature surges (+Z_LST is high)
    #   - Canopy greenness collapses (-Z_NDVI is high)
    #   - Foliar water content collapses (-Z_NDMI is high)
    #
    # Raw sensitivity sum: (-Z_P) + (-Z_SM) + (Z_LST) + (-Z_NDVI) + (-Z_NDMI)
    lsi_raw = (z_p.multiply(-1.0)
               .add(z_sm.multiply(-1.0))
               .add(z_lst)
               .add(z_ndvi.multiply(-1.0))
               .add(z_ndmi.multiply(-1.0))
               .rename('lsi_raw'))

    # Normalize LSI to 0.0 - 1.0 range based on provincial 2nd to 98th percentile
    p_stats = lsi_raw.reduceRegion(
        reducer=ee.Reducer.percentile([2, 98]),
        geometry=aoi_geom,
        scale=2000,
        maxPixels=1e10
    ).getInfo()

    p2 = list(p_stats.values())[0]
    p98 = list(p_stats.values())[1]
    if p2 is None or p98 is None or p2 == p98:
        p2, p98 = -2.0, 5.0
    print(f'  LSI normalization bounds: P2 = {p2:.2f}, P98 = {p98:.2f}')

    lsi = (lsi_raw.subtract(p2).divide(p98 - p2)).clamp(0.0, 1.0).rename('landscape_sensitivity_index')
    print('  [OK] Continuous LSI [0.0 - 1.0] computed')

    # Provincial mean LSI
    lsi_mean_val = lsi.reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi_geom, scale=2000, maxPixels=1e10).getInfo().get('landscape_sensitivity_index', 0.5)
    print(f'    Provincial Mean LSI: {lsi_mean_val:.3f}')

    # ----------------------------------------------------------
    # Step 4: Unsupervised Spatial Clustering (Phase 8: k-Means)
    # ----------------------------------------------------------
    print('\n--- Step 4: Unsupervised Spatial Clustering (5 Regimes) ---')

    # Feature stack for clustering
    feature_stack = (z_p
                     .addBands(z_sm)
                     .addBands(z_lst)
                     .addBands(z_ndvi)
                     .addBands(z_ndmi)
                     .clip(aoi_geom))

    # Sample 8,000 pixels across East Java at 1 km scale
    print('  Sampling 8,000 pixels across East Java for cluster training...')
    sample_points = feature_stack.sample(
        region=aoi_geom,
        scale=1000,
        numPixels=8000,
        seed=42,
        geometries=False
    )

    # Train k-Means clusterer with k=5
    print('  Training Weka k-Means clusterer (k=5)...')
    clusterer = ee.Clusterer.wekaKMeans(5).train(sample_points)

    # Apply clusterer
    clustered = feature_stack.cluster(clusterer).rename('cluster_raw')
    print('  [OK] Landscape classified into 5 clusters')

    # Calculate cluster centroids & areas
    print('  Calculating centroid signatures for each cluster...')
    cluster_profiles = []

    # Pixel area calculation
    pixel_area = ee.Image.pixelArea().divide(1e6)  # km2

    for cid in range(5):
        c_mask = clustered.eq(cid)

        # Area
        area_km2 = pixel_area.updateMask(c_mask).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=aoi_geom,
            scale=2000,
            maxPixels=1e10
        ).getInfo().get('area', 0.0)

        # Means of features
        c_means = feature_stack.updateMask(c_mask).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi_geom,
            scale=2000,
            maxPixels=1e10
        ).getInfo()

        c_lsi = lsi.updateMask(c_mask).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi_geom,
            scale=2000,
            maxPixels=1e10
        ).getInfo().get('landscape_sensitivity_index', 0.0)

        cluster_profiles.append({
            'raw_id': cid,
            'area_km2': round(area_km2, 1),
            'z_p': round(c_means.get('z_p', 0.0), 3),
            'z_sm': round(c_means.get('z_sm', 0.0), 3),
            'z_lst': round(c_means.get('z_lst', 0.0), 3),
            'z_ndvi': round(c_means.get('z_ndvi', 0.0), 3),
            'z_ndmi': round(c_means.get('z_ndmi', 0.0), 3),
            'mean_lsi': round(c_lsi, 3),
        })

    # Sort clusters by mean_lsi from lowest (Regime 1: Most Resilient) to highest (Regime 5: Most Sensitive)
    cluster_profiles.sort(key=lambda x: x['mean_lsi'])

    total_area = sum(p['area_km2'] for p in cluster_profiles)
    for idx, p in enumerate(cluster_profiles):
        p['regime_id'] = idx + 1
        p['area_pct'] = round((p['area_km2'] / total_area) * 100, 1) if total_area > 0 else 0.0

    # Scientific regime labeling
    regime_names = {
        1: "Regime 1: Buffered Highland Forests & Volcanic Slopes (Resilient)",
        2: "Regime 2: Irrigated Alluvial River Basins (Moderately Buffered)",
        3: "Regime 3: Rolling Uplands & Mixed Croplands (Moderate Sensitivity)",
        4: "Regime 4: Arid Rain-Shadow Corridors (High Moisture Deficit)",
        5: "Regime 5: Hyper-Sensitive Lowland Plains & Karst (Critical Vulnerability)",
    }

    for p in cluster_profiles:
        p['regime_name'] = regime_names[p['regime_id']]

    # Remap cluster_raw to ordered regime_id (1 to 5)
    from_list = [p['raw_id'] for p in cluster_profiles]
    to_list = [p['regime_id'] for p in cluster_profiles]
    regimes_img = clustered.remap(from_list, to_list).rename('landscape_response_regimes')

    print('\n--- Identified Landscape Response Regimes (Deliverable B) ---')
    print(f'  {"ID":<3} {"Regime Name":<52} {"Area (%)":>9} {"LSI":>6} {"Z_P":>6} {"Z_SM":>6} {"Z_LST":>6} {"Z_NDVI":>7}')
    print(f'  {"-"*3} {"-"*52} {"-"*9} {"-"*6} {"-"*6} {"-"*6} {"-"*6} {"-"*7}')
    for p in cluster_profiles:
        print(f'  {p["regime_id"]:<3} {p["regime_name"][:52]:<52} {p["area_pct"]:>8.1f}% {p["mean_lsi"]:>6.2f} {p["z_p"]:>+6.2f} {p["z_sm"]:>+6.2f} {p["z_lst"]:>+6.2f} {p["z_ndvi"]:>+7.2f}')

    # ----------------------------------------------------------
    # Step 5: Save Statistics JSON
    # ----------------------------------------------------------
    output_dir = os.path.join(PROJECT_DIR, 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    summary_json = {
        'generated': datetime.now().isoformat(),
        'provincial_mean_lsi': round(lsi_mean_val, 3),
        'total_area_km2': round(total_area, 1),
        'cluster_regimes': cluster_profiles,
    }
    stats_path = os.path.join(output_dir, 'm5_sensitivity_statistics.json')
    with open(stats_path, 'w') as f:
        json.dump(summary_json, f, indent=2)
    print(f'\n[OK] Sensitivity statistics saved -> {stats_path}')

    # ----------------------------------------------------------
    # Step 6: Export to Google Drive & Local Duplicates
    # ----------------------------------------------------------
    print(f'\n--- Step 6: Exporting to Drive & Downloading Local Duplicates ---')

    exports = {
        # Core Deliverable B Layers
        'M5_Landscape_Sensitivity_Index':  lsi,
        'M5_Landscape_Response_Regimes':   regimes_img,
        'M5_Optimal_Response_Lag':         lag_map,
        'M5_Lag_Memory_Index':             lag_diff,

        # Standardized LRS Component Layers
        'M5_LRS_ZP_SON':                   z_p,
        'M5_LRS_ZSM_SON':                  z_sm,
        'M5_LRS_ZLST_SON':                 z_lst,
        'M5_LRS_ZNDVI_SON':                z_ndvi,
        'M5_LRS_ZNDMI_SON':                z_ndmi,
    }

    # Start Drive tasks
    drive_tasks = []
    for desc, img in exports.items():
        task = export_image(img, desc, aoi, scale=1000)
        drive_tasks.append(task)
        print(f'  [Drive Task] {desc}')

    # Download local duplicates
    m5_local_dir = os.path.join(output_dir, 'geotiffs', 'm5')
    os.makedirs(m5_local_dir, exist_ok=True)
    print(f'\n  Downloading local GeoTIFF duplicates to {m5_local_dir}...')

    for desc, img in exports.items():
        dst = os.path.join(m5_local_dir, f"{desc}.tif")
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            print(f'  [EXISTS] {desc}.tif ({os.path.getsize(dst)/1024:.1f} KB)')
            continue
        try:
            print(f'  [DOWNLOAD] {desc}...', end=' ', flush=True)
            t0 = time.time()
            download_image_local(img, desc, aoi_geom, m5_local_dir, scale=1000)
            dt = time.time() - t0
            print(f'OK ({os.path.getsize(dst)/1024:.1f} KB in {dt:.1f}s)')
        except Exception as e:
            print(f'FAILED: {e}')

    print('\n' + '=' * 65)
    print('   MILESTONE 5 COMPLETE')
    print('=' * 65)


if __name__ == '__main__':
    main()
