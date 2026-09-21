"""
Download GeoTIFF duplicates to local disk
=========================================
Downloads raster layers for Milestone 2 and Milestone 3 directly to:
  - outputs/geotiffs/m2/
  - outputs/geotiffs/m3/
"""

import os
import sys
import time

# Configure UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import ee

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from config import (
    get_east_java,
    START_YEAR, END_YEAR,
    EL_NINO_ALL, EL_NINO_ONLY, EL_NINO_IOD,
    LA_NINA, NEUTRAL,
    JJA, SON, DRY_SEASON,
    CHIRPS_SCALE, EXPORT_SCALE,
    build_seasonal_collection,
    download_image_local,
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


def download_m2_geotiffs(aoi, out_dir):
    print("\n--- Downloading Milestone 2 GeoTIFFs (Climate Response) ---")
    aoi_geom = aoi.geometry()

    jja_col = build_seasonal_collection(JJA, START_YEAR, END_YEAR, aoi_geom)
    son_col = build_seasonal_collection(SON, START_YEAR, END_YEAR, aoi_geom)
    dry_col = build_seasonal_collection(DRY_SEASON, START_YEAR, END_YEAR, aoi_geom)

    jja_mean, jja_std = m2_compute_climatology(jja_col, NEUTRAL)
    son_mean, son_std = m2_compute_climatology(son_col, NEUTRAL)
    dry_mean, dry_std = m2_compute_climatology(dry_col, NEUTRAL)

    jja_anom = m2_compute_anomaly(jja_col, jja_mean, jja_std)
    son_anom = m2_compute_anomaly(son_col, son_mean, son_std)
    dry_anom = m2_compute_anomaly(dry_col, dry_mean, dry_std)

    m2_layers = {
        'M2_JJA_climatology':           jja_mean,
        'M2_SON_climatology':           son_mean,
        'M2_JJA_ElNino_anomaly_mm':     m2_composite(jja_anom, EL_NINO_ALL, 'anomaly'),
        'M2_JJA_ElNino_zscore':         m2_composite(jja_anom, EL_NINO_ALL, 'z_score'),
        'M2_SON_ElNino_anomaly_mm':     m2_composite(son_anom, EL_NINO_ALL, 'anomaly'),
        'M2_SON_ElNino_zscore':         m2_composite(son_anom, EL_NINO_ALL, 'z_score'),
        'M2_JJA_LaNina_anomaly_mm':     m2_composite(jja_anom, LA_NINA,     'anomaly'),
        'M2_SON_LaNina_anomaly_mm':     m2_composite(son_anom, LA_NINA,     'anomaly'),
        'M2_JJA_ElNinoOnly_anomaly':    m2_composite(jja_anom, EL_NINO_ONLY, 'anomaly'),
        'M2_JJA_ElNinoIOD_anomaly':     m2_composite(jja_anom, EL_NINO_IOD,  'anomaly'),
        'M2_SON_ElNinoOnly_anomaly':    m2_composite(son_anom, EL_NINO_ONLY, 'anomaly'),
        'M2_SON_ElNinoIOD_anomaly':     m2_composite(son_anom, EL_NINO_IOD,  'anomaly'),
        'M2_JJASON_ElNino_anomaly_mm':  m2_composite(dry_anom, EL_NINO_ALL, 'anomaly'),
        'M2_JJASON_ElNino_zscore':      m2_composite(dry_anom, EL_NINO_ALL, 'z_score'),
    }

    for name, img in m2_layers.items():
        dst = os.path.join(out_dir, f"{name}.tif")
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            print(f"  [EXISTS] {name}.tif ({os.path.getsize(dst)/1024:.1f} KB)")
            continue
        try:
            print(f"  [DOWNLOADING] {name}...", end=" ", flush=True)
            t0 = time.time()
            download_image_local(img, name, aoi_geom, out_dir, scale=CHIRPS_SCALE)
            dt = time.time() - t0
            print(f"OK ({os.path.getsize(dst)/1024:.1f} KB in {dt:.1f}s)")
        except Exception as e:
            print(f"FAILED: {e}")


def download_m3_geotiffs(aoi, out_dir):
    print("\n--- Downloading Milestone 3 GeoTIFFs (Physical Response) ---")
    aoi_geom = aoi.geometry()

    # Soil Moisture
    sm_jja_col = build_seasonal_sm_collection(JJA, START_YEAR, END_YEAR, aoi_geom)
    sm_son_col = build_seasonal_sm_collection(SON, START_YEAR, END_YEAR, aoi_geom)

    sm_jja_mean, sm_jja_std = m3_compute_climatology(sm_jja_col, 'sm', NEUTRAL, min_std=0.005)
    sm_son_mean, sm_son_std = m3_compute_climatology(sm_son_col, 'sm', NEUTRAL, min_std=0.005)

    sm_jja_anom = m3_compute_anomalies(sm_jja_col, 'sm', sm_jja_mean, sm_jja_std)
    sm_son_anom = m3_compute_anomalies(sm_son_col, 'sm', sm_son_mean, sm_son_std)

    # LST
    lst_jja_col = build_seasonal_lst_collection(JJA, START_YEAR, END_YEAR, aoi_geom)
    lst_son_col = build_seasonal_lst_collection(SON, START_YEAR, END_YEAR, aoi_geom)

    lst_jja_mean, lst_jja_std = m3_compute_climatology(lst_jja_col, 'lst', NEUTRAL, min_std=0.1)
    lst_son_mean, lst_son_std = m3_compute_climatology(lst_son_col, 'lst', NEUTRAL, min_std=0.1)

    lst_jja_anom = m3_compute_anomalies(lst_jja_col, 'lst', lst_jja_mean, lst_jja_std)
    lst_son_anom = m3_compute_anomalies(lst_son_col, 'lst', lst_son_mean, lst_son_std)

    # Physical Sensitivity Index (PSI) & Hotspots
    z_lst_son = m3_composite(lst_son_anom, 'lst_zscore', EL_NINO_ALL)
    z_sm_son  = m3_composite(sm_son_anom,  'sm_zscore',  EL_NINO_ALL)
    psi = z_lst_son.subtract(z_sm_son).rename('psi')
    hotspot = z_lst_son.gt(0.5).And(z_sm_son.lt(-0.5)).rename('hotspot')

    m3_layers = {
        # Soil moisture (5 km)
        ('M3_JJA_SM_ElNino_anomaly',     5000): m3_composite(sm_jja_anom, 'sm_anomaly', EL_NINO_ALL),
        ('M3_SON_SM_ElNino_anomaly',     5000): m3_composite(sm_son_anom, 'sm_anomaly', EL_NINO_ALL),
        ('M3_SON_SM_ElNino_zscore',      5000): m3_composite(sm_son_anom, 'sm_zscore',  EL_NINO_ALL),
        ('M3_SON_SM_ElNinoOnly_anomaly', 5000): m3_composite(sm_son_anom, 'sm_anomaly', EL_NINO_ONLY),
        ('M3_SON_SM_ElNinoIOD_anomaly',  5000): m3_composite(sm_son_anom, 'sm_anomaly', EL_NINO_IOD),
        ('M3_SON_SM_LaNina_anomaly',     5000): m3_composite(sm_son_anom, 'sm_anomaly', LA_NINA),

        # LST (1 km)
        ('M3_JJA_LST_ElNino_anomaly',     1000): m3_composite(lst_jja_anom, 'lst_anomaly', EL_NINO_ALL),
        ('M3_SON_LST_ElNino_anomaly',     1000): m3_composite(lst_son_anom, 'lst_anomaly', EL_NINO_ALL),
        ('M3_SON_LST_ElNino_zscore',      1000): z_lst_son,
        ('M3_SON_LST_ElNinoOnly_anomaly', 1000): m3_composite(lst_son_anom, 'lst_anomaly', EL_NINO_ONLY),
        ('M3_SON_LST_ElNinoIOD_anomaly',  1000): m3_composite(lst_son_anom, 'lst_anomaly', EL_NINO_IOD),
        ('M3_SON_LST_LaNina_anomaly',     1000): m3_composite(lst_son_anom, 'lst_anomaly', LA_NINA),

        # Coupling & Hotspots (1 km)
        ('M3_SON_Physical_Sensitivity_Index', 1000): psi,
        ('M3_SON_High_Sensitivity_Zone',      1000): hotspot,
    }

    for (name, scale), img in m3_layers.items():
        dst = os.path.join(out_dir, f"{name}.tif")
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            print(f"  [EXISTS] {name}.tif ({os.path.getsize(dst)/1024:.1f} KB)")
            continue
        try:
            print(f"  [DOWNLOADING] {name} ({scale}m)...", end=" ", flush=True)
            t0 = time.time()
            download_image_local(img, name, aoi_geom, out_dir, scale=scale)
            dt = time.time() - t0
            print(f"OK ({os.path.getsize(dst)/1024:.1f} KB in {dt:.1f}s)")
        except Exception as e:
            print(f"FAILED: {e}")


def main():
    print("=" * 65)
    print("   LOCAL GEOTIFF DOWNLOADER")
    print("   East Java El Nino Sensitivity Project")
    print("=" * 65)

    ee.Initialize()
    aoi = get_east_java()

    m2_dir = os.path.join(PROJECT_DIR, 'outputs', 'geotiffs', 'm2')
    m3_dir = os.path.join(PROJECT_DIR, 'outputs', 'geotiffs', 'm3')

    download_m2_geotiffs(aoi, m2_dir)
    download_m3_geotiffs(aoi, m3_dir)

    print("\n" + "=" * 65)
    print("   ALL GEOTIFF DUPLICATES STORED LOCALLY")
    print(f"   M2 folder: {m2_dir}")
    print(f"   M3 folder: {m3_dir}")
    print("=" * 65)


if __name__ == '__main__':
    main()
