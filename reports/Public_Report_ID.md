# Laporan Publik: Memetakan Sensitivitas Lanskap Jawa Timur terhadap El Niño
## Analisis Multi-Sensor Observasi Bumi 25 Tahun (2001–2025) untuk Ketahanan Pangan dan Adaptasi Iklim

---

**Halaman Sampul dan Metadata**

| Atribut | Detail |
|:---|:---|
| **Judul** | Memetakan Sensitivitas Lanskap Jawa Timur terhadap El Niño: Analisis Multi-Sensor Observasi Bumi 25 Tahun (2001–2025) untuk Ketahanan Pangan dan Adaptasi Iklim |
| **Penulis** | Mochamad Khoirul Rifai |
| **Afiliasi** | Departemen Fisika, Universitas Negeri Malang |
| **Tanggal terbit** | September 2026 |
| **Versi** | 0.9 (Draft / Pre-release) |
| **DOI** | *(Akan diterbitkan melalui Zenodo)* |
| **Lisensi** | Kode: MIT License; Data & Laporan: CC BY 4.0 International |
| **Repositori** | [github.com/mkrifai/east-java-elnino-sensitivity](https://github.com/mkrifai/east-java-elnino-sensitivity) |

> **Pernyataan Independensi Akademik & Penafian Afiliasi (Institutional Disclaimer):**  
> Laporan publik ini merupakan karya riset independen dan **tidak mewakili pandangan formal, posisi resmi, maupun kebijakan institusional dari unit kerja atau afiliasi institusi penulis saat ini (Departemen Fisika, Universitas Negeri Malang)** maupun instansi pemerintah manapun. Penelitian ini diselenggarakan murni sebagai **bentuk tanggung jawab akademik, integritas keilmuan, dan dedikasi ilmiah** dalam bidang fisika kebumian, pemodelan komputasi spasial, dan sains observasi bumi yang ditekuni penulis untuk kemaslahatan publik dan ketahanan iklim masyarakat. Penulis tidak menerima pendanaan eksternal dan tidak memiliki konflik kepentingan. Seluruh metodologi, analisis data, temuan empiris, dan rekomendasi yang termuat di dalamnya merupakan tanggung jawab intelektual dan pribadi penulis sepenuhnya.

---

## Ringkasan Eksekutif dan Pesan Kunci

### Pesan Kunci

1. **35,1% wilayah Jawa Timur terdampak kekeringan parah di setiap episode El Niño** — bukan secara acak, melainkan di koridor yang sama berulang kali.
2. **Enam kabupaten menanggung 92,5% kerusakan pertanian** selama El Niño 2023–2024 (total 41.576 hektar).
3. **Sinyal peringatan dini tersedia 4–6 minggu** sebelum kerusakan terlihat, melalui pemantauan kelembaban kanopi satelit.
4. **Model kerentanan satelit terkonfirmasi** oleh data bencana resmi BPBD (r = 0,933; 87% varian terjelaskan).
5. **Diperlukan reformasi alokasi anggaran darurat** menggunakan formula berbasis bukti, bukan distribusi politis merata.

### Ringkasan

Jawa Timur adalah provinsi penghasil beras terbesar Indonesia, namun secara berulang mengalami kekeringan pertanian akibat El Niño. Riset ini merekonstruksi 25 tahun data satelit multi-sensor pada resolusi 1 km untuk memetakan rantai respons biofisik lengkap — dari defisit curah hujan hingga eksposur pertanian — di seluruh 38 kabupaten/kota. Temuan utama menunjukkan bahwa dampak El Niño bersifat deterministik secara spasial dan dapat dideteksi lebih awal, membuka peluang transformasi dari respons reaktif ke kesiapan preventif.

---

## 1. Pendahuluan

### 1.1 Latar Belakang

El Niño-Southern Oscillation (ENSO) merupakan pengendali utama variabilitas iklim antar-tahunan di Indonesia. Selama fase El Niño, perpindahan anomali konveksi atmosfer ke Pasifik Tengah dan Timur menyebabkan subsidensi atmosfer, supresi konveksi, dan defisit curah hujan signifikan di Kepulauan Indonesia.

Jawa Timur — dengan luas baku sawah lebih dari 1,14 juta hektar dan produksi gabah tahunan melebihi 10 juta ton — menjadi sangat rentan terhadap anomali iklim terkait ENSO. Namun, **respons lanskap terhadap El Niño tidak homogen**: dua wilayah dengan penurunan curah hujan yang sama dapat menunjukkan dampak permukaan lahan yang sangat berbeda, bergantung pada topografi, tipe tanah, akses irigasi, tutupan lahan, dan sistem pertanian.

### 1.2 Tujuan

Riset ini bertujuan menjawab tiga pertanyaan:

1. **Bagaimana El Niño memengaruhi curah hujan dan kondisi permukaan lahan** di berbagai lanskap heterogen Jawa Timur? *(RQ1)*
2. **Bagaimana magnitude dan waktu respons permukaan lahan** bervariasi di antara rezim lanskap yang berbeda? *(RQ2)*
3. **Karakteristik lanskap apa yang menjelaskan heterogenitas spasial** sensitivitas El Niño, dan bagaimana pola ini dapat menginformasikan kesiapan kekeringan terarah? *(RQ3)*

### 1.3 Ruang Lingkup

- **Wilayah studi:** Provinsi Jawa Timur (38 kabupaten/kota; ~47.800 km²)
- **Periode analisis:** 2001–2025 (25 tahun)
- **Resolusi spasial:** 1 km (*regular grid*)
- **Episode El Niño yang dianalisis:** 8 kejadian (2002, 2004, 2006, 2009, 2014, 2015, 2018, 2023)
- **Tahun baseline ENSO-netral:** 6 tahun (2001, 2003, 2012, 2013, 2019, 2025; |ONI| < 0,5°C)

---

## 2. Metodologi

### 2.1 Desain Penelitian

Riset ini menggunakan pendekatan **analisis observasi bumi retrospektif** berbasis *cloud computing* (Google Earth Engine Python API). Rantai kausal biofisik direkonstruksi secara sekuensial:

```
Bulan 0    Curah hujan ↓
               │
Bulan 1    Kelembaban tanah ↓
               │
Bulan 2    Suhu permukaan lahan ↑
               │
Bulan 2–3  Kelembaban kanopi (NDMI) ↓
               │
Bulan 3    Kehijauan vegetasi (NDVI) ↓
               │
Bulan 4+   Eksposur pertanian → gagal panen (puso)
```

### 2.2 Sumber Data

| No | Dataset | Sumber | Resolusi | Periode | Variabel |
|:---:|:---|:---|:---|:---|:---|
| 1 | CHIRPS v2.0 | UCSB/CHG | 0,05° (~5,5 km) | 2001–2025 | Curah hujan bulanan |
| 2 | ERA5-Land | ECMWF | 0,1° (~11 km) | 2001–2025 | Kelembaban tanah (0–28 cm) |
| 3 | MODIS MOD11A2 | NASA Terra | 1 km | 2001–2025 | Suhu permukaan lahan (LST) |
| 4 | MODIS MOD09A1 | NASA Terra | 500 m → 1 km | 2001–2025 | NDVI, EVI, NDMI |
| 5 | NASA GPM IMERG V07 | NASA | 0,1° | 2001–2025 | Curah hujan (validasi sensor) |
| 6 | ESA WorldCover 2021 | ESA | 10 m | 2021 | Tutupan lahan / densitas sawah |
| 7 | BPS Jawa Timur | BPS | Kabupaten | 2015–2024 | Statistik pertanian |
| 8 | Dinas Pertanian Jatim | Pemprov | Kabupaten/bulan | 2015–2024 | Luas dampak kekeringan |
| 9 | BPBD Jawa Timur | Pemprov | Kabupaten/desa | 2023 | Kejadian darurat kekeringan |

### 2.3 Analisis

Analisis dilaksanakan dalam 12 fase (*milestone*) yang tersusun hierarkis:

| Fase | Milestone | Deskripsi |
|:---:|:---|:---|
| 1–2 | M1–M2 | Kerangka riset dan respons iklim (anomali curah hujan CHIRPS) |
| 3–4 | M3 | Respons fisik (kelembaban tanah ERA5 dan suhu permukaan MODIS LST) |
| 5–7 | M4 | Respons vegetasi (NDVI, EVI, NDMI dari MODIS Terra) |
| 8–9 | M5 | Indeks Sensitivitas Lanskap (LSI) dan klasterisasi 5 rezim |
| 10–11 | M6 | Indeks Sensitivitas Pertanian (ASI), hotspot, dan 4 zona kebijakan |
| 12 | M7 | Validasi multi-sumber, kuantifikasi ketidakpastian, dan *ground truth* |

**Indeks Sensitivitas Lanskap (LSI)** dihitung sebagai komposit tertimbang dari anomali terstandarisasi curah hujan, kelembaban tanah, suhu permukaan, dan kelembaban/kehijauan kanopi, dinormalisasi ke skala 0–1 (0 = paling tangguh; 1 = paling rentan).

**Indeks Sensitivitas Pertanian (ASI)** menggabungkan LSI dengan densitas lahan pertanian (dari ESA WorldCover 10 m) untuk mengidentifikasi wilayah dengan kerentanan iklim tinggi *dan* eksposur pertanian tinggi secara bersamaan.

**Klasterisasi 5 rezim** menggunakan algoritma unsupervised Weka k-Means untuk mengelompokkan piksel 1 km berdasarkan profil multi-dimensi respons biofisiknya.

### 2.4 Validasi

Validasi dilakukan dalam empat tahap:

1. **Validasi silang sensor iklim:** CHIRPS v2.0 (IR/gauge) vs NASA GPM IMERG V07 (radar/microwave) pada grid 15 km (n = 280 titik). Hasil: r = 0,745; konsistensi 83,1%.
2. **Validasi silang indeks vegetasi:** NDVI vs EVI (formulasi spektral berbeda). Hasil: r = 0,872; kesepakatan anomali 87,2%.
3. **Validasi *ground truth* BPBD 2023:** LSI vs desa krisis air BPBD (kohort benchmark n = 9 kabupaten). Hasil: Pearson r = 0,933; Spearman ρ = 0,950; p-spasial = 0,0074.
4. **Validasi *ground truth* pertanian 2023–2024:** ASI vs luas dampak kekeringan Dinas Pertanian (sensus n = 38 kabupaten/kota). Hasil: r = 0,505; p = 0,001.

### 2.5 Pertimbangan Etis

- **Tidak ada data manusia individual** yang dikumpulkan. Seluruh data bersifat agregat (tingkat kabupaten/desa) dan berasal dari sumber publik.
- **Tidak ada persetujuan etik (*ethical approval*)** yang diperlukan karena riset tidak melibatkan subjek manusia secara langsung.
- **Perlindungan data:** Data sensitif tentang lokasi desa rentan disajikan dalam bentuk agregat kabupaten. Tidak ada nama atau identitas individu yang dipublikasikan.
- **Prinsip *do no harm*:** Laporan ini menghindari stigmatisasi wilayah tertentu. Identifikasi kabupaten rentan bertujuan mengarahkan bantuan, bukan mendiskreditkan pemerintah daerah.

---

## 3. Temuan dan Pembahasan

### 3.1 Respons Iklim: Curah Hujan Menurun Drastis Saat El Niño

Rata-rata 8 episode El Niño menunjukkan:
- **Defisit curah hujan musim kering:** -151 mm (-45,4%) pada puncak SON (September–November)
- **Compound event** (El Niño + IOD+) memperdalam defisit tambahan -21,5 mm (catatan: belum signifikan secara statistik karena n kecil, p = 0,77)
- Standardized anomaly: Z = -0,83 (rata-rata); tiga kejadian terparah (2006: Z = -1,43; 2015: Z = -1,10; 2023: Z = -1,01) menembus ambang kekeringan meteorologis

**Sumber data:** CHIRPS v2.0 divalidasi silang dengan NASA GPM IMERG V07 (konsistensi 83,1%; r = 0,745 pada grid regular 15 km).

### 3.2 Respons Fisik: Tanah Mengering dan Suhu Melonjak

- **Kelembaban tanah:** Turun rata-rata -0,043 m³/m³ (pure El Niño) hingga -0,053 m³/m³ (compound event)
- **Suhu permukaan lahan (LST):** Melonjak +1,71°C rata-rata; puncak +2,8°C di dataran rendah utara
- **Decoupling evaporatif:** Tanah yang sangat kering tidak lagi mampu mendinginkan permukaan melalui evaporasi, menyebabkan lonjakan suhu yang tidak proporsional

### 3.3 Respons Vegetasi: Kelembaban Kanopi Turun Lebih Awal dari Kehijauan

- **NDMI (kelembaban kanopi):** Z = -0,84 — turun 30–45 hari lebih awal dari NDVI
- **NDVI (kehijauan daun):** Z = -0,66 — terlihat setelah kerusakan internal daun sudah terjadi
- **Implikasi operasional:** Jendela 30–45 hari antara sinyal NDMI dan kerusakan NDVI merupakan peluang intervensi yang belum dimanfaatkan

### 3.4 Indeks Sensitivitas Lanskap: Lima Rezim Spasial

Klasterisasi unsupervised (Weka k-Means, k = 5) menghasilkan lima rezim lanskap yang koheren:

| Rezim | Deskripsi | % Wilayah | Ciri Dominan |
|:---:|:---|:---:|:---|
| 1 | Dataran rendah pesisir utara | 22,3% | Kekeringan parah, infrastruktur irigasi ujung |
| 2 | Lembah aluvial Brantas/Bengawan Solo | 19,5% | Kerentanan sedang-tinggi, sawah teknis |
| 3 | Peralihan lereng menengah | 23,1% | Campuran tegalan dan sawah tadah hujan |
| 4 | Dataran tinggi vulkanik | 20,0% | Ketangguhan sedang, hutan dan hortikultura |
| 5 | Hutan pegunungan dan kawasan lindung | 15,2% | Paling tangguh, fungsi resapan air |

**Zona robust kerentanan tinggi:** 35,1% wilayah daratan (LSI ≥ 0,60, CV ≤ 0,45) menunjukkan kerentanan parah yang konsisten di seluruh 8 episode El Niño.

### 3.5 Eksposur Pertanian: 10 Kabupaten Prioritas Ekstrem

Dengan mengalikan LSI dengan densitas lahan pertanian, dihasilkan **Indeks Sensitivitas Pertanian (ASI)**. Peringkat 10 teratas:

| Peringkat | Kabupaten | LSI | Densitas Sawah | ASI | Hotspot Kritis (%) | Tier |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | Lamongan | 0,71 | 70,2% | 0,479 | 51,5% | Extreme (Tier 1) |
| 2 | Gresik | 0,60 | 45,7% | 0,357 | 36,9% | Extreme (Tier 1) |
| 3 | Bojonegoro | 0,76 | 44,7% | 0,339 | 39,5% | Extreme (Tier 1) |
| 4 | Jombang | 0,68 | 49,4% | 0,335 | 33,1% | Extreme (Tier 1) |
| 5 | Nganjuk | 0,65 | 43,1% | 0,293 | 32,4% | Extreme (Tier 1) |
| 6 | Tuban | 0,67 | 46,0% | 0,291 | 28,3% | Extreme (Tier 1) |
| 7 | Kediri | 0,60 | 43,9% | 0,285 | 25,3% | Extreme (Tier 1) |
| 8 | Mojokerto | 0,62 | 40,5% | 0,285 | 29,4% | Extreme (Tier 1) |
| 9 | Ngawi | 0,76 | 36,9% | 0,281 | 34,5% | Extreme (Tier 1) |
| 10 | Magetan | 0,70 | 38,1% | 0,260 | 27,9% | Extreme (Tier 1) |

### 3.6 Validasi Empiris: Model Terkonfirmasi oleh Data Bencana

**Validasi 1 — BPBD 2023 (kohort darurat, n = 9):**
- Pearson r = 0,933 (R² = 0,870)
- Spearman ρ = 0,950
- Signifikan setelah koreksi autokorelasi spasial (p = 0,0074, N-eff = 5,90)
- 273 dari 279 desa krisis (97,8%) berada di kabupaten LSI ≥ 0,55

**Validasi 2 — Dinas Pertanian 2023–2024 (sensus penuh, n = 38):**
- Pearson r = 0,505 (p = 0,001)
- Spearman ρ sesuai tier risiko
- 6 kabupaten Quadrant I (kerusakan > 3.000 ha DAN intensitas > 3,65%) menampung 92,5% total kerusakan

### 3.7 Paradoks Pacitan: Kerentanan Bersifat Multi-Dimensi

Kabupaten Pacitan — klasifikasi Tier 4 (Low/Buffered) dalam model musim kering — mencatat **kerusakan 43,43% seluruh basis sawahnya**. Ini terjadi karena:
- 97,3% kerusakan (5.719 ha) terjadi di **Januari 2024** akibat keterlambatan onset monsun barat (MT-1)
- Selama musim kering klasik (SON 2023), kerusakan hanya 28 ha
- Pacitan memiliki Location Quotient 11,90× — hampir 12 kali rata-rata provinsi

**Implikasi:** Satu metrik kerentanan tidak cukup. Diperlukan pendekatan multi-tier yang membedakan volume absolut, intensitas lokal, dan keadilan antar-wilayah.

---

## 4. Kesimpulan dan Rekomendasi

### 4.1 Kesimpulan

1. Sensitivitas lanskap Jawa Timur terhadap El Niño **bersifat spasial deterministik** — koridor kerentanan tinggi terbentuk secara konsisten di setiap episode.
2. Rantai kausal biofisik (hujan → tanah → suhu → kanopi → panen) berjalan secara **berurutan dan dapat diprediksi**, dengan jendela intervensi 30–45 hari antara sinyal kelembaban kanopi dan kegagalan panen.
3. Dampak pertanian bersifat **hyper-terkonsentrasi** — 92,5% kerusakan terjadi di 6 dari 38 kabupaten/kota.
4. Evaluasi keparahan harus bersifat **multi-dimensional**: volume absolut (untuk ketahanan pangan makro), intensitas lokal (untuk perlindungan penghidupan), dan Location Quotient (untuk keadilan fiskal).

### 4.2 Rekomendasi

| Prioritas | Rekomendasi | Pelaksana | Tenggat | Indikator Keberhasilan |
|:---:|:---|:---|:---|:---|
| 1 | Realokasi BTT dengan formula 60/40 Hibrida | Gubernur, BPKAD | Sebelum April | Deviasi distribusi ≤ 10% dari formula |
| 2 | Integrasi NDMI sebagai pemicu peringatan dini resmi | BPBD, Pusdalops | 6 bulan | Waktu respons ≤ 14 hari dari deteksi |
| 3 | Subsidi penuh AUTP di 6 kabupaten prioritas | Dinas Pertanian, Jasindo | Saat Advisory BMKG | Cakupan ≥ 80% petani terdaftar |
| 4 | Kuota gilir irigasi saat compound event | BBWS Brantas & Bengawan Solo | Segera saat forecast | Tidak ada kekurangan air sawah hilir |

---

## 5. Keterbatasan

1. **Resolusi spasial 1 km:** Memadai untuk perencanaan kabupaten/kecamatan; tidak cukup untuk keputusan tingkat petak sawah. Diperlukan Sentinel-2 (10 m) untuk implementasi presisi.

2. **Validasi kohort *purposive*:** Korelasi tinggi (r = 0,933) diperoleh dari 9 kabupaten pelapor resmi, bukan sampel acak seluruh provinsi. Kabupaten non-pelapor (baik karena tidak terdampak maupun karena keterbatasan kapasitas administrasi) tidak termasuk.

3. **Ukuran sampel compound event kecil:** Hanya 3 dari 8 episode bersifat compound (El Niño + IOD+). Efek amplifikasi teramati secara konsisten tetapi belum signifikan secara statistik (p = 0,77).

4. **Pembaur yang tidak dimodelkan:** Kapasitas administratif pelaporan BPBD, kepadatan penduduk, infrastruktur air *baseline*, dan perilaku adaptif petani merupakan faktor yang berpotensi memengaruhi korelasi tetapi tidak dikendalikan.

5. **Asumsi stasioneritas:** Analisis berbasis data historis 2001–2025 mengasumsikan hubungan iklim-lanskap relatif stabil. Perubahan iklim jangka panjang (pergeseran pola monsun, pemanasan global) di luar periode ini belum diperhitungkan.

6. **Biaya implementasi bersifat estimasi:** Angka Rp 25–40 miliar/tahun belum melewati analisis biaya-manfaat formal.

---

## 6. Dampak, Capaian, dan Akuntabilitas

### 6.1 Capaian Riset

| Aspek | Detail |
|:---|:---|
| **Produk geospasial** | 51+ GeoTIFF resolusi 1 km (anomali iklim, kelembaban tanah, LST, NDVI, NDMI, LSI, ASI, hotspot) |
| **Visualisasi** | 10+ figur publikasi-grade (300 DPI) |
| **Laporan ilmiah** | 7 laporan teknis per milestone + 1 laporan validasi + 1 laporan benchmarking |
| **Kode sumber** | Seluruh *pipeline* terbuka di GitHub (Python, MIT License) |
| **Reprodusibilitas** | Setiap angka dalam laporan dapat ditelusuri ke skrip dan dataset spesifik |

### 6.2 Integritas Keilmuan dan Independensi Institusional

Riset ini dilaksanakan sebagai wujud komitmen etika keilmuan dan tanggung jawab akademik dalam bidang fisika dan pemodelan geospasial. Penulis menegaskan bahwa:
- Dokumen ini **bukan merupakan produk kebijakan resmi atau dokumen representasi formal dari Departemen Fisika, Universitas Negeri Malang**.
- Seluruh interpretasi dan rekomendasi dirumuskan secara independen berdasarkan data empiris dan literatur ilmiah terbuka, tanpa intervensi pihak luar.
- Penulis bertanggung jawab penuh atas segala klaim analitis dan metodologis yang disajikan.

### 6.3 Penggunaan Dana

Riset ini sepenuhnya didanai secara mandiri (*self-funded*) oleh peneliti. Tidak ada dana publik atau donor yang digunakan. Biaya operasional meliputi:
- Akses internet dan komputasi lokal
- Lisensi Google Earth Engine (gratis untuk riset)
- Tidak ada biaya perjalanan lapangan (riset berbasis *remote sensing*)

### 6.4 Rencana Diseminasi

| Kanal | Target Audiens | Timeline |
|:---|:---|:---|
| Repositori GitHub (*open-source*) | Komunitas riset, pengembang | Sudah tersedia |
| Zenodo DOI (arsip permanen) | Akademisi, sitasi formal | Setelah rilis final |
| Policy Brief (dokumen ini) | Pembuat kebijakan Pemprov Jatim | September 2026 |
| Public Summary | Masyarakat umum, media | September 2026 |
| Presentasi ke BPBD/Dinas Pertanian | Praktisi operasional | Dijadwalkan |

---

## 7. Lampiran

### Lampiran A: Daftar File Keluaran Utama

| Milestone | File | Deskripsi |
|:---|:---|:---|
| M2 | `outputs/m2_elnino_rainfall_anomalies.png` | Atlas anomali curah hujan 8 episode El Niño |
| M3 | `outputs/m3_physical_response.png` | Respons kelembaban tanah dan suhu permukaan |
| M4 | `outputs/m4_vegetation_response.png` | Respons NDVI, EVI, dan NDMI |
| M5 | `outputs/m5_landscape_sensitivity.png` | Indeks Sensitivitas Lanskap dan 5 rezim |
| M6 | `outputs/m6_agriculture_policy.png` | Indeks Sensitivitas Pertanian dan zona kebijakan |
| M7.1 | `outputs/m7_1_sensor_validation.png` | Validasi silang sensor (CHIRPS vs GPM, NDVI vs EVI) |
| M7.2 | `outputs/m7_2_uncertainty_groundtruth.png` | Validasi *ground truth* BPBD |
| M7.3 | `outputs/m7_3_ensemble_uncertainty.png` | Ketidakpastian *ensemble* 8 episode |
| M7.4 | `outputs/m7_4_agricultural_groundtruth.png` | Validasi pertanian empiris 2023–2024 |
| M7.5 | `outputs/m7_5_crop_loss_severity_framework.png` | Kerangka benchmarking keparahan multi-tier |

### Lampiran B: Klasifikasi Episode El Niño (2001–2025)

| Tahun | Intensitas | Peak ONI (°C) | IOD+ Bersamaan? | Tipe |
|:---|:---|:---|:---|:---|
| 2002–2003 | Moderate | ~1,3 | Tidak | El Niño murni |
| 2004–2005 | Weak | ~0,7 | Tidak | El Niño murni |
| 2006–2007 | Weak | ~0,9 | **Ya** | Compound (El Niño + IOD+) |
| 2009–2010 | Moderate | ~1,6 | Tidak | El Niño murni |
| 2014–2015 | Weak | ~0,6 | Tidak | El Niño murni |
| 2015–2016 | **Very Strong** | ~2,6 | Tidak | El Niño murni |
| 2018–2019 | Weak | ~0,8 | **Ya** | Compound (El Niño + IOD+) |
| 2023–2024 | **Strong** | ~2,0 | **Ya** | Compound (El Niño + IOD+) |

### Lampiran C: Glosarium

| Istilah | Penjelasan |
|:---|:---|
| **ASI** | *Agricultural Sensitivity Index* — indeks kerentanan pertanian (LSI × densitas sawah) |
| **AUTP** | *Asuransi Usaha Tani Padi* — asuransi tanaman padi bersubsidi pemerintah |
| **BPBD** | *Badan Penanggulangan Bencana Daerah* |
| **BTT** | *Belanja Tidak Terduga* — pos anggaran darurat bencana |
| **CHIRPS** | *Climate Hazards InfraRed Precipitation with Station* — produk curah hujan satelit |
| **Compound event** | Kejadian iklim gabungan (El Niño + IOD positif secara bersamaan) |
| **El Niño** | Pemanasan abnormal Samudera Pasifik Ekuatorial, menyebabkan kekeringan di Indonesia |
| **EVI** | *Enhanced Vegetation Index* — indeks vegetasi terkoreksi atmosfer |
| **IOD+** | *Indian Ocean Dipole positif* — anomali suhu Samudera Hindia yang memperkuat kekeringan |
| **LQ** | *Location Quotient* — rasio kerusakan lokal terhadap rata-rata provinsi |
| **LSI** | *Landscape Sensitivity Index* — indeks sensitivitas lanskap (0–1) |
| **LST** | *Land Surface Temperature* — suhu permukaan lahan dari satelit |
| **MODIS** | *Moderate Resolution Imaging Spectroradiometer* — sensor satelit NASA Terra/Aqua |
| **NDMI** | *Normalized Difference Moisture Index* — indeks kelembaban kanopi tanaman |
| **NDVI** | *Normalized Difference Vegetation Index* — indeks kehijauan vegetasi |
| **ONI** | *Oceanic Niño Index* — indikator El Niño berdasarkan anomali suhu Pasifik |
| **Puso** | Gagal panen total akibat kekeringan, banjir, atau serangan hama |

---

## 8. Daftar Pustaka

### Sumber Data Primer
1. Funk, C., et al. (2015). The Climate Hazards InfraRed Precipitation with Station data (CHIRPS). *Scientific Data*, 2, 150066.
2. Muñoz-Sabater, J., et al. (2021). ERA5-Land: A state-of-the-art global reanalysis dataset. *Earth System Science Data*, 13(9), 4349–4383.
3. Huffman, G. J., et al. (2020). NASA Global Precipitation Measurement (GPM) Integrated Multi-satellitE Retrievals for GPM (IMERG), Version 07. NASA.
4. Zanaga, D., et al. (2022). ESA WorldCover 10 m 2021 v200.
5. BPS Provinsi Jawa Timur. (2023). *Jawa Timur Dalam Angka 2023*. Badan Pusat Statistik.
6. Kementerian ATR/BPN. (2019). Keputusan Menteri ATR/BPN No. 686/SK-PG.03.03/XII/2019 tentang Penetapan Peta Luas Baku Sawah Nasional.

### Kerangka Kebijakan
7. Pemerintah RI. (2013). Undang-Undang No. 19 Tahun 2013 tentang Perlindungan dan Pemberdayaan Petani.
8. Pemerintah RI. (2019). Peraturan Presiden No. 39 Tahun 2019 tentang Satu Data Indonesia.
9. Pemerintah RI. (2022). Undang-Undang No. 27 Tahun 2022 tentang Pelindungan Data Pribadi.
10. United Nations. (2015). Sendai Framework for Disaster Risk Reduction 2015–2030.
11. UNFCCC. (2015). Paris Agreement.
12. United Nations. (2015). Transforming Our World: The 2030 Agenda for Sustainable Development (SDGs).

---

## 9. Informasi Kontak dan Cara Sitasi

**Penulis:** Mochamad Khoirul Rifai  
**Afiliasi:** Departemen Fisika, Universitas Negeri Malang  
**Email:** mochamadkhoirulrifai25@gmail.com  
**GitHub:** [@mkrifai](https://github.com/mkrifai)  
**Repositori:** [east-java-elnino-sensitivity](https://github.com/mkrifai/east-java-elnino-sensitivity)

**Cara sitasi:**
```
Rifai, M. K. (2026). Memetakan Sensitivitas Lanskap Jawa Timur terhadap El Niño:
Analisis Multi-Sensor Observasi Bumi 25 Tahun (2001–2025) untuk Ketahanan Pangan
dan Adaptasi Iklim. Laporan Publik v0.9, Departemen Fisika, Universitas Negeri Malang.
```

---

*Laporan ini disusun dengan komitmen terhadap transparansi, reprodusibilitas, dan akuntabilitas riset ilmiah untuk kepentingan publik.*
