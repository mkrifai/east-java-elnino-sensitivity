import pandas as pd
import numpy as np

csv_path = r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr.csv'
df = pd.read_csv(csv_path)

print("=" * 80)
print("A. INVESTIGASI NAMA KABUPATEN/KOTA '0' DAN ENTITAS TIDAK VALID")
print("=" * 80)
invalid_kabs = df[df['nama_kabupaten_kota'].isin(['0', 0, ''])]
print(f"Total baris dengan nama_kabupaten_kota == '0': {len(invalid_kabs)}")
print(invalid_kabs[['id', 'id_index', 'kode_kabupaten_kota', 'nama_kabupaten_kota', 'periode_update', 'kategori', 'jumlah']].head(20).to_string())

# Cek apakah '0' adalah total provinsi
print("\nVerifikasi apakah baris '0' merupakan TOTAL PROVINSI:")
for p in invalid_kabs['periode_update'].unique():
    for c in ['PADI', 'JAGUNG']:
        sub = df[(df['periode_update'] == p) & (df['kategori'] == c)]
        val_0 = sub[sub['nama_kabupaten_kota'].isin(['0', 0])]['jumlah'].values
        val_other_sum = sub[~sub['nama_kabupaten_kota'].isin(['0', 0])]['jumlah'].sum()
        if len(val_0) > 0 and (val_0[0] > 0 or val_other_sum > 0):
            print(f"Periode {p} | {c:6s}: Nilai di baris '0' = {val_0[0]:10.2f} | Sum dari kabupaten lain = {val_other_sum:10.2f} | Selisih = {val_0[0] - val_other_sum:.2f}")

print("\n" + "=" * 80)
print("B. STRUKTUR ID DAN MENGAPA 7 KOTA TERDUPLIKASI TIAP BULAN")
print("=" * 80)
m1 = df[df['periode_update'] == '2020-01']
# Urutkan berdasarkan id
unique_entries = m1[['id', 'kode_kabupaten_kota', 'nama_kabupaten_kota']].drop_duplicates().sort_values(by='id')
print(f"Total entitas di 2020-01: {len(unique_entries)} entitas")
print(unique_entries.to_string())

print("\n" + "=" * 80)
print("C. TOTAL JUMLAH DATA TERDUPLIKAT (TOTAL ROWS, ROWS TERKENA)")
print("=" * 80)
key_cols = ['nama_kabupaten_kota', 'periode_update', 'kategori']
# Duplikasi eksak
exact_dups = df.duplicated()
print(f"Duplikasi eksak seluruh kolom: {exact_dups.sum()}")

# Duplikasi pada kunci bisnis (kabupaten, periode, kategori)
dup_keys = df.duplicated(subset=key_cols, keep=False)
print(f"Baris yang terlibat duplikasi kunci bisnis: {dup_keys.sum():,} baris ({dup_keys.sum()/len(df)*100:.1f}%)")

# Cek apakah salah satu baris duplikat selalu memiliki jumlah=0 sedangkan yang lain memiliki nilai aktual
diff_records = []
for (k, p, c), grp in df[dup_keys].groupby(key_cols):
    if grp['jumlah'].nunique() > 1:
        diff_records.append({
            'kab': k,
            'periode': p,
            'kategori': c,
            'id_1': grp.iloc[0]['id'],
            'val_1': grp.iloc[0]['jumlah'],
            'id_2': grp.iloc[1]['id'],
            'val_2': grp.iloc[1]['jumlah'],
            'max_val': grp['jumlah'].max()
        })
diff_df = pd.DataFrame(diff_records)
print(f"Kasus duplikasi dengan nilai berbeda (konflik): {len(diff_df)}")
print(diff_df.to_string())

print("\n" + "=" * 80)
print("D. ANALISIS DATA KOSONG (0.0 HA) MENURUT KABUPATEN DAN TAHUN")
print("=" * 80)
# Cek kabupaten mana saja yang PERNAH melaporkan kekeringan (>0 ha) vs TIDAK PERNAH (100% kosong)
kab_summary = df[~df['nama_kabupaten_kota'].isin(['0', 0])].groupby('nama_kabupaten_kota')['jumlah'].agg(
    total_laporan='count',
    laporan_nol=lambda x: (x == 0).sum(),
    laporan_ada_dampak=lambda x: (x > 0).sum(),
    total_ha='sum',
    max_ha='max'
).sort_values(by='total_ha', ascending=False)
print(kab_summary.to_string())

print("\n" + "=" * 80)
print("E. KABUPATEN DENGAN 100% DATA KOSONG (TIDAK PERNAH ADA DAMPAK KEKERINGAN TERCATAT)")
print("=" * 80)
zero_kabs = kab_summary[kab_summary['total_ha'] == 0]
print(f"Jumlah Kabupaten/Kota dengan 0 ha sepanjang 2020-2026: {len(zero_kabs)} dari {len(kab_summary)}")
print(zero_kabs.index.tolist())

print("\n" + "=" * 80)
print("F. DETAIL KEKERINGAN TAHUN 2023 (EL NINO KUAT): PERINGKAT KABUPATEN")
print("=" * 80)
df_2023_clean = df[(df['tahun'] == 2023) & (~df['nama_kabupaten_kota'].isin(['0', 0]))]
# jika duplikat, ambil max
df_2023_dedup = df_2023_clean.groupby(['nama_kabupaten_kota', 'periode_update', 'kategori'])['jumlah'].max().reset_index()

padi_2023 = df_2023_dedup[df_2023_dedup['kategori'] == 'PADI'].groupby('nama_kabupaten_kota')['jumlah'].agg(
    bulan_terdampak=lambda x: (x > 0).sum(),
    total_luas_ha='sum',
    max_bulan_ha='max'
).sort_values(by='total_luas_ha', ascending=False)

print("Peringkat Luas Kekeringan PADI Tahun 2023:")
print(padi_2023[padi_2023['total_luas_ha'] > 0].to_string())

print("\nPeringkat Luas Kekeringan JAGUNG Tahun 2023:")
jagung_2023 = df_2023_dedup[df_2023_dedup['kategori'] == 'JAGUNG'].groupby('nama_kabupaten_kota')['jumlah'].agg(
    bulan_terdampak=lambda x: (x > 0).sum(),
    total_luas_ha='sum',
    max_bulan_ha='max'
).sort_values(by='total_luas_ha', ascending=False)
print(jagung_2023[jagung_2023['total_luas_ha'] > 0].to_string())
