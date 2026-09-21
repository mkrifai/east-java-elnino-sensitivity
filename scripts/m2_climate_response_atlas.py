"""
Milestone 2: Climate Response Atlas
=====================================
Phase 1 -- Climate Characterization
Phase 2 -- ENSO Rainfall Response

Computes and exports:
  1. Baseline seasonal rainfall climatology (JJA & SON)
  2. El Niño composite rainfall anomaly maps (mm & z-score)
  3. La Niña composite for contrast
  4. El Niño-only vs El Niño+IOD+ comparison
  5. Individual El Niño event anomaly maps
  6. Spatial statistics summary

Output -> Deliverable A: East Java ENSO Rainfall Response Map

Usage:
  cd "d:\\My Research\\Portfolio\\2. Mapping the Spatial Sensitivity..."
  python scripts/m2_climate_response_atlas.py
"""

import ee
import os
import sys
import json
from datetime import datetime

# Configure UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# --- Path setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from config import (
    get_east_java, get_east_java_districts,
    START_YEAR, END_YEAR,
    EL_NINO_ALL, EL_NINO_ONLY, EL_NINO_IOD,
    LA_NINA, NEUTRAL, ALL_YEARS,
    ENSO_INTENSITY, IOD_POSITIVE,
    JJA, SON, DRY_SEASON,
    CHIRPS_SCALE, EXPORT_SCALE, DRIVE_FOLDER,
    build_seasonal_collection, export_image, compute_region_stats,
)


# ================================================================
#  CORE ANALYSIS FUNCTIONS
# ================================================================

def compute_climatology(seasonal_collection, baseline_years):
    """
    Compute seasonal climatology (mean & std) from baseline years.

    Parameters
    ----------
    seasonal_collection : ee.ImageCollection
        One image per year with seasonal total rainfall.
    baseline_years : list of int
        Years to use for computing the climatological mean.

    Returns
    -------
    tuple of (ee.Image, ee.Image)
        (clim_mean, clim_std) -- both single-band images.
    """
    baseline = seasonal_collection.filter(
        ee.Filter.inList('year', ee.List(baseline_years))
    )
    clim_mean = baseline.mean().rename('clim_mean')
    clim_std  = baseline.reduce(ee.Reducer.stdDev()).rename('clim_std')
    # Floor std at 1 mm to prevent division by near-zero
    clim_std = clim_std.max(ee.Image(1.0))
    return clim_mean, clim_std


def compute_anomaly_collection(seasonal_collection, clim_mean, clim_std):
    """
    Compute rainfall anomaly (P') and standardized anomaly (Z_P)
    for every year in the collection.

    Returns an ee.ImageCollection with bands:
      - 'precipitation': original seasonal total
      - 'anomaly': P' = P - clim_mean  (mm)
      - 'z_score': Z_P = P' / clim_std  (unitless)
    """
    def _add_anomaly(image):
        anomaly = image.select('precipitation').subtract(clim_mean).rename('anomaly')
        z_score = anomaly.divide(clim_std).rename('z_score')
        return image.addBands(anomaly).addBands(z_score)

    return seasonal_collection.map(_add_anomaly)


def enso_composite(anomaly_collection, years, band='anomaly'):
    """
    Compute mean anomaly composite for a set of years.

    Parameters
    ----------
    anomaly_collection : ee.ImageCollection
        Collection with 'anomaly' and 'z_score' bands.
    years : list of int
        Years to include in the composite.
    band : str
        Band to composite ('anomaly' or 'z_score').

    Returns
    -------
    ee.Image
        Mean composite image.
    """
    return (anomaly_collection
            .filter(ee.Filter.inList('year', ee.List(years)))
            .select(band)
            .mean()
            .rename(band))


def per_event_anomalies(anomaly_collection, years, aoi, scale=None):
    """
    Compute mean anomaly for each individual year over the study area.

    Returns a list of dicts: [{'year': YYYY, 'anomaly_mm': X, 'z_score': Z}, ...]
    """
    if scale is None:
        scale = CHIRPS_SCALE
    results = []
    for year in years:
        img = anomaly_collection.filter(ee.Filter.eq('year', year)).first()
        stats = img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi.geometry(),
            scale=scale,
            maxPixels=1e10,
        ).getInfo()
        results.append({
            'year': year,
            'intensity': ENSO_INTENSITY.get(year, '--'),
            'iod_positive': 'Yes' if year in IOD_POSITIVE else 'No',
            'anomaly_mm': round(stats.get('anomaly', 0), 1),
            'z_score': round(stats.get('z_score', 0), 2),
        })
    return results


# ================================================================
#  PRINTING / REPORTING
# ================================================================

