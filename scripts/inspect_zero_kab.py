import pandas as pd
df = pd.read_csv(r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr.csv')

sub_0 = df[df['nama_kabupaten_kota'].isin(['0', 0])]
print(f"Total rows with nama_kabupaten_kota == '0': {len(sub_0)}")
print("Unique periods with '0':")
print(sub_0['periode_update'].value_counts().sort_index())

print("\nDetail of rows with '0':")
print(sub_0[['id', 'id_index', 'kode_kabupaten_kota', 'nama_kabupaten_kota', 'periode_update', 'kategori', 'jumlah', 'tahun']].to_string())
