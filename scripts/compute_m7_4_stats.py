import pandas as pd
import numpy as np
from scipy import stats
import json

# 1. Load clean ground truth 2023-2024
clean_csv = 'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr_clean.csv'
df_gt = pd.read_csv(clean_csv)
df_en = df_gt[df_gt['tahun'].isin([2023, 2024])]

gt_agg = df_en.groupby('nama_kabupaten_kota').agg(
    total_drought_ha=('jumlah', 'sum'),
    padi_ha=('jumlah', lambda x: x[df_en.loc[x.index, 'kategori'] == 'PADI'].sum()),
    jagung_ha=('jumlah', lambda x: x[df_en.loc[x.index, 'kategori'] == 'JAGUNG'].sum()),
    kedelai_ha=('jumlah', lambda x: x[df_en.loc[x.index, 'kategori'] == 'KEDELAI'].sum()),
    palawija_ha=('jumlah', lambda x: x[df_en.loc[x.index, 'kategori'].isin(['JAGUNG', 'KEDELAI'])].sum()),
    months_drought=('jumlah', lambda x: (x > 0).sum())
).reset_index()

# 2. Load M6 statistics
with open('outputs/m6_agriculture_policy_statistics.json') as f:
    m6_stats = json.load(f)

m6_df = pd.DataFrame(m6_stats['district_rankings'])

def normalize_name(n):
    n = n.upper()
    if not n.startswith('KABUPATEN') and not n.startswith('KOTA'):
        n = 'KABUPATEN ' + n
    return n

m6_df['norm_name'] = m6_df['district_name'].apply(normalize_name)
m6_df = m6_df[m6_df['district_name'] != 'Kota Jember']

# Merge
merged = pd.merge(gt_agg, m6_df, left_on='nama_kabupaten_kota', right_on='norm_name', how='inner')
print(f"Merged {len(merged)} districts successfully!")

# Correlations
r_asi, p_asi = stats.pearsonr(merged['mean_asi'], merged['total_drought_ha'])
rho_asi, p_rho_asi = stats.spearmanr(merged['mean_asi'], merged['total_drought_ha'])

r_lsi, p_lsi = stats.pearsonr(merged['mean_lsi'], merged['total_drought_ha'])
rho_lsi, p_rho_lsi = stats.spearmanr(merged['mean_lsi'], merged['total_drought_ha'])

r_crop, p_crop = stats.pearsonr(merged['crop_fraction'], merged['total_drought_ha'])
rho_crop, p_rho_crop = stats.spearmanr(merged['crop_fraction'], merged['total_drought_ha'])

print("\n=== CORRELATION WITH 2023-2024 TOTAL DROUGHT HA (n=38) ===")
print(f"ASI  -> Pearson r: {r_asi:.4f} (p={p_asi:.4e}, R²={r_asi**2:.4f}) | Spearman rho: {rho_asi:.4f} (p={p_rho_asi:.4e})")
print(f"LSI  -> Pearson r: {r_lsi:.4f} (p={p_lsi:.4e}, R²={r_lsi**2:.4f}) | Spearman rho: {rho_lsi:.4f} (p={p_rho_lsi:.4e})")
print(f"CROP -> Pearson r: {r_crop:.4f} (p={p_crop:.4e}, R²={r_crop**2:.4f}) | Spearman rho: {rho_crop:.4f} (p={p_rho_crop:.4e})")

# Padi only
r_padi_asi, p_padi_asi = stats.pearsonr(merged['mean_asi'], merged['padi_ha'])
rho_padi_asi, p_rho_padi = stats.spearmanr(merged['mean_asi'], merged['padi_ha'])
print(f"\nPADI HA vs ASI -> Pearson r: {r_padi_asi:.4f} (p={p_padi_asi:.4e}) | Spearman rho: {rho_padi_asi:.4f} (p={p_rho_padi:.4e})")

# Check log transform (since loss area spans orders of magnitude: 0 to 13,000 ha)
# log(ha + 1)
merged['log_total_ha'] = np.log10(merged['total_drought_ha'] + 1)
merged['log_padi_ha'] = np.log10(merged['padi_ha'] + 1)

r_log_asi, p_log_asi = stats.pearsonr(merged['mean_asi'], merged['log_total_ha'])
rho_log_asi, _ = stats.spearmanr(merged['mean_asi'], merged['log_total_ha'])
print(f"\nLOG10(TOTAL HA + 1) vs ASI -> Pearson r: {r_log_asi:.4f} (p={p_log_asi:.4e}, R²={r_log_asi**2:.4f}) | Spearman rho: {rho_log_asi:.4f}")

# Check by risk tier
print("\n=== TOTAL LOSS BY ASI RISK TIER ===")
tier_summary = merged.groupby('risk_tier').agg(
    districts=('district_name', 'count'),
    total_drought_ha=('total_drought_ha', 'sum'),
    padi_ha=('padi_ha', 'sum'),
    palawija_ha=('palawija_ha', 'sum'),
    mean_asi=('mean_asi', 'mean'),
    mean_lsi=('mean_lsi', 'mean')
).sort_values(by='mean_asi', ascending=False)
tier_summary['share_pct'] = tier_summary['total_drought_ha'] / merged['total_drought_ha'].sum() * 100
print(tier_summary.to_string())

print("\n=== TOP 15 DISTRICTS ===")
cols_show = ['district_name', 'priority_rank', 'mean_asi', 'mean_lsi', 'crop_fraction', 'risk_tier', 'total_drought_ha', 'padi_ha', 'palawija_ha']
print(merged.sort_values(by='total_drought_ha', ascending=False)[cols_show].head(15).to_string())
