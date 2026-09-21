"""
Milestone 4: Vegetation Response (NDVI, EVI, and NDMI)
=====================================================
Phase 5 -- Vegetation Response (MODIS Terra 1 km)

Computes, exports to Drive, and duplicates locally:
  1. Seasonal vegetation climatology (NDVI, EVI, NDMI for JJA and SON)
  2. El Nino vegetation anomaly composites (absolute and z-score)
  3. La Nina vegetation composites for contrast
  4. Pure El Nino vs Compound (El Nino + IOD+) vegetation response
  5. Cross-variable coupling metrics:
     - Vegetation Sensitivity Index (VSI)
     - Canopy Water Stress Hotspot mask
  6. Per-event vegetation statistics for all 8 El Nino events
  7. Export GeoTIFFs to Google Drive (folder: EastJava_ElNino_Sensitivity)
  8. Direct download of local GeoTIFF duplicates to outputs/geotiffs/m4/

Output -> Deliverable B component: Vegetation Sensitivity Surface

Usage:
  python scripts/m4_vegetation_response.py
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
    MODIS_NDVI,
    EXPORT_SCALE, DRIVE_FOLDER,
    export_image, download_image_local, compute_region_stats,
)


# ================================================================
#  COLLECTION BUILDER
# ================================================================

def build_seasonal_veg_collection(season_months, start_year, end_year, aoi=None):
    """
    Build annual seasonal vegetation collection from MODIS Terra MOD13A2 (16-day, 1 km).
    Bands:
      - 'ndvi': NDVI * 0.0001
      - 'evi':  EVI * 0.0001
      - 'ndmi': (b02 - b07) / (b02 + b07)
    """
    modis = ee.ImageCollection(MODIS_NDVI)
    if aoi is not None:
        modis = modis.filterBounds(aoi)

    first_month = season_months[0]
    last_month  = season_months[-1]
    years = ee.List.sequence(start_year, end_year)

    def _seasonal_veg(year):
        year  = ee.Number(year)
        start = ee.Date.fromYMD(year, first_month, 1)
        end   = ee.Date.fromYMD(year, last_month, 1).advance(1, 'month')

        season_imgs = modis.filterDate(start, end)

        def _calc_indices(img):
            # Scale NDVI and EVI
            ndvi = img.select('NDVI').multiply(0.0001).rename('ndvi')
            evi  = img.select('EVI').multiply(0.0001).rename('evi')
            # NDMI = (NIR - SWIR) / (NIR + SWIR)
            ndmi = img.normalizedDifference(['sur_refl_b02', 'sur_refl_b07']).rename('ndmi')
            return ndvi.addBands(evi).addBands(ndmi)

        veg_mean = season_imgs.map(_calc_indices).mean()
        return veg_mean.set({
            'year': year,
            'system:time_start': start.millis(),
        })

    return ee.ImageCollection(years.map(_seasonal_veg))


# ================================================================
#  CLIMATOLOGY & ANOMALY FUNCTIONS
# ================================================================

def compute_climatology(collection, var_name, baseline_years, min_std=0.01):
    """
    Compute mean & std from baseline (neutral) years.
    """
    baseline = collection.filter(
        ee.Filter.inList('year', ee.List(baseline_years))
    )
    clim_mean = baseline.select(var_name).mean().rename(f'{var_name}_clim_mean')
    clim_std  = baseline.select(var_name).reduce(ee.Reducer.stdDev()).rename(f'{var_name}_clim_std')
    clim_std  = clim_std.max(ee.Image(min_std))
    return clim_mean, clim_std


def compute_anomalies(collection, var_name, clim_mean, clim_std):
    """
    Compute anomaly (var - clim_mean) and standardized anomaly z_score.
    """
    def _add_anomaly(img):
        raw = img.select(var_name)
        anom = raw.subtract(clim_mean).rename(f'{var_name}_anomaly')
        z    = anom.divide(clim_std).rename(f'{var_name}_zscore')
        return img.addBands(anom).addBands(z)

    return collection.map(_add_anomaly)


def enso_composite(anomaly_collection, band, years):
    """
    Compute mean composite for specified years.
    """
    return (anomaly_collection
            .filter(ee.Filter.inList('year', ee.List(years)))
            .select(band)
            .mean()
            .rename(band))


def per_event_veg(collection, var_name, years, aoi, scale=2000):
    """
    Compute provincial mean anomaly and z-score for each individual year.
    """
    results = []
    anom_band = f'{var_name}_anomaly'
    z_band = f'{var_name}_zscore'

    for year in years:
        img = collection.filter(ee.Filter.eq('year', year)).first()
        stats = img.select([anom_band, z_band]).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi.geometry(),
            scale=scale,
            maxPixels=1e10,
        ).getInfo()
        results.append({
            'year': year,
            'intensity': ENSO_INTENSITY.get(year, '--'),
            'iod_positive': 'Yes' if year in IOD_POSITIVE else 'No',
            'anomaly': round(stats.get(anom_band, 0), 4),
            'z_score': round(stats.get(z_band, 0), 3),
        })
    return results


# ================================================================
#  MAIN PIPELINE
# ================================================================

def main():
    print()
    print('=' * 65)
    print('   MILESTONE 4: VEGETATION RESPONSE ATLAS')
    print('   East Java NDVI, EVI & NDMI Response to El Nino')
    print('   ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
    print('=' * 65)

    ee.Initialize()
    print('\n[OK] Google Earth Engine initialized')

    aoi = get_east_java()
    aoi_geom = aoi.geometry()
    print('[OK] Study area: Jawa Timur (East Java)')

    # ----------------------------------------------------------
    # Step 1: Building Seasonal Vegetation Collections (2001-2025)
    # ----------------------------------------------------------
    print('\n--- Step 1: Building Vegetation Collections (2001-2025) ---')
    veg_jja_col = build_seasonal_veg_collection(JJA, START_YEAR, END_YEAR, aoi_geom)
    veg_son_col = build_seasonal_veg_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    print('  [OK] MODIS Terra 1 km vegetation collections built (JJA and SON)')

    # Baseline Climatologies (neutral years)
    print(f'  Computing baseline climatology from neutral years {NEUTRAL}...')
    ndvi_jja_mean, ndvi_jja_std = compute_climatology(veg_jja_col, 'ndvi', NEUTRAL)
    ndvi_son_mean, ndvi_son_std = compute_climatology(veg_son_col, 'ndvi', NEUTRAL)

    evi_jja_mean, evi_jja_std = compute_climatology(veg_jja_col, 'evi', NEUTRAL)
    evi_son_mean, evi_son_std = compute_climatology(veg_son_col, 'evi', NEUTRAL)

    ndmi_jja_mean, ndmi_jja_std = compute_climatology(veg_jja_col, 'ndmi', NEUTRAL)
    ndmi_son_mean, ndmi_son_std = compute_climatology(veg_son_col, 'ndmi', NEUTRAL)

    # Compute anomalies
    jja_anom_col = compute_anomalies(veg_jja_col, 'ndvi', ndvi_jja_mean, ndvi_jja_std)
    jja_anom_col = compute_anomalies(jja_anom_col, 'evi',  evi_jja_mean,  evi_jja_std)
    jja_anom_col = compute_anomalies(jja_anom_col, 'ndmi', ndmi_jja_mean, ndmi_jja_std)

    son_anom_col = compute_anomalies(veg_son_col, 'ndvi', ndvi_son_mean, ndvi_son_std)
    son_anom_col = compute_anomalies(son_anom_col, 'evi',  evi_son_mean,  evi_son_std)
    son_anom_col = compute_anomalies(son_anom_col, 'ndmi', ndmi_son_mean, ndmi_son_std)
    print('  [OK] NDVI, EVI, and NDMI anomalies & z-scores computed')

    # Provincial baseline means
    def get_mean(img, scale=2000):
        val = img.reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi_geom, scale=scale, maxPixels=1e10).getInfo()
        return list(val.values())[0] if val else 0.0

    ndvi_jja_clim = get_mean(ndvi_jja_mean)
    ndvi_son_clim = get_mean(ndvi_son_mean)
    evi_jja_clim  = get_mean(evi_jja_mean)
    evi_son_clim  = get_mean(evi_son_mean)
    ndmi_jja_clim = get_mean(ndmi_jja_mean)
    ndmi_son_clim = get_mean(ndmi_son_mean)

    print(f'    JJA Baselines: NDVI={ndvi_jja_clim:.3f}, EVI={evi_jja_clim:.3f}, NDMI={ndmi_jja_clim:.3f}')
    print(f'    SON Baselines: NDVI={ndvi_son_clim:.3f}, EVI={evi_son_clim:.3f}, NDMI={ndmi_son_clim:.3f}')

    # ----------------------------------------------------------
    # Step 2: Composites Creation
    # ----------------------------------------------------------
    print('\n--- Step 2: Creating Vegetation Response Composites ---')
    composites = {}

    # NDVI composites
    composites['ndvi_jja_elnino_anom']     = enso_composite(jja_anom_col, 'ndvi_anomaly', EL_NINO_ALL)
    composites['ndvi_jja_elnino_z']        = enso_composite(jja_anom_col, 'ndvi_zscore',  EL_NINO_ALL)
    composites['ndvi_son_elnino_anom']     = enso_composite(son_anom_col, 'ndvi_anomaly', EL_NINO_ALL)
    composites['ndvi_son_elnino_z']        = enso_composite(son_anom_col, 'ndvi_zscore',  EL_NINO_ALL)

    composites['ndvi_son_elnino_only_anom'] = enso_composite(son_anom_col, 'ndvi_anomaly', EL_NINO_ONLY)
    composites['ndvi_son_elnino_iod_anom']  = enso_composite(son_anom_col, 'ndvi_anomaly', EL_NINO_IOD)
    composites['ndvi_son_lanina_anom']      = enso_composite(son_anom_col, 'ndvi_anomaly', LA_NINA)

    # EVI composites
    composites['evi_son_elnino_anom']      = enso_composite(son_anom_col, 'evi_anomaly',  EL_NINO_ALL)
    composites['evi_son_elnino_z']         = enso_composite(son_anom_col, 'evi_zscore',   EL_NINO_ALL)

    # NDMI (Moisture Index) composites
    composites['ndmi_jja_elnino_anom']     = enso_composite(jja_anom_col, 'ndmi_anomaly', EL_NINO_ALL)
    composites['ndmi_son_elnino_anom']     = enso_composite(son_anom_col, 'ndmi_anomaly', EL_NINO_ALL)
    composites['ndmi_son_elnino_z']        = enso_composite(son_anom_col, 'ndmi_zscore',  EL_NINO_ALL)
    composites['ndmi_son_elnino_only_anom'] = enso_composite(son_anom_col, 'ndmi_anomaly', EL_NINO_ONLY)
    composites['ndmi_son_elnino_iod_anom']  = enso_composite(son_anom_col, 'ndmi_anomaly', EL_NINO_IOD)
    composites['ndmi_son_lanina_anom']      = enso_composite(son_anom_col, 'ndmi_anomaly', LA_NINA)

    # ----------------------------------------------------------
    # Step 3: Vegetation Sensitivity Index & Hotspots
    # ----------------------------------------------------------
    print('\n--- Step 3: Computing Vegetation Sensitivity Index (VSI) ---')

    # VSI = - (Z_NDVI_SON + Z_NDMI_SON) / 2
    # Inverted: positive values mean high vegetative stress
    vsi = (composites['ndvi_son_elnino_z'].add(composites['ndmi_son_elnino_z'])) \
          .multiply(-0.5).rename('vegetation_sensitivity_index')
    composites['vsi_elnino'] = vsi

    # Canopy stress hotspot: Z_NDVI < -0.5 AND Z_NDMI < -0.5
    hotspot_veg = (composites['ndvi_son_elnino_z'].lt(-0.5)
                   .And(composites['ndmi_son_elnino_z'].lt(-0.5))
                   .rename('vegetation_drought_hotspot'))
    composites['hotspot_veg'] = hotspot_veg
    print('  [OK] VSI and Canopy Stress Hotspots created')

    # ----------------------------------------------------------
    # Step 4: Spatial Statistics Calculation
    # ----------------------------------------------------------
    print('\n--- Step 4: Calculating Provincial Spatial Statistics ---')

    stats_dict = {
        'ndvi_jja_elnino_anom': get_mean(composites['ndvi_jja_elnino_anom']),
        'ndvi_jja_elnino_z':    get_mean(composites['ndvi_jja_elnino_z']),
        'ndvi_son_elnino_anom': get_mean(composites['ndvi_son_elnino_anom']),
        'ndvi_son_elnino_z':    get_mean(composites['ndvi_son_elnino_z']),
        'ndvi_son_pure_anom':   get_mean(composites['ndvi_son_elnino_only_anom']),
        'ndvi_son_iod_anom':    get_mean(composites['ndvi_son_elnino_iod_anom']),
        'ndvi_son_lanina_anom': get_mean(composites['ndvi_son_lanina_anom']),

        'evi_son_elnino_anom':  get_mean(composites['evi_son_elnino_anom']),
        'evi_son_elnino_z':     get_mean(composites['evi_son_elnino_z']),

        'ndmi_jja_elnino_anom': get_mean(composites['ndmi_jja_elnino_anom']),
        'ndmi_son_elnino_anom': get_mean(composites['ndmi_son_elnino_anom']),
        'ndmi_son_elnino_z':    get_mean(composites['ndmi_son_elnino_z']),
        'ndmi_son_pure_anom':   get_mean(composites['ndmi_son_elnino_only_anom']),
        'ndmi_son_iod_anom':    get_mean(composites['ndmi_son_elnino_iod_anom']),
        'ndmi_son_lanina_anom': get_mean(composites['ndmi_son_lanina_anom']),

        'vsi_elnino_mean':      get_mean(composites['vsi_elnino']),
    }

    print('\n  NDVI (Greenness) Response:')
    print(f'    JJA El Nino NDVI Anom:   {stats_dict["ndvi_jja_elnino_anom"]:+.4f}  (Z = {stats_dict["ndvi_jja_elnino_z"]:+.2f})')
    print(f'    SON El Nino NDVI Anom:   {stats_dict["ndvi_son_elnino_anom"]:+.4f}  (Z = {stats_dict["ndvi_son_elnino_z"]:+.2f})')
    print(f'    SON Pure El Nino Anom:   {stats_dict["ndvi_son_pure_anom"]:+.4f}')
    print(f'    SON El Nino+IOD+ Anom:   {stats_dict["ndvi_son_iod_anom"]:+.4f}')
    print(f'    SON La Nina NDVI Anom:   {stats_dict["ndvi_son_lanina_anom"]:+.4f}')

    print('\n  EVI (Enhanced Vegetation) Response:')
    print(f'    SON El Nino EVI Anom:    {stats_dict["evi_son_elnino_anom"]:+.4f}  (Z = {stats_dict["evi_son_elnino_z"]:+.2f})')

    print('\n  NDMI (Canopy Moisture) Response:')
    print(f'    JJA El Nino NDMI Anom:   {stats_dict["ndmi_jja_elnino_anom"]:+.4f}')
    print(f'    SON El Nino NDMI Anom:   {stats_dict["ndmi_son_elnino_anom"]:+.4f}  (Z = {stats_dict["ndmi_son_elnino_z"]:+.2f})')
    print(f'    SON Pure El Nino Anom:   {stats_dict["ndmi_son_pure_anom"]:+.4f}')
    print(f'    SON El Nino+IOD+ Anom:   {stats_dict["ndmi_son_iod_anom"]:+.4f}')
    print(f'    SON La Nina NDMI Anom:   {stats_dict["ndmi_son_lanina_anom"]:+.4f}')

    print(f'\n  Vegetation Sensitivity Index (VSI): {stats_dict["vsi_elnino_mean"]:+.2f}')

    # Per-event table
    print('\n--- Per-Event Vegetation Response ---')
    ndvi_events_son = per_event_veg(son_anom_col, 'ndvi', EL_NINO_ALL, aoi)
    ndmi_events_son = per_event_veg(son_anom_col, 'ndmi', EL_NINO_ALL, aoi)
    evi_events_son  = per_event_veg(son_anom_col, 'evi',  EL_NINO_ALL, aoi)

    print(f'\n  {"Year":<6} {"Intensity":<14} {"IOD+":<5} '
          f'{"NDVI_SON":>10} {"Z_NDVI":>8} {"NDMI_SON":>10} {"Z_NDMI":>8} {"EVI_SON":>10}')
    print(f'  {"-"*6} {"-"*14} {"-"*5} {"-"*10} {"-"*8} {"-"*10} {"-"*8} {"-"*10}')
    for i in range(len(EL_NINO_ALL)):
        e_ndvi = ndvi_events_son[i]
        e_ndmi = ndmi_events_son[i]
        e_evi  = evi_events_son[i]
        print(f'  {e_ndvi["year"]:<6} {e_ndvi["intensity"]:<14} {e_ndvi["iod_positive"]:<5} '
              f'{e_ndvi["anomaly"]:>+10.4f} {e_ndvi["z_score"]:>+8.2f} '
              f'{e_ndmi["anomaly"]:>+10.4f} {e_ndmi["z_score"]:>+8.2f} '
              f'{e_evi["anomaly"]:>+10.4f}')

    # ----------------------------------------------------------
    # Step 5: Save Statistics JSON
    # ----------------------------------------------------------
    output_dir = os.path.join(PROJECT_DIR, 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    summary_json = {
        'generated': datetime.now().isoformat(),
        'baseline_years': NEUTRAL,
        'ndvi_baseline_mean_jja': ndvi_jja_clim,
        'ndvi_baseline_mean_son': ndvi_son_clim,
        'evi_baseline_mean_jja': evi_jja_clim,
        'evi_baseline_mean_son': evi_son_clim,
        'ndmi_baseline_mean_jja': ndmi_jja_clim,
        'ndmi_baseline_mean_son': ndmi_son_clim,
        'provincial_stats': stats_dict,
        'ndvi_per_event_son': ndvi_events_son,
        'ndmi_per_event_son': ndmi_events_son,
        'evi_per_event_son': evi_events_son,
    }
    stats_path = os.path.join(output_dir, 'm4_vegetation_statistics.json')
    with open(stats_path, 'w') as f:
        json.dump(summary_json, f, indent=2)
    print(f'\n[OK] Vegetation statistics saved -> {stats_path}')

    # ----------------------------------------------------------
    # Step 6: Export to Google Drive & Local Duplication
    # ----------------------------------------------------------
    print(f'\n--- Step 6: Exporting to Drive & Downloading Local Duplicates ---')

    exports = {
        # NDVI
        'M4_JJA_NDVI_ElNino_anomaly':        composites['ndvi_jja_elnino_anom'],
        'M4_SON_NDVI_ElNino_anomaly':        composites['ndvi_son_elnino_anom'],
        'M4_SON_NDVI_ElNino_zscore':         composites['ndvi_son_elnino_z'],
        'M4_SON_NDVI_ElNinoOnly_anomaly':    composites['ndvi_son_elnino_only_anom'],
        'M4_SON_NDVI_ElNinoIOD_anomaly':     composites['ndvi_son_elnino_iod_anom'],
        'M4_SON_NDVI_LaNina_anomaly':        composites['ndvi_son_lanina_anom'],

        # EVI
        'M4_SON_EVI_ElNino_anomaly':         composites['evi_son_elnino_anom'],
        'M4_SON_EVI_ElNino_zscore':          composites['evi_son_elnino_z'],

        # NDMI (Canopy Moisture)
        'M4_JJA_NDMI_ElNino_anomaly':        composites['ndmi_jja_elnino_anom'],
        'M4_SON_NDMI_ElNino_anomaly':        composites['ndmi_son_elnino_anom'],
        'M4_SON_NDMI_ElNino_zscore':         composites['ndmi_son_elnino_z'],
        'M4_SON_NDMI_ElNinoOnly_anomaly':    composites['ndmi_son_elnino_only_anom'],
        'M4_SON_NDMI_ElNinoIOD_anomaly':     composites['ndmi_son_elnino_iod_anom'],
        'M4_SON_NDMI_LaNina_anomaly':        composites['ndmi_son_lanina_anom'],

        # Sensitivity & Hotspots
        'M4_SON_Vegetation_Sensitivity_Index': composites['vsi_elnino'],
        'M4_SON_Vegetation_Drought_Hotspot':   composites['hotspot_veg'],
    }

    # Start Drive exports
    drive_tasks = []
    for desc, img in exports.items():
        task = export_image(img, desc, aoi, scale=1000)
        drive_tasks.append(task)
        print(f'  [Drive Task] {desc}')

    # Download local duplicates
    m4_local_dir = os.path.join(output_dir, 'geotiffs', 'm4')
    os.makedirs(m4_local_dir, exist_ok=True)
    print(f'\n  Downloading local GeoTIFF duplicates to {m4_local_dir}...')

    for desc, img in exports.items():
        dst = os.path.join(m4_local_dir, f"{desc}.tif")
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            print(f'  [EXISTS] {desc}.tif ({os.path.getsize(dst)/1024:.1f} KB)')
            continue
        try:
            print(f'  [DOWNLOAD] {desc}...', end=' ', flush=True)
            t0 = time.time()
            download_image_local(img, desc, aoi_geom, m4_local_dir, scale=1000)
            dt = time.time() - t0
            print(f'OK ({os.path.getsize(dst)/1024:.1f} KB in {dt:.1f}s)')
        except Exception as e:
            print(f'FAILED: {e}')

    print('\n' + '=' * 65)
    print('   MILESTONE 4 COMPLETE')
    print('=' * 65)


if __name__ == '__main__':
    main()