def print_header():
    print()
    print('=' * 65)
    print('   MILESTONE 2: CLIMATE RESPONSE ATLAS')
    print('   East Java El Niño Rainfall Response')
    print('   ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
    print('=' * 65)


def print_classification():
    print('\n--- ENSO Classification (Dry-Season Year) ---')
    print(f'  El Niño-only  ({len(EL_NINO_ONLY)}): {EL_NINO_ONLY}')
    print(f'  El Niño+IOD+  ({len(EL_NINO_IOD)}):  {EL_NINO_IOD}')
    print(f'  La Niña       ({len(LA_NINA)}): {LA_NINA}')
    print(f'  Neutral       ({len(NEUTRAL)}):  {NEUTRAL}')


def print_composite_stats(label, image, aoi):
    stats = compute_region_stats(image, aoi, scale=CHIRPS_SCALE)
    keys = list(stats.keys())
    # Extract values robustly
    mean_val = next((stats[k] for k in keys if 'mean' in k.lower()), None)
    min_val  = next((stats[k] for k in keys if 'min' in k.lower()), None)
    max_val  = next((stats[k] for k in keys if 'max' in k.lower()), None)
    std_val  = next((stats[k] for k in keys if 'stddev' in k.lower()), None)

    def fmt(v):
        return f'{v:+.1f}' if v is not None else 'N/A'

    print(f'  {label:30s}  mean={fmt(mean_val)}  '
          f'min={fmt(min_val)}  max={fmt(max_val)}  '
          f'std={fmt(std_val) if std_val else "N/A"}')


def print_event_table(events, season_label):
    print(f'\n  --- Per-Event {season_label} Anomaly ---')
    print(f'  {"Year":<6} {"Intensity":<14} {"IOD+":<5} '
          f'{"Anomaly (mm)":>13} {"Z-score":>8}')
    print(f'  {"-"*6} {"-"*14} {"-"*5} {"-"*13} {"-"*8}')
    for e in events:
        print(f'  {e["year"]:<6} {e["intensity"]:<14} {e["iod_positive"]:<5} '
              f'{e["anomaly_mm"]:>+13.1f} {e["z_score"]:>+8.2f}')


# ================================================================
#  EXPORT FUNCTIONS
# ================================================================

def run_exports(exports_dict, aoi):
    """
    Start all GEE export tasks.

    Parameters
    ----------
    exports_dict : dict
        {description: ee.Image, ...}
    aoi : ee.FeatureCollection

    Returns list of started tasks.
    """
    tasks = []
    for desc, image in exports_dict.items():
        task = export_image(image, desc, aoi, scale=CHIRPS_SCALE)
        tasks.append(task)
        print(f'  [->] Started: {desc}')
    return tasks


# ================================================================
#  MAIN PIPELINE
# ================================================================

def main():
    print_header()

    # ----------------------------------------------------------
    # Initialize GEE
    # ----------------------------------------------------------
    try:
        ee.Initialize()
    except Exception:
        ee.Authenticate()
        ee.Initialize()
    print('\n[OK] Google Earth Engine initialized')

    # ----------------------------------------------------------
    # Study area
    # ----------------------------------------------------------
    aoi = get_east_java()
    print('[OK] Study area: Jawa Timur (East Java)')

    # ----------------------------------------------------------
    # Phase 1: Climate Characterization
    # ----------------------------------------------------------
    print_classification()

    # ----------------------------------------------------------
    # Phase 2: Build seasonal rainfall collections
    # ----------------------------------------------------------
    print('\n--- Step 1: Building seasonal rainfall collections (2001-2025) ---')
    print('  Aggregating CHIRPS daily -> seasonal totals...')

    aoi_geom = aoi.geometry()
    jja_collection = build_seasonal_collection(JJA, START_YEAR, END_YEAR, aoi_geom)
    son_collection = build_seasonal_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    dry_collection = build_seasonal_collection(DRY_SEASON, START_YEAR, END_YEAR, aoi_geom)

    print('  [OK] JJA collection (Jun-Aug)')
    print('  [OK] SON collection (Sep-Nov)')
    print('  [OK] JJASON collection (Jun-Nov, full dry season)')

    # ----------------------------------------------------------
    # Step 2: Baseline climatology from neutral years
    # ----------------------------------------------------------
    print(f'\n--- Step 2: Computing baseline climatology (neutral years: {NEUTRAL}) ---')

    jja_clim_mean, jja_clim_std = compute_climatology(jja_collection, NEUTRAL)
    son_clim_mean, son_clim_std = compute_climatology(son_collection, NEUTRAL)
    dry_clim_mean, dry_clim_std = compute_climatology(dry_collection, NEUTRAL)

    print('  [OK] JJA climatology computed')
    print('  [OK] SON climatology computed')
    print('  [OK] JJASON climatology computed')

    # Print climatological means
    print('\n  Baseline rainfall (neutral-year mean):')
    jja_stats = jja_clim_mean.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi_geom,
        scale=CHIRPS_SCALE, maxPixels=1e10
    ).getInfo()
    son_stats = son_clim_mean.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi_geom,
        scale=CHIRPS_SCALE, maxPixels=1e10
    ).getInfo()
    jja_mean_val = list(jja_stats.values())[0]
    son_mean_val = list(son_stats.values())[0]
    print(f'    JJA mean total: {jja_mean_val:.0f} mm')
    print(f'    SON mean total: {son_mean_val:.0f} mm')

    # ----------------------------------------------------------
    # Step 3: Compute anomalies for all years
    # ----------------------------------------------------------
    print('\n--- Step 3: Computing rainfall anomalies (P\' and Z_P) ---')

    jja_anomalies = compute_anomaly_collection(jja_collection, jja_clim_mean, jja_clim_std)
    son_anomalies = compute_anomaly_collection(son_collection, son_clim_mean, son_clim_std)
    dry_anomalies = compute_anomaly_collection(dry_collection, dry_clim_mean, dry_clim_std)

    print('  [OK] Anomalies computed for JJA, SON, and JJASON')

    # ----------------------------------------------------------
    # Step 4: ENSO phase composites
    # ----------------------------------------------------------
    print('\n--- Step 4: Creating ENSO phase composites ---')

    composites = {}

    # -- JJA --
    composites['jja_elnino_anomaly']   = enso_composite(jja_anomalies, EL_NINO_ALL, 'anomaly')
    composites['jja_elnino_zscore']    = enso_composite(jja_anomalies, EL_NINO_ALL, 'z_score')
    composites['jja_lanina_anomaly']   = enso_composite(jja_anomalies, LA_NINA,     'anomaly')
    composites['jja_lanina_zscore']    = enso_composite(jja_anomalies, LA_NINA,     'z_score')

    # -- SON --
    composites['son_elnino_anomaly']   = enso_composite(son_anomalies, EL_NINO_ALL, 'anomaly')
    composites['son_elnino_zscore']    = enso_composite(son_anomalies, EL_NINO_ALL, 'z_score')
    composites['son_lanina_anomaly']   = enso_composite(son_anomalies, LA_NINA,     'anomaly')
    composites['son_lanina_zscore']    = enso_composite(son_anomalies, LA_NINA,     'z_score')

    # -- Full dry season --
    composites['dry_elnino_anomaly']   = enso_composite(dry_anomalies, EL_NINO_ALL, 'anomaly')
    composites['dry_elnino_zscore']    = enso_composite(dry_anomalies, EL_NINO_ALL, 'z_score')

    print('  [OK] All composites created')

    # ----------------------------------------------------------
    # Step 5: El Niño-only vs El Niño+IOD+ comparison
    # ----------------------------------------------------------
    print('\n--- Step 5: El Niño-only vs El Niño+IOD+ ---')

    composites['jja_elnino_only_anomaly'] = enso_composite(jja_anomalies, EL_NINO_ONLY, 'anomaly')
    composites['jja_elnino_iod_anomaly']  = enso_composite(jja_anomalies, EL_NINO_IOD,  'anomaly')
    composites['son_elnino_only_anomaly'] = enso_composite(son_anomalies, EL_NINO_ONLY, 'anomaly')
    composites['son_elnino_iod_anomaly']  = enso_composite(son_anomalies, EL_NINO_IOD,  'anomaly')

    composites['jja_elnino_only_zscore']  = enso_composite(jja_anomalies, EL_NINO_ONLY, 'z_score')
    composites['jja_elnino_iod_zscore']   = enso_composite(jja_anomalies, EL_NINO_IOD,  'z_score')
    composites['son_elnino_only_zscore']  = enso_composite(son_anomalies, EL_NINO_ONLY, 'z_score')
    composites['son_elnino_iod_zscore']   = enso_composite(son_anomalies, EL_NINO_IOD,  'z_score')

    print('  [OK] Compound event comparison composites created')

    # ----------------------------------------------------------
    # Step 6: Spatial statistics
    # ----------------------------------------------------------
    print('\n--- Step 6: Spatial Statistics ---')
    print('\n  Composite Rainfall Anomaly (mm, mean over East Java):')

    print('\n  [JJA -- June-July-August]')
    print_composite_stats('El Niño (all)',          composites['jja_elnino_anomaly'],      aoi)
    print_composite_stats('El Niño-only',           composites['jja_elnino_only_anomaly'], aoi)
    print_composite_stats('El Niño + IOD+',         composites['jja_elnino_iod_anomaly'],  aoi)
    print_composite_stats('La Niña',                composites['jja_lanina_anomaly'],      aoi)

    print('\n  [SON -- September-October-November]')
    print_composite_stats('El Niño (all)',          composites['son_elnino_anomaly'],      aoi)
    print_composite_stats('El Niño-only',           composites['son_elnino_only_anomaly'], aoi)
    print_composite_stats('El Niño + IOD+',         composites['son_elnino_iod_anomaly'],  aoi)
    print_composite_stats('La Niña',                composites['son_lanina_anomaly'],      aoi)

    print('\n  [JJASON -- Full Dry Season]')
    print_composite_stats('El Niño (all)',          composites['dry_elnino_anomaly'],      aoi)

    # Per-event breakdown
    print('\n--- Per-Event Analysis ---')
    jja_events = per_event_anomalies(jja_anomalies, EL_NINO_ALL, aoi)
    print_event_table(jja_events, 'JJA')

    son_events = per_event_anomalies(son_anomalies, EL_NINO_ALL, aoi)
    print_event_table(son_events, 'SON')

    # ----------------------------------------------------------
    # Step 7: Save per-event statistics locally
    # ----------------------------------------------------------
    output_dir = os.path.join(PROJECT_DIR, 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    stats_output = {
        'generated': datetime.now().isoformat(),
        'baseline_years': NEUTRAL,
        'jja_climatology_mean_mm': jja_mean_val,
        'son_climatology_mean_mm': son_mean_val,
        'jja_per_event': jja_events,
        'son_per_event': son_events,
    }
    stats_path = os.path.join(output_dir, 'm2_rainfall_statistics.json')
    with open(stats_path, 'w') as f:
        json.dump(stats_output, f, indent=2)
    print(f'\n[OK] Statistics saved -> {stats_path}')

    # ----------------------------------------------------------
    # Step 8: Export to Google Drive
    # ----------------------------------------------------------
    print(f'\n--- Step 7: Exporting to Google Drive (folder: {DRIVE_FOLDER}) ---')

    exports = {
        # Climatology baselines
        'M2_JJA_climatology':           jja_clim_mean,
        'M2_SON_climatology':           son_clim_mean,
        # El Niño composites
        'M2_JJA_ElNino_anomaly_mm':     composites['jja_elnino_anomaly'],
        'M2_JJA_ElNino_zscore':         composites['jja_elnino_zscore'],
        'M2_SON_ElNino_anomaly_mm':     composites['son_elnino_anomaly'],
        'M2_SON_ElNino_zscore':         composites['son_elnino_zscore'],
        # La Niña composites (contrast)
        'M2_JJA_LaNina_anomaly_mm':     composites['jja_lanina_anomaly'],
        'M2_SON_LaNina_anomaly_mm':     composites['son_lanina_anomaly'],
        # El Niño-only vs compound
        'M2_JJA_ElNinoOnly_anomaly':    composites['jja_elnino_only_anomaly'],
        'M2_JJA_ElNinoIOD_anomaly':     composites['jja_elnino_iod_anomaly'],
        'M2_SON_ElNinoOnly_anomaly':    composites['son_elnino_only_anomaly'],
        'M2_SON_ElNinoIOD_anomaly':     composites['son_elnino_iod_anomaly'],
        # Full dry season
        'M2_JJASON_ElNino_anomaly_mm':  composites['dry_elnino_anomaly'],
        'M2_JJASON_ElNino_zscore':      composites['dry_elnino_zscore'],
    }

    tasks = run_exports(exports, aoi)
    print(f'\n  {len(tasks)} export tasks started.')
    print(f'  Check progress at: https://code.earthengine.google.com/tasks')
    print(f'  Files will appear in Google Drive -> {DRIVE_FOLDER}/')

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------
    print('\n' + '=' * 65)
    print('   MILESTONE 2 COMPLETE')
    print('=' * 65)
    print(f"""
  Outputs:
    Local:  {stats_path}
    Drive:  {DRIVE_FOLDER}/ ({len(tasks)} GeoTIFF files)

  Key composites exported:
    * JJA & SON El Nino rainfall anomaly (mm)
    * JJA & SON El Nino standardized anomaly (z-score)
    * La Nina contrast maps
    * El Nino-only vs El Nino+IOD+ comparison
    * Seasonal climatology baselines
    * Full dry season (JJASON) composites

  -> These maps form Deliverable A: Climate Response Atlas
  -> Next: Milestone 3 (Physical Response -- Soil Moisture & LST)
""")


if __name__ == '__main__':
    main()
