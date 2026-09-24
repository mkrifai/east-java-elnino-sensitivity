import pandas as pd
df = pd.read_csv(r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr.csv')

print("Checking when KABUPATEN BLITAR/KEDIRI/MALANG/PROBOLINGGO/PASURUAN/MOJOKERTO/MADIUN appear:")
kab_names = [
    'KABUPATEN BLITAR', 'KABUPATEN KEDIRI', 'KABUPATEN MALANG', 
    'KABUPATEN PROBOLINGGO', 'KABUPATEN PASURUAN', 'KABUPATEN MOJOKERTO', 'KABUPATEN MADIUN'
]

sub = df[df['nama_kabupaten_kota'].isin(kab_names)]
print("Total rows:", len(sub))
print("Unique periods where they appear:")
print(sub['periode_update'].value_counts().sort_index())

print("\nWhat happened in those periods? (e.g. late 2025 or 2026?)")
for p in sub['periode_update'].unique():
    kabs_in_p = df[df['periode_update'] == p]['nama_kabupaten_kota'].unique()
    print(f"Period {p}: Total unique kabs = {len(kabs_in_p)}")
    has_kab_blitar = 'KABUPATEN BLITAR' in kabs_in_p
    has_kota_blitar = 'KOTA BLITAR' in kabs_in_p
    kota_blitar_count = (df[(df['periode_update'] == p) & (df['nama_kabupaten_kota'] == 'KOTA BLITAR')].shape[0])
    print(f"  has KAB BLITAR: {has_kab_blitar}, has KOTA BLITAR: {has_kota_blitar} (count rows: {kota_blitar_count})")
