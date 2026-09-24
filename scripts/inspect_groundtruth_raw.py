import pandas as pd
import numpy as np

csv_path = r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr.csv'
df = pd.read_csv(csv_path)

print("======================================================================")
print("1. DATASET OVERVIEW & SCHEMA")
print("======================================================================")
print(f"Total rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")
print("Columns:", list(df.columns))
print(f"Tahun range: {df['tahun'].min()} to {df['tahun'].max()}")
print(f"Periode update range: {df['periode_update'].min()} to {df['periode_update'].max()}")
print(f"Unique periode_update: {df['periode_update'].nunique()} months")

print("\n======================================================================")
print("2. LIST OF ALL KABUPATEN/KOTA IN 2020-01")
print("======================================================================")
m1 = df[df['periode_update'] == '2020-01']
kab_m1 = m1[['id', 'kode_kabupaten_kota', 'nama_kabupaten_kota']].drop_duplicates().sort_values(by='id')
print(f"Total kabupaten/kota entries in 2020-01: {len(kab_m1)}")
for _, r in kab_m1.iterrows():
    print(f"id: {r['id']:3d} | kode: {r['kode_kabupaten_kota']} | nama: {r['nama_kabupaten_kota']}")

print("\n======================================================================")
print("3. UNIQUE KABUPATEN/KOTA NAMES ACROSS ENTIRE DATASET")
print("======================================================================")
unique_kabs = df['nama_kabupaten_kota'].unique()
print(f"Unique kabupaten/kota names: {len(unique_kabs)}")
print(sorted(unique_kabs))

print("\n======================================================================")
print("4. DUPLICATES ANALYSIS")
print("======================================================================")
key_cols = ['nama_kabupaten_kota', 'periode_update', 'kategori']
dup_mask = df.duplicated(subset=key_cols, keep=False)
dups = df[dup_mask]
print(f"Rows with duplicate (nama_kabupaten_kota, periode_update, kategori): {len(dups)}")
print(f"Unique duplicate pairs: {dups.groupby(key_cols).ngroups}")
print("Duplicated kabupaten breakdown:")
print(dups['nama_kabupaten_kota'].value_counts())

# What is happening with the 7 cities?
print("\nCheck id range for the duplicate cities:")
for city in dups['nama_kabupaten_kota'].unique():
    city_df = m1[m1['nama_kabupaten_kota'] == city]
    ids = city_df['id'].unique()
    kodes = city_df['kode_kabupaten_kota'].unique()
    print(f"  {city:20s} -> ids: {ids}, kodes: {kodes}")

print("\n======================================================================")
print("5. CHECKING THE 18 CASES WHERE DUPLICATES HAVE DIFFERENT JUMLAH")
print("======================================================================")
diff_cases = []
for (k, p, c), grp in dups.groupby(key_cols):
    if grp['jumlah'].nunique() > 1:
        diff_cases.append(grp)

print(f"Total duplicate groups with conflicting 'jumlah': {len(diff_cases)}")
if diff_cases:
    diff_df = pd.concat(diff_cases)
    print(diff_df[['id', 'id_index', 'nama_kabupaten_kota', 'periode_update', 'kategori', 'jumlah']].to_string())

print("\n======================================================================")
print("6. DISTRIBUTION OF VALUES (ZEROS VS NON-ZEROS)")
print("======================================================================")
zeros = (df['jumlah'] == 0).sum()
non_zeros = (df['jumlah'] > 0).sum()
print(f"Zero values (0.0): {zeros:,} ({zeros/len(df)*100:.2f}%)")
print(f"Non-zero values (>0): {non_zeros:,} ({non_zeros/len(df)*100:.2f}%)")
print(f"Null / NaN values: {df['jumlah'].isna().sum()}")

print("\nNon-zero summary stats:")
print(df[df['jumlah'] > 0]['jumlah'].describe())

print("\n======================================================================")
print("7. ANNUAL & COMMODITY SUMMARY")
print("======================================================================")
pivot = df.groupby(['tahun', 'kategori'])['jumlah'].agg(
    total_rows='count',
    non_zero_rows=lambda x: (x > 0).sum(),
    sum_ha='sum',
    max_ha='max'
)
print(pivot)

print("\n======================================================================")
print("8. MONTHLY SUMMARY FOR 2023 (EL NINO YEAR)")
print("======================================================================")
df_2023 = df[df['tahun'] == 2023]
pivot_2023 = df_2023.groupby(['periode_update', 'kategori'])['jumlah'].agg(
    non_zero=lambda x: (x > 0).sum(),
    sum_ha='sum'
).unstack()
print(pivot_2023)

print("\n======================================================================")
print("9. CHECKING THE HUGE 2024 NUMBER (58,145 HA)")
print("======================================================================")
df_2024 = df[df['tahun'] == 2024]
top_2024 = df_2024[df_2024['jumlah'] > 100].sort_values(by='jumlah', ascending=False)
print("Top records in 2024 (> 100 ha):")
print(top_2024[['nama_kabupaten_kota', 'periode_update', 'kategori', 'jumlah']].head(15).to_string())
