"""
Milestone 3: Physical Response (Soil Moisture and LST)
=====================================================
Phase 3 -- Soil-Moisture Response (ERA5-Land)
Phase 4 -- Thermal Response (MODIS Daytime LST)

Computes and exports:
  1. Seasonal root-zone soil moisture (SM) climatology (JJA and SON)
  2. Seasonal MODIS Daytime LST climatology (JJA and SON)
  3. El Nino SM anomaly composites (m3/m3 and z-score)
  4. El Nino LST anomaly composites (deg C and z-score)
  5. La Nina physical response composites for contrast
  6. Pure El Nino vs Compound (El Nino + IOD+) physical response
  7. Physical sensitivity metrics:
     - Hydrologic response ratio (delta_SM / delta_P)
     - Evaporative cooling decoupling (delta_LST / delta_SM)
     - High Physical Sensitivity Index (combined low SM + high LST)
  8. Per-event physical statistics for all 8 El Nino events
  9. Export GeoTIFFs to Google Drive (folder: EastJava_ElNino_Sensitivity)

Output -> Deliverable B components: Soil Moisture and Thermal Sensitivity Surfaces

Usage:
  python scripts/m3_physical_response.py
"""

import os
import sys
import json
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
    ERA5_LAND, MODIS_LST,
    EXPORT_SCALE, DRIVE_FOLDER,
    export_image, compute_region_stats,
)


# ================================================================
#  COLLECTION BUILDERS
# ================================================================

def build_seasonal_sm_collection(season_months, start_year, end_year, aoi=None):
    """
    Build annual seasonal root-zone soil moisture collection (m3/m3)
    from ERA5-Land monthly aggregation.
    Root zone (0-28 cm) weighted: (7*Layer1 + 21*Layer2) / 28.
    """
    era5 = ee.ImageCollection(ERA5_LAND)
    if aoi is not None:
        era5 = era5.filterBounds(aoi)

    first_month = season_months[0]
    last_month  = season_months[-1]
    years = ee.List.sequence(start_year, end_year)

    def _seasonal_sm(year):
        year  = ee.Number(year)
        start = ee.Date.fromYMD(year, first_month, 1)
        end   = ee.Date.fromYMD(year, last_month, 1).advance(1, 'month')

        season_imgs = era5.filterDate(start, end)
        def _calc_rootzone(img):
            l1 = img.select('volumetric_soil_water_layer_1')
            l2 = img.select('volumetric_soil_water_layer_2')
            # Weighted average 0-28 cm depth
            rz = l1.multiply(7.0).add(l2.multiply(21.0)).divide(28.0).rename('sm_rootzone')
            return rz

        sm_mean = season_imgs.map(_calc_rootzone).mean().rename('sm')
        return sm_mean.set({
            'year': year,
            'system:time_start': start.millis(),
        })

    return ee.ImageCollection(years.map(_seasonal_sm))


def build_seasonal_lst_collection(season_months, start_year, end_year, aoi=None):
    """
    Build annual seasonal daytime LST collection (deg C)
    from MODIS Terra MOD11A2 8-day 1 km composite.
    Formula: LST_Day_1km * 0.02 - 273.15.
    """
    modis = ee.ImageCollection(MODIS_LST)
    if aoi is not None:
        modis = modis.filterBounds(aoi)

    first_month = season_months[0]
    last_month  = season_months[-1]
    years = ee.List.sequence(start_year, end_year)

    def _seasonal_lst(year):
        year  = ee.Number(year)
        start = ee.Date.fromYMD(year, first_month, 1)
        end   = ee.Date.fromYMD(year, last_month, 1).advance(1, 'month')

        season_imgs = modis.filterDate(start, end)
        raw = season_imgs.select('LST_Day_1km').mean()
        valid = raw.gt(7500).And(raw.lt(20000))
        celsius = raw.multiply(0.02).subtract(273.15).updateMask(valid).rename('lst')
        return celsius.set({
            'year': year,
            'system:time_start': start.millis(),
        })

    return ee.ImageCollection(years.map(_seasonal_lst))


