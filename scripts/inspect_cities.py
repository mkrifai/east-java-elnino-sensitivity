import pandas as pd
df = pd.read_csv(r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr.csv')
m1 = df[df['periode_update'] == '2020-01']
unique_entries = m1[['id', 'kode_kabupaten_kota', 'nama_kabupaten_kota']].drop_duplicates().sort_values(by='id')
for _, r in unique_entries.iterrows():
    print(f"id: {int(r['id']):2d} | kode: {r['kode_kabupaten_kota']:6.0f} | nama: {r['nama_kabupaten_kota']}")
