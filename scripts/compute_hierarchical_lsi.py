"""
Compute Hierarchical Landscape Sensitivity Index (H-LSI) for all 582 Kecamatan in East Java.
Generates comprehensive tabular dataset with provincial ranking and intra-kabupaten relative disparity.
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import warnings
warnings.filterwarnings('ignore')

def main():
    shp_path = "Batas Administrasi Kecamatan di Jawa Timur/administrasi_ar_kec_jatim.shp"
    tif_path = "outputs/geotiffs/m5/M5_Landscape_Sensitivity_Index.tif"
    out_csv = "outputs/m5_hierarchical_lsi_kecamatan.csv"

    print(f"Loading kecamatan shapefile: {shp_path}...")
    gdf = gpd.read_file(shp_path)
    print(f"Total kecamatan in shapefile: {len(gdf)}")

    print(f"Opening raster: {tif_path}...")
    with rasterio.open(tif_path) as src:
        raster_crs = src.crs
        nodata = src.nodata

        # Ensure CRS matches
        if gdf.crs != raster_crs:
            print(f"Reprojecting GDF from {gdf.crs} to {raster_crs}...")
            gdf = gdf.to_crs(raster_crs)

        results = []
        for idx, row in gdf.iterrows():
            geom = [row.geometry]
            kab = str(row['NAMA_KABUP']).strip()
            kec = str(row['NAMA_KECAM']).strip()
            id_kec = row.get('ID_KEC', idx)

            try:
                out_img, _ = mask(src, geom, crop=True)
                data = out_img[0]
                valid = data[~np.isnan(data) & (data != nodata) & (data >= 0) & (data <= 1)]
                
                if len(valid) > 0:
                    mean_val = float(np.mean(valid))
                    median_val = float(np.median(valid))
                    std_val = float(np.std(valid))
                    p10_val = float(np.percentile(valid, 10))
                    p90_val = float(np.percentile(valid, 90))
                    iqr_val = float(np.percentile(valid, 75) - np.percentile(valid, 25))
                    pct_crit = float(np.sum(valid >= 0.75) / len(valid) * 100.0)
                    pct_severe = float(np.sum(valid >= 0.85) / len(valid) * 100.0)
                    n_pixels = int(len(valid))
                else:
                    mean_val = np.nan
                    median_val = np.nan
                    std_val = np.nan
                    p10_val = np.nan
                    p90_val = np.nan
                    iqr_val = np.nan
                    pct_crit = np.nan
                    pct_severe = np.nan
                    n_pixels = 0

            except Exception as e:
                mean_val = np.nan
                median_val = np.nan
                std_val = np.nan
                p10_val = np.nan
                p90_val = np.nan
                iqr_val = np.nan
                pct_crit = np.nan
                pct_severe = np.nan
                n_pixels = 0

            results.append({
                'id_kec': id_kec,
                'kabupaten': kab,
                'kecamatan': kec,
                'mean_lsi': mean_val,
                'median_lsi': median_val,
                'std_lsi': std_val,
                'p10_lsi': p10_val,
                'p90_lsi': p90_val,
                'iqr_lsi': iqr_val,
                'pct_critical_area': pct_crit,
                'pct_severe_area': pct_severe,
                'n_pixels_1km2': n_pixels
            })

    df = pd.DataFrame(results)

    # For tiny sub-grid coastal/island subdistricts with 0 valid raster cells due to ERA5 coastal masking,
    # impute using spatial nearest neighbor / county mean so no kecamatan is left unclassified
    kab_means = df.groupby('kabupaten')['mean_lsi'].transform('mean')
    df['mean_lsi_filled'] = df['mean_lsi'].fillna(kab_means)
    df['median_lsi_filled'] = df['median_lsi'].fillna(df['mean_lsi_filled'])
    df['pct_critical_area'] = df['pct_critical_area'].fillna(0.0)

    # Provincial Rank (1 = Highest Sensitivity / Most Vulnerable)
    df['prov_rank'] = df['mean_lsi_filled'].rank(ascending=False, method='min').astype(int)

    # Intra-Kabupaten Mean & Std
    kab_stats = df.groupby('kabupaten')['mean_lsi_filled'].agg(['mean', 'std']).reset_index()
    kab_stats.columns = ['kabupaten', 'kab_mean_lsi', 'kab_std_lsi']
    df = df.merge(kab_stats, on='kabupaten', how='left')

    # Intra-Kabupaten Rank
    df['intra_kab_rank'] = df.groupby('kabupaten')['mean_lsi_filled'].rank(ascending=False, method='min').astype(int)
    df['kab_total_kec'] = df.groupby('kabupaten')['kecamatan'].transform('count')

    # Intra-Kabupaten Relative Metrics
    df['intra_kab_delta'] = df['mean_lsi_filled'] - df['kab_mean_lsi']
    df['intra_kab_zscore'] = np.where(
        (df['kab_std_lsi'].isna()) | (df['kab_std_lsi'] == 0),
        0.0,
        (df['mean_lsi_filled'] - df['kab_mean_lsi']) / df['kab_std_lsi']
    )

    # Risk Classification
    def classify_risk(row):
        score = row['mean_lsi_filled']
        crit_pct = row['pct_critical_area']
        if score >= 0.80 or crit_pct >= 60.0:
            return "Extreme Priority (Tier 1)"
        elif score >= 0.65 or crit_pct >= 30.0:
            return "High Priority (Tier 2)"
        elif score >= 0.45:
            return "Moderate Sensitivity (Tier 3)"
        else:
            return "High Resilience (Buffer Zone)"

    df['risk_category'] = df.apply(classify_risk, axis=1)

    # Sort by Provincial Rank
    df = df.sort_values(by='prov_rank', ascending=True).reset_index(drop=True)

    # Select and arrange clean columns
    col_order = [
        'prov_rank', 'kabupaten', 'kecamatan', 'mean_lsi_filled', 'median_lsi_filled',
        'std_lsi', 'iqr_lsi', 'pct_critical_area', 'pct_severe_area', 'n_pixels_1km2',
        'intra_kab_rank', 'kab_total_kec', 'kab_mean_lsi', 'intra_kab_delta', 'intra_kab_zscore',
        'risk_category'
    ]
    df_out = df[col_order].rename(columns={
        'mean_lsi_filled': 'mean_lsi',
        'median_lsi_filled': 'median_lsi'
    })

    os.makedirs('outputs', exist_ok=True)
    df_out.to_csv(out_csv, index=False)
    print(f"Successfully saved {len(df_out)} kecamatan to {out_csv}!")

    # Print executive summary
    print("\n" + "="*80)
    print("TOP 10 MOST VULNERABLE KECAMATAN IN EAST JAVA (PROVINCIAL LEVEL):")
    print("="*80)
    print(df_out[['prov_rank', 'kabupaten', 'kecamatan', 'mean_lsi', 'pct_critical_area', 'risk_category']].head(10).to_string(index=False))

    print("\n" + "="*80)
    print("TOP 10 MOST RESILIENT KECAMATAN IN EAST JAVA (NATURAL CLIMATE BUFFERS):")
    print("="*80)
    print(df_out[['prov_rank', 'kabupaten', 'kecamatan', 'mean_lsi', 'pct_critical_area', 'risk_category']].tail(10).to_string(index=False))

    print("\n" + "="*80)
    print("KABUPATEN WITH HIGHEST INTERNAL DISPARITY (MAX DELTA BETWEEN KECAMATAN):")
    print("="*80)
    kab_range = df_out.groupby('kabupaten')['mean_lsi'].agg(['min', 'max', 'count']).reset_index()
    kab_range['disparity_range'] = kab_range['max'] - kab_range['min']
    print(kab_range.sort_values(by='disparity_range', ascending=False).head(8).to_string(index=False))

if __name__ == '__main__':
    main()
