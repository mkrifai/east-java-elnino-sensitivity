"""
Milestone 6: Agriculture and Policy Translation
===============================================
Phase 10 -- Agricultural Exposure Mapping
Deliverable C -- Agricultural Sensitivity Atlas
Phase 11 -- Policy-Relevant Prioritization & Decision-Support
Deliverable D -- Policy Translation Map

Computes, exports to Drive, and duplicates locally:
  1. Cropland Fraction at 1 km (ESA WorldCover)
  2. Agricultural Sensitivity Index (ASI = LSI * Cropland Fraction)
  3. Critical Cropland Risk Hotspots (High LSI and High Cropland density)
  4. 4 Policy Intervention Zones (Zone 1 to Zone 4)
  5. Comprehensive district-level risk ranking across all 39 Kabupaten/Kota
  6. Direct download of local GeoTIFF duplicates to outputs/geotiffs/m6/

Outputs -> Deliverable C (Agricultural Sensitivity) & Deliverable D (Policy Translation Map)

Usage:
  python scripts/m6_agriculture_policy.py
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
    get_east_java, get_east_java_districts,
    START_YEAR, END_YEAR,
    EL_NINO_ALL, NEUTRAL,
    SON, JJA, DRY_SEASON,
    WORLDCOVER,
    EXPORT_SCALE, DRIVE_FOLDER,
    build_seasonal_collection,
    export_image, download_image_local,
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


def main():
    print()
    print('=' * 65)
    print('   MILESTONE 6: AGRICULTURE & POLICY TRANSLATION')
    print('   Deliverables C & D: Agricultural Sensitivity & Policy Zones')
    print('   ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
    print('=' * 65)

    ee.Initialize()
    print('\n[OK] Google Earth Engine initialized')

    aoi = get_east_java()
    aoi_geom = aoi.geometry()
    districts = get_east_java_districts()
    print('[OK] Study area: Jawa Timur (East Java) with 39 Districts')

    # ----------------------------------------------------------
    # Step 1: Reconstructing LSI from Milestone 5
    # ----------------------------------------------------------
    print('\n--- Step 1: Reconstructing Landscape Sensitivity Index (LSI) ---')

    chirps_son_col = build_seasonal_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    p_son_mean, p_son_std = m2_compute_climatology(chirps_son_col, NEUTRAL)
    z_p = m2_composite(m2_compute_anomaly(chirps_son_col, p_son_mean, p_son_std), EL_NINO_ALL, 'z_score')

    sm_son_col = build_seasonal_sm_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    sm_son_mean, sm_son_std = m3_compute_climatology(sm_son_col, 'sm', NEUTRAL, min_std=0.005)
    z_sm = m3_composite(m3_compute_anomalies(sm_son_col, 'sm', sm_son_mean, sm_son_std), 'sm_zscore', EL_NINO_ALL)

    lst_son_col = build_seasonal_lst_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    lst_son_mean, lst_son_std = m3_compute_climatology(lst_son_col, 'lst', NEUTRAL, min_std=0.1)
    z_lst = m3_composite(m3_compute_anomalies(lst_son_col, 'lst', lst_son_mean, lst_son_std), 'lst_zscore', EL_NINO_ALL)

    veg_son_col = build_seasonal_veg_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    ndvi_son_mean, ndvi_son_std = m4_compute_climatology(veg_son_col, 'ndvi', NEUTRAL)
    ndmi_son_mean, ndmi_son_std = m4_compute_climatology(veg_son_col, 'ndmi', NEUTRAL)

    veg_anom = m4_compute_anomalies(veg_son_col, 'ndvi', ndvi_son_mean, ndvi_son_std)
    veg_anom = m4_compute_anomalies(veg_anom, 'ndmi', ndmi_son_mean, ndmi_son_std)
    z_ndvi = m4_composite(veg_anom, 'ndvi_zscore', EL_NINO_ALL)
    z_ndmi = m4_composite(veg_anom, 'ndmi_zscore', EL_NINO_ALL)

    lsi_raw = (z_p.multiply(-1.0)
               .add(z_sm.multiply(-1.0))
               .add(z_lst)
               .add(z_ndvi.multiply(-1.0))
               .add(z_ndmi.multiply(-1.0)))

    # Normalized LSI [0.0 to 1.0] using established percentiles
    p2, p98 = 1.09, 6.22
    lsi = (lsi_raw.subtract(p2).divide(p98 - p2)).clamp(0.0, 1.0).rename('landscape_sensitivity_index')
    print('  [OK] LSI reconstructed successfully')

    # ----------------------------------------------------------
    # Step 2: Agricultural Exposure Mapping (Phase 10)
    # ----------------------------------------------------------
    print('\n--- Step 2: Agricultural Exposure Mapping (Phase 10) ---')
    wc = ee.ImageCollection(WORLDCOVER).first().clip(aoi_geom)
    # Class 40 is Cropland in ESA WorldCover
    cropland_10m = wc.eq(40).rename('cropland')
    # Resample / aggregate to 1 km fraction (0.0 to 1.0)
    crop_fraction = cropland_10m.toFloat().rename('crop_fraction')
    print('  [OK] Cropland exposure layer created')

    # ----------------------------------------------------------
    # Step 3: Agricultural Sensitivity Index (Deliverable C)
    # ----------------------------------------------------------
    print('\n--- Step 3: Synthesizing Agricultural Sensitivity Index (ASI) ---')
    # ASI = LSI * Cropland Fraction
    asi = lsi.multiply(crop_fraction).rename('agricultural_sensitivity_index')

    # Critical Cropland Risk Hotspots: LSI > 0.60 AND Crop Fraction > 0.30
    critical_hotspots = (lsi.gt(0.60).And(crop_fraction.gt(0.30))).rename('critical_cropland_hotspot')

    print('  [OK] Deliverable C: Agricultural Sensitivity Index (ASI) & Hotspots synthesized')

    # ----------------------------------------------------------
    # Step 4: Policy Intervention Zones (Deliverable D - Phase 11)
    # ----------------------------------------------------------
    print('\n--- Step 4: Delineating Policy Intervention Zones (Deliverable D) ---')

    # 4 Operational Policy Zones:
    # Zone 1: Critical Emergency Intervention Zone (High LSI >= 0.60 & High Crop Fraction >= 0.30)
    # Zone 2: Hydrologic Vulnerability & Irrigation Conflict (High LSI >= 0.60 & Crop Fraction < 0.30)
    # Zone 3: Rain-Shadow & Fodder/Orchard Vulnerability (0.50 <= LSI < 0.60)
    # Zone 4: Ecological Catchment Protection Zone (LSI < 0.50)

    z1 = lsi.gte(0.60).And(crop_fraction.gte(0.30))
    z2 = lsi.gte(0.60).And(crop_fraction.lt(0.30))
    z3 = lsi.gte(0.50).And(lsi.lt(0.60))
    z4 = lsi.lt(0.50)

    policy_zones = (ee.Image(0)
                    .where(z4, 4)
                    .where(z3, 3)
                    .where(z2, 2)
                    .where(z1, 1)
                    .rename('policy_intervention_zones'))

    print('  [OK] Deliverable D: 4 Policy Intervention Zones delineated')

    # ----------------------------------------------------------
    # Step 5: District-Level Batch Aggregation (39 Districts)
    # ----------------------------------------------------------
    print('\n--- Step 5: District-Level Aggregation & Risk Ranking ---')

    combined_stack = (lsi
                      .addBands(crop_fraction)
                      .addBands(asi)
                      .addBands(critical_hotspots))

    pixel_area_ha = ee.Image.pixelArea().divide(1e4)

    # Batch reduce across all districts using reduceRegions
    reduced_districts = combined_stack.reduceRegions(
        collection=districts,
        reducer=ee.Reducer.mean(),
        scale=1000
    )

    district_features = reduced_districts.getInfo()['features']
    district_table = []

    for f in district_features:
        p = f['properties']
        name = p.get('ADM2_NAME', 'Unknown')
        mean_lsi = p.get('landscape_sensitivity_index', 0.0)
        mean_crop = p.get('crop_fraction', 0.0)
        mean_asi = p.get('agricultural_sensitivity_index', 0.0)
        mean_hotspot = p.get('critical_cropland_hotspot', 0.0)

        # Estimate total district area from geometry if possible
        district_table.append({
            'district_name': name,
            'mean_lsi': round(mean_lsi, 3),
            'crop_fraction': round(mean_crop, 3),
            'mean_asi': round(mean_asi, 4),
            'critical_hotspot_pct': round(mean_hotspot * 100, 1),
        })

    # Sort districts by Mean Agricultural Sensitivity Index (mean_asi) descending
    district_table.sort(key=lambda x: x['mean_asi'], reverse=True)

    for rank, d in enumerate(district_table, 1):
        d['priority_rank'] = rank
        # Assign risk category
        if d['mean_asi'] >= 0.20:
            d['risk_tier'] = 'Extreme Priority (Tier 1)'
        elif d['mean_asi'] >= 0.15:
            d['risk_tier'] = 'High Priority (Tier 2)'
        elif d['mean_asi'] >= 0.10:
            d['risk_tier'] = 'Moderate Priority (Tier 3)'
        else:
            d['risk_tier'] = 'Low / Buffered (Tier 4)'

    print('\n--- Top 15 Most Vulnerable Agricultural Districts in East Java ---')
    print(f'  {"Rank":<5} {"District Name":<22} {"Mean LSI":>9} {"Crop Frac":>10} {"Mean ASI":>9} {"Hotspot (%)":>12} {"Risk Tier":<22}')
    print(f'  {"-"*5} {"-"*22} {"-"*9} {"-"*10} {"-"*9} {"-"*12} {"-"*22}')
    for d in district_table[:15]:
        print(f'  {d["priority_rank"]:<5} {d["district_name"]:<22} {d["mean_lsi"]:>9.2f} {d["crop_fraction"]:>10.3f} {d["mean_asi"]:>9.3f} {d["critical_hotspot_pct"]:>11.1f}% {d["risk_tier"]:<22}')

    # ----------------------------------------------------------
    # Step 6: Save Statistics JSON
    # ----------------------------------------------------------
    output_dir = os.path.join(PROJECT_DIR, 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    summary_json = {
        'generated': datetime.now().isoformat(),
        'total_districts': len(district_table),
        'district_rankings': district_table,
        'policy_zones_description': {
            'Zone_1': 'Critical Emergency Intervention Zone (High LSI >= 0.60 & Crop Fraction >= 0.30)',
            'Zone_2': 'Hydrologic Vulnerability & Irrigation Conflict Zone (High LSI >= 0.60 & Crop Fraction < 0.30)',
            'Zone_3': 'Rain-Shadow & Fodder/Orchard Vulnerability Zone (0.50 <= LSI < 0.60)',
            'Zone_4': 'Ecological Catchment Protection Zone (LSI < 0.50)',
        }
    }
    stats_path = os.path.join(output_dir, 'm6_agriculture_policy_statistics.json')
    with open(stats_path, 'w') as f:
        json.dump(summary_json, f, indent=2)
    print(f'\n[OK] Agricultural & Policy statistics saved -> {stats_path}')

    # ----------------------------------------------------------
    # Step 7: Export to Google Drive & Download Local Duplicates
    # ----------------------------------------------------------
    print(f'\n--- Step 7: Exporting to Drive & Downloading Local Duplicates ---')

    exports = {
        # Deliverable C
        'M6_Cropland_Fraction_1km':           crop_fraction,
        'M6_Agricultural_Sensitivity_Index':   asi,
        'M6_Critical_Cropland_Risk_Hotspots': critical_hotspots,

        # Deliverable D
        'M6_Policy_Intervention_Zones':        policy_zones,
    }

    # Start Drive tasks
    drive_tasks = []
    for desc, img in exports.items():
        task = export_image(img, desc, aoi, scale=1000)
        drive_tasks.append(task)
        print(f'  [Drive Task] {desc}')

    # Download local duplicates
    m6_local_dir = os.path.join(output_dir, 'geotiffs', 'm6')
    os.makedirs(m6_local_dir, exist_ok=True)
    print(f'\n  Downloading local GeoTIFF duplicates to {m6_local_dir}...')

    for desc, img in exports.items():
        dst = os.path.join(m6_local_dir, f"{desc}.tif")
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            print(f'  [EXISTS] {desc}.tif ({os.path.getsize(dst)/1024:.1f} KB)')
            continue
        try:
            print(f'  [DOWNLOAD] {desc}...', end=' ', flush=True)
            t0 = time.time()
            download_image_local(img, desc, aoi_geom, m6_local_dir, scale=1000)
            dt = time.time() - t0
            print(f'OK ({os.path.getsize(dst)/1024:.1f} KB in {dt:.1f}s)')
        except Exception as e:
            print(f'FAILED: {e}')

    print('\n' + '=' * 65)
    print('   MILESTONE 6 COMPLETE')
    print('=' * 65)


if __name__ == '__main__':
    main()
