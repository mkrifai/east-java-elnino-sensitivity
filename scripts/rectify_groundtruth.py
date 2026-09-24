import pandas as pd
import numpy as np

csv_path = r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr.csv'
df = pd.read_csv(csv_path)

print("======================================================================")
print("ALGORITMA REKONSTRUKSI DATA BERSIH (DATA CLEANING & RECTIFICATION)")
print("======================================================================")

# 1. Filter out baris '0' (Total Provinsi)
df_clean = df[~df['nama_kabupaten_kota'].isin(['0', 0])].copy()

# 2. Identifikasi posisi entitas per periode update untuk membetulkan nama 7 Kabupaten
# Mapping resmi 29 Kabupaten (posisi 1-29) dan 9 Kota (posisi 30-38)
kemendagri_map = {
    1: ('KABUPATEN PACITAN', 3501),
    2: ('KABUPATEN PONOROGO', 3502),
    3: ('KABUPATEN TRENGGALEK', 3503),
    4: ('KABUPATEN TULUNGAGUNG', 3504),
    5: ('KABUPATEN BLITAR', 3505),
    6: ('KABUPATEN KEDIRI', 3506),
    7: ('KABUPATEN MALANG', 3507),
    8: ('KABUPATEN LUMAJANG', 3508),
    9: ('KABUPATEN JEMBER', 3509),
    10: ('KABUPATEN BANYUWANGI', 3510),
    11: ('KABUPATEN BONDOWOSO', 3511),
    12: ('KABUPATEN SITUBONDO', 3512),
    13: ('KABUPATEN PROBOLINGGO', 3513),
    14: ('KABUPATEN PASURUAN', 3514),
    15: ('KABUPATEN SIDOARJO', 3515),
    16: ('KABUPATEN MOJOKERTO', 3516),
    17: ('KABUPATEN JOMBANG', 3517),
    18: ('KABUPATEN NGANJUK', 3518),
    19: ('KABUPATEN MADIUN', 3519),
    20: ('KABUPATEN MAGETAN', 3520),
    21: ('KABUPATEN NGAWI', 3521),
    22: ('KABUPATEN BOJONEGORO', 3522),
    23: ('KABUPATEN TUBAN', 3523),
    24: ('KABUPATEN LAMONGAN', 3524),
    25: ('KABUPATEN GRESIK', 3525),
    26: ('KABUPATEN BANGKALAN', 3526),
    27: ('KABUPATEN SAMPANG', 3527),
    28: ('KABUPATEN PAMEKASAN', 3528),
    29: ('KABUPATEN SUMENEP', 3529),
    30: ('KOTA KEDIRI', 3571),
    31: ('KOTA PROBOLINGGO', 3574),
    32: ('KOTA PASURUAN', 3575),
    33: ('KOTA MADIUN', 3577),
    34: ('KOTA BATU', 3579),
    35: ('KOTA BLITAR', 3572),
    36: ('KOTA MALANG', 3573),
    37: ('KOTA MOJOKERTO', 3576),
    38: ('KOTA SURABAYA', 3578),
}

# Verifikasi perbaikan
rectified_rows = []
for p, p_df in df_clean.groupby('periode_update'):
    # Ambil unique id secara berurutan
    unique_ids = sorted(p_df['id'].unique())
    # jika ada 38 id
    if len(unique_ids) == 38:
        id_to_rank = {uid: rank + 1 for rank, uid in enumerate(unique_ids)}
        for idx, row in p_df.iterrows():
            rank = id_to_rank[row['id']]
            true_name, true_code = kemendagri_map[rank]
            r = row.to_dict()
            r['nama_kabupaten_kota_asli'] = r['nama_kabupaten_kota']
            r['nama_kabupaten_kota_rectified'] = true_name
            r['kode_kabupaten_kota_rectified'] = true_code
            r['entity_rank'] = rank
            rectified_rows.append(r)
    else:
        print(f"Warning: Periode {p} has {len(unique_ids)} IDs")

df_rect = pd.DataFrame(rectified_rows)
print(f"Total baris yang berhasil di-rectify: {len(df_rect):,}")

# Cek berapa baris yang nama/kodenya berubah
changed_mask = df_rect['nama_kabupaten_kota_asli'] != df_rect['nama_kabupaten_kota_rectified']
print(f"Baris yang salah nama (Kota vs Kabupaten) dan berhasil dibetulkan: {changed_mask.sum():,} baris")
print("Contoh baris yang dibetulkan:")
print(df_rect[changed_mask][['periode_update', 'id', 'nama_kabupaten_kota_asli', 'nama_kabupaten_kota_rectified', 'kategori', 'jumlah']].head(10).to_string())

# Cek apakah sekarang masih ada duplikat kunci (nama_rectified, periode_update, kategori)?
dup_after = df_rect.duplicated(subset=['nama_kabupaten_kota_rectified', 'periode_update', 'kategori'], keep=False)
print(f"\nDuplikasi setelah perbaikan nama entitas: {dup_after.sum()} baris (HARUS 0!)")

print("\n" + "=" * 80)
print("REKAPITULASI SETELAH PEMBERSIHAN DATA (CLEAN BENCHMARK)")
print("=" * 80)
# Cek summary per kabupaten setelah rectified
kab_stats = df_rect.groupby('nama_kabupaten_kota_rectified')['jumlah'].agg(
    total_laporan='count',
    laporan_ada_dampak=lambda x: (x > 0).sum(),
    total_ha='sum',
    max_ha='max'
).sort_values(by='total_ha', ascending=False)

print(kab_stats.to_string())

print("\n" + "=" * 80)
print("CROSS-CHECK DENGAN MODEL LSI / ASI PORTFOLIO KITA")
print("=" * 80)
# Load M6/M7 ranking
import json
with open('outputs/m7_validation_statistics.json', 'r') as f:
    m7_data = json.load(f)

# Buat komparasi
print("Top 10 Kabupaten Terdampak Kekeringan Terluas (Data Resmi Dinas Pertanian Jatim):")
for i, (name, r) in enumerate(kab_stats.head(15).iterrows(), 1):
    print(f"{i:2d}. {name:25s} | Total: {r['total_ha']:9.2f} ha | Max bln: {r['max_ha']:8.2f} ha | Bulan terdampak: {int(r['laporan_ada_dampak']):2d}")
