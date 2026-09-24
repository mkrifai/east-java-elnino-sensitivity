import pandas as pd
df = pd.read_csv(r'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr.csv')

sub_0 = df[df['nama_kabupaten_kota'].isin(['0', 0])]
print("Verifying if '0' is the provincial total row for each period & crop:")

mismatches = 0
matches = 0

for (p, c), grp in sub_0.groupby(['periode_update', 'kategori']):
    val_0 = grp['jumlah'].values[0]
    
    # Sum of other entities in that period & crop
    # Note: need to handle duplicate kota as well!
    other = df[(df['periode_update'] == p) & (df['kategori'] == c) & (~df['nama_kabupaten_kota'].isin(['0', 0]))]
    
    # If we take max by entity name (to deduplicate the duplicate kota)
    other_dedup = other.groupby('nama_kabupaten_kota')['jumlah'].max().sum()
    other_raw = other['jumlah'].sum()
    
    if val_0 > 0:
        print(f"Periode {p} | {c:7s} -> Val '0': {val_0:9.2f} | Raw other sum: {other_raw:9.2f} | Dedup other sum: {other_dedup:9.2f}")
        if abs(val_0 - other_dedup) < 0.05:
            matches += 1
        else:
            mismatches += 1

print(f"\nTotal non-zero periods checked: {matches + mismatches}")
print(f"Exact matches with deduplicated county sum: {matches}")
print(f"Mismatches: {mismatches}")