# ================================================================
#  CLIMATOLOGY & ANOMALY FUNCTIONS
# ================================================================

def compute_climatology(collection, var_name, baseline_years, min_std=0.001):
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


def per_event_physical(collection, var_name, years, aoi, scale=5000):
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
    print('   MILESTONE 3: PHYSICAL RESPONSE ATLAS')
    print('   East Java Soil Moisture & LST Response to El Nino')
    print('   ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
    print('=' * 65)

    ee.Initialize()
    print('\n[OK] Google Earth Engine initialized')

    aoi = get_east_java()
    aoi_geom = aoi.geometry()
    print('[OK] Study area: Jawa Timur (East Java)')

    # ----------------------------------------------------------
    # Step 1: Soil Moisture Processing (ERA5-Land)
    # ----------------------------------------------------------
    print('\n--- Step 1: Building Soil Moisture Collections (2001-2025) ---')
    sm_jja_col = build_seasonal_sm_collection(JJA, START_YEAR, END_YEAR, aoi_geom)
    sm_son_col = build_seasonal_sm_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    print('  [OK] ERA5-Land root-zone SM collections built (JJA and SON)')

    # Baseline climatology (neutral years)
    print(f'  Computing SM climatology from neutral years {NEUTRAL}...')
    sm_jja_mean, sm_jja_std = compute_climatology(sm_jja_col, 'sm', NEUTRAL, min_std=0.005)
    sm_son_mean, sm_son_std = compute_climatology(sm_son_col, 'sm', NEUTRAL, min_std=0.005)

    sm_jja_anom_col = compute_anomalies(sm_jja_col, 'sm', sm_jja_mean, sm_jja_std)
    sm_son_anom_col = compute_anomalies(sm_son_col, 'sm', sm_son_mean, sm_son_std)
    print('  [OK] SM anomalies and z-scores computed')

    # Provincial baseline mean
    sm_jja_clim_val = sm_jja_mean.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi_geom, scale=11132, maxPixels=1e10
    ).getInfo().get('sm_clim_mean', 0)
    sm_son_clim_val = sm_son_mean.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi_geom, scale=11132, maxPixels=1e10
    ).getInfo().get('sm_clim_mean', 0)
    print(f'    JJA SM baseline mean: {sm_jja_clim_val:.3f} m3/m3')
    print(f'    SON SM baseline mean: {sm_son_clim_val:.3f} m3/m3')

    # ----------------------------------------------------------
    # Step 2: Land Surface Temperature Processing (MODIS)
    # ----------------------------------------------------------
    print('\n--- Step 2: Building MODIS Daytime LST Collections (2001-2025) ---')
    lst_jja_col = build_seasonal_lst_collection(JJA, START_YEAR, END_YEAR, aoi_geom)
    lst_son_col = build_seasonal_lst_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    print('  [OK] MODIS Terra 1 km Daytime LST collections built (JJA and SON)')

    # Baseline climatology (neutral years)
    print(f'  Computing LST climatology from neutral years {NEUTRAL}...')
    lst_jja_mean, lst_jja_std = compute_climatology(lst_jja_col, 'lst', NEUTRAL, min_std=0.1)
    lst_son_mean, lst_son_std = compute_climatology(lst_son_col, 'lst', NEUTRAL, min_std=0.1)

    lst_jja_anom_col = compute_anomalies(lst_jja_col, 'lst', lst_jja_mean, lst_jja_std)
    lst_son_anom_col = compute_anomalies(lst_son_col, 'lst', lst_son_mean, lst_son_std)
    print('  [OK] LST anomalies and z-scores computed')

    # Provincial baseline mean
    lst_jja_clim_val = lst_jja_mean.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi_geom, scale=2000, maxPixels=1e10
    ).getInfo().get('lst_clim_mean', 0)
    lst_son_clim_val = lst_son_mean.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi_geom, scale=2000, maxPixels=1e10
    ).getInfo().get('lst_clim_mean', 0)
    print(f'    JJA LST baseline mean: {lst_jja_clim_val:.1f} deg C')
    print(f'    SON LST baseline mean: {lst_son_clim_val:.1f} deg C')

    # ----------------------------------------------------------
    # Step 3: Composites Creation
    # ----------------------------------------------------------
    print('\n--- Step 3: Creating Physical Response Composites ---')
    composites = {}

    # Soil moisture composites
    composites['sm_jja_elnino_anom']     = enso_composite(sm_jja_anom_col, 'sm_anomaly', EL_NINO_ALL)
    composites['sm_jja_elnino_z']        = enso_composite(sm_jja_anom_col, 'sm_zscore',  EL_NINO_ALL)
    composites['sm_son_elnino_anom']     = enso_composite(sm_son_anom_col, 'sm_anomaly', EL_NINO_ALL)
    composites['sm_son_elnino_z']        = enso_composite(sm_son_anom_col, 'sm_zscore',  EL_NINO_ALL)

    composites['sm_son_elnino_only_anom'] = enso_composite(sm_son_anom_col, 'sm_anomaly', EL_NINO_ONLY)
    composites['sm_son_elnino_iod_anom']  = enso_composite(sm_son_anom_col, 'sm_anomaly', EL_NINO_IOD)
    composites['sm_son_lanina_anom']      = enso_composite(sm_son_anom_col, 'sm_anomaly', LA_NINA)

    # LST composites
    composites['lst_jja_elnino_anom']     = enso_composite(lst_jja_anom_col, 'lst_anomaly', EL_NINO_ALL)
    composites['lst_jja_elnino_z']        = enso_composite(lst_jja_anom_col, 'lst_zscore',  EL_NINO_ALL)
    composites['lst_son_elnino_anom']     = enso_composite(lst_son_anom_col, 'lst_anomaly', EL_NINO_ALL)
    composites['lst_son_elnino_z']        = enso_composite(lst_son_anom_col, 'lst_zscore',  EL_NINO_ALL)

    composites['lst_son_elnino_only_anom'] = enso_composite(lst_son_anom_col, 'lst_anomaly', EL_NINO_ONLY)
    composites['lst_son_elnino_iod_anom']  = enso_composite(lst_son_anom_col, 'lst_anomaly', EL_NINO_IOD)
    composites['lst_son_lanina_anom']      = enso_composite(lst_son_anom_col, 'lst_anomaly', LA_NINA)

    # ----------------------------------------------------------
    # Step 4: Physical Coupling & High Physical Sensitivity Index
    # ----------------------------------------------------------
    print('\n--- Step 4: Computing Coupling and High Sensitivity Index ---')

    # Physical Sensitivity Index (PSI):
    # Standardized LST surge minus Standardized Soil Moisture (since SM drops during drought, -Z_SM is positive)
    # PSI = Z_LST_SON - Z_SM_SON
    # High PSI = severe atmospheric heating combined with severe soil desiccation
    psi_elnino = (composites['lst_son_elnino_z']
                  .subtract(composites['sm_son_elnino_z'])
                  .rename('physical_sensitivity_index'))
    composites['psi_elnino'] = psi_elnino

    # Binary hotspot: Z_LST > 0.5 AND Z_SM < -0.5
    hotspot_mask = (composites['lst_son_elnino_z'].gt(0.5)
                    .And(composites['sm_son_elnino_z'].lt(-0.5))
                    .rename('high_physical_sensitivity_zone'))
    composites['high_sensitivity_zone'] = hotspot_mask

    print('  [OK] Physical Sensitivity Index (PSI) & Hotspot zone created')

    # ----------------------------------------------------------
    # Step 5: Spatial Statistics Calculation
    # ----------------------------------------------------------
    print('\n--- Step 5: Calculating Provincial Spatial Statistics ---')

    def calc_mean(img, scale=5000):
        val = img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi_geom,
            scale=scale,
            maxPixels=1e10
        ).getInfo()
        return list(val.values())[0] if val else 0.0

    stats_dict = {
        'sm_jja_elnino_anom':  calc_mean(composites['sm_jja_elnino_anom'], scale=11132),
        'sm_jja_elnino_z':     calc_mean(composites['sm_jja_elnino_z'], scale=11132),
        'sm_son_elnino_anom':  calc_mean(composites['sm_son_elnino_anom'], scale=11132),
        'sm_son_elnino_z':     calc_mean(composites['sm_son_elnino_z'], scale=11132),
        'sm_son_pure_anom':    calc_mean(composites['sm_son_elnino_only_anom'], scale=11132),
        'sm_son_iod_anom':     calc_mean(composites['sm_son_elnino_iod_anom'], scale=11132),
        'sm_son_lanina_anom':  calc_mean(composites['sm_son_lanina_anom'], scale=11132),

        'lst_jja_elnino_anom': calc_mean(composites['lst_jja_elnino_anom'], scale=2000),
        'lst_jja_elnino_z':    calc_mean(composites['lst_jja_elnino_z'], scale=2000),
        'lst_son_elnino_anom': calc_mean(composites['lst_son_elnino_anom'], scale=2000),
        'lst_son_elnino_z':    calc_mean(composites['lst_son_elnino_z'], scale=2000),
        'lst_son_pure_anom':   calc_mean(composites['lst_son_elnino_only_anom'], scale=2000),
        'lst_son_iod_anom':    calc_mean(composites['lst_son_elnino_iod_anom'], scale=2000),
        'lst_son_lanina_anom': calc_mean(composites['lst_son_lanina_anom'], scale=2000),

        'psi_elnino_mean':     calc_mean(composites['psi_elnino'], scale=2000),
    }

    print('\n  Soil Moisture Response:')
    print(f'    JJA El Nino SM Anomaly:  {stats_dict["sm_jja_elnino_anom"]:+.4f} m3/m3  (Z = {stats_dict["sm_jja_elnino_z"]:+.2f})')
    print(f'    SON El Nino SM Anomaly:  {stats_dict["sm_son_elnino_anom"]:+.4f} m3/m3  (Z = {stats_dict["sm_son_elnino_z"]:+.2f})')
    print(f'    SON Pure El Nino Anom:   {stats_dict["sm_son_pure_anom"]:+.4f} m3/m3')
    print(f'    SON El Nino+IOD+ Anom:   {stats_dict["sm_son_iod_anom"]:+.4f} m3/m3')
    print(f'    SON La Nina SM Anomaly:  {stats_dict["sm_son_lanina_anom"]:+.4f} m3/m3')

    print('\n  Land Surface Temperature Response:')
    print(f'    JJA El Nino LST Anomaly: {stats_dict["lst_jja_elnino_anom"]:+.2f} deg C  (Z = {stats_dict["lst_jja_elnino_z"]:+.2f})')
    print(f'    SON El Nino LST Anomaly: {stats_dict["lst_son_elnino_anom"]:+.2f} deg C  (Z = {stats_dict["lst_son_elnino_z"]:+.2f})')
    print(f'    SON Pure El Nino Anom:   {stats_dict["lst_son_pure_anom"]:+.2f} deg C')
    print(f'    SON El Nino+IOD+ Anom:   {stats_dict["lst_son_iod_anom"]:+.2f} deg C')
    print(f'    SON La Nina LST Anomaly: {stats_dict["lst_son_lanina_anom"]:+.2f} deg C')

    print(f'\n  Physical Sensitivity Index (PSI = Z_LST - Z_SM): {stats_dict["psi_elnino_mean"]:+.2f}')

    # Per-event tables
    print('\n--- Per-Event Physical Response ---')
    sm_events_jja = per_event_physical(sm_jja_anom_col, 'sm', EL_NINO_ALL, aoi, scale=11132)
    sm_events_son = per_event_physical(sm_son_anom_col, 'sm', EL_NINO_ALL, aoi, scale=11132)
    lst_events_jja = per_event_physical(lst_jja_anom_col, 'lst', EL_NINO_ALL, aoi, scale=3000)
    lst_events_son = per_event_physical(lst_son_anom_col, 'lst', EL_NINO_ALL, aoi, scale=3000)

    print(f'\n  {"Year":<6} {"Intensity":<14} {"IOD+":<5} '
          f'{"SM_SON (m3/m3)":>15} {"Z_SM":>8} {"LST_SON (C)":>13} {"Z_LST":>8}')
    print(f'  {"-"*6} {"-"*14} {"-"*5} {"-"*15} {"-"*8} {"-"*13} {"-"*8}')
    for i in range(len(EL_NINO_ALL)):
        e_sm = sm_events_son[i]
        e_lst = lst_events_son[i]
        print(f'  {e_sm["year"]:<6} {e_sm["intensity"]:<14} {e_sm["iod_positive"]:<5} '
              f'{e_sm["anomaly"]:>+15.4f} {e_sm["z_score"]:>+8.2f} '
              f'{e_lst["anomaly"]:>+13.2f} {e_lst["z_score"]:>+8.2f}')

    # ----------------------------------------------------------
    # Step 6: Save Statistics JSON
    # ----------------------------------------------------------
    output_dir = os.path.join(PROJECT_DIR, 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    summary_json = {
        'generated': datetime.now().isoformat(),
        'baseline_years': NEUTRAL,
        'sm_baseline_mean_jja': sm_jja_clim_val,
        'sm_baseline_mean_son': sm_son_clim_val,
        'lst_baseline_mean_jja_degC': lst_jja_clim_val,
        'lst_baseline_mean_son_degC': lst_son_clim_val,
        'provincial_stats': stats_dict,
        'sm_per_event_jja': sm_events_jja,
        'sm_per_event_son': sm_events_son,
        'lst_per_event_jja': lst_events_jja,
        'lst_per_event_son': lst_events_son,
    }
    stats_path = os.path.join(output_dir, 'm3_physical_statistics.json')
    with open(stats_path, 'w') as f:
        json.dump(summary_json, f, indent=2)
    print(f'\n[OK] Physical statistics saved -> {stats_path}')

    # ----------------------------------------------------------
    # Step 7: Export to Google Drive
    # ----------------------------------------------------------
    print(f'\n--- Step 7: Exporting to Google Drive (folder: {DRIVE_FOLDER}) ---')

    exports = {
        # Soil Moisture
        'M3_JJA_SM_ElNino_anomaly':          composites['sm_jja_elnino_anom'],
        'M3_SON_SM_ElNino_anomaly':          composites['sm_son_elnino_anom'],
        'M3_SON_SM_ElNino_zscore':           composites['sm_son_elnino_z'],
        'M3_SON_SM_ElNinoOnly_anomaly':      composites['sm_son_elnino_only_anom'],
        'M3_SON_SM_ElNinoIOD_anomaly':       composites['sm_son_elnino_iod_anom'],
        'M3_SON_SM_LaNina_anomaly':          composites['sm_son_lanina_anom'],

        # Land Surface Temperature (1 km)
        'M3_JJA_LST_ElNino_anomaly':         composites['lst_jja_elnino_anom'],
        'M3_SON_LST_ElNino_anomaly':         composites['lst_son_elnino_anom'],
        'M3_SON_LST_ElNino_zscore':          composites['lst_son_elnino_z'],
        'M3_SON_LST_ElNinoOnly_anomaly':     composites['lst_son_elnino_only_anom'],
        'M3_SON_LST_ElNinoIOD_anomaly':      composites['lst_son_elnino_iod_anom'],
        'M3_SON_LST_LaNina_anomaly':         composites['lst_son_lanina_anom'],

        # Physical Sensitivity & Hotspots
        'M3_SON_Physical_Sensitivity_Index': composites['psi_elnino'],
        'M3_SON_High_Sensitivity_Zone':      composites['high_sensitivity_zone'],
    }

    tasks = []
    for desc, img in exports.items():
        # Choose export scale: 1000m for LST and indices, 5000m for SM
        scale = 1000 if 'LST' in desc or 'Sensitivity' in desc else 5000
        task = export_image(img, desc, aoi, scale=scale)
        tasks.append(task)
        print(f'  [->] Started: {desc} (scale: {scale}m)')

    print(f'\n  {len(tasks)} export tasks started.')
    print(f'  Check progress at: https://code.earthengine.google.com/tasks')

    print('\n' + '=' * 65)
    print('   MILESTONE 3 COMPLETE')
    print('=' * 65)


if __name__ == '__main__':
    main()
