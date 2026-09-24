import pandas as pd
import numpy as np

csv_path = r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr.csv'
df = pd.read_csv(csv_path)

# 1. Filter out baris '0' (Total Provinsi)
df_clean = df[~df['nama_kabupaten_kota'].isin(['0', 0])].copy()

# Mapping resmi Kemendagri 29 Kabupaten (1-29) dan 9 Kota (30-38)
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

rectified_rows = []
for p, p_df in df_clean.groupby('periode_update'):
    unique_ids = sorted(p_df['id'].unique())
    if len(unique_ids) == 38:
        id_to_rank = {uid: rank + 1 for rank, uid in enumerate(unique_ids)}
        for idx, row in p_df.iterrows():
            rank = id_to_rank[row['id']]
            true_name, true_code = kemendagri_map[rank]
            r = row.to_dict()
            r['kode_kabupaten_kota'] = true_code
            r['nama_kabupaten_kota'] = true_name
            rectified_rows.append(r)

df_out = pd.DataFrame(rectified_rows)
# Reorder columns standardly
cols_order = ['id', 'id_index', 'kode_provinsi', 'nama_provinsi', 'kode_kabupaten_kota', 'nama_kabupaten_kota', 'periode_update', 'tahun', 'kategori', 'jumlah', 'satuan']
df_out = df_out[cols_order].sort_values(by=['periode_update', 'kode_kabupaten_kota', 'kategori'])

out_csv = r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr_clean.csv'
df_out.to_csv(out_csv, index=False)
print(f"[OK] Clean rectified dataset exported to: {out_csv}")
print(f"Total rows: {len(df_out):,}, Duplicates: {df_out.duplicated(subset=['nama_kabupaten_kota', 'periode_update', 'kategori']).sum()}")
