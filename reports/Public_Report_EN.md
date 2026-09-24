# Public Report: Mapping the Spatial Sensitivity of East Java Landscapes to El Niño
## A 25-Year Multi-Sensor Earth Observation Analysis (2001–2025) for Food Security and Climate Adaptation

---

**Cover Page and Metadata**

| Attribute | Detail |
|:---|:---|
| **Title** | Mapping the Spatial Sensitivity of East Java Landscapes to El Niño: A 25-Year Multi-Sensor Earth Observation Analysis (2001–2025) for Food Security and Climate Adaptation |
| **Author** | Mochamad Khoirul Rifai |
| **Affiliation** | Department of Physics, Universitas Negeri Malang, Indonesia |
| **Date** | September 2026 |
| **Version** | 0.9 (Draft / Pre-release) |
| **DOI** | *(To be assigned via Zenodo upon final release)* |
| **License** | Code: MIT License; Data & Reports: CC BY 4.0 International |
| **Repository** | [github.com/mkrifai/east-java-elnino-sensitivity](https://github.com/mkrifai/east-java-elnino-sensitivity) |

> **Disclaimer:** This report presents findings from independent research and does not represent the official position of Universitas Negeri Malang, the Government of East Java Province, or any other institution. The author received no external funding and declares no conflicts of interest.

---

## Executive Summary and Key Messages

### Key Messages

1. **35.1% of East Java's land area suffers severe drought during every El Niño episode** — not randomly, but along the same spatial corridors repeatedly.
2. **Six regencies bear 92.5% of agricultural damage** during the 2023–2024 El Niño (total 41,576 hectares).
3. **Early warning signals are available 4–6 weeks** before visible damage, through satellite canopy moisture monitoring.
4. **The satellite vulnerability model is confirmed** by official BPBD disaster data (r = 0.933; 87% of variance explained).
5. **Emergency budget allocation reform is needed** using an evidence-based formula rather than politically equal distribution.

### Summary

East Java is Indonesia's largest rice-producing province, yet repeatedly suffers agricultural drought from El Niño. This study reconstructs 25 years of multi-sensor satellite data at 1 km resolution to map the complete biophysical response chain — from rainfall deficit to agricultural exposure — across all 38 regencies/municipalities. The core finding is that El Niño's impact is spatially deterministic and detectable in advance, opening the door for transformation from reactive response to preventive preparedness.

---

## 1. Introduction

### 1.1 Background

The El Niño-Southern Oscillation (ENSO) is the dominant mode of interannual climate variability in Indonesia. During El Niño phases, anomalous eastward displacement of the Indo-Pacific warm pool causes atmospheric subsidence, suppressed convection, and significant rainfall deficits across the Indonesian archipelago.

East Java — with over 1.14 million hectares of official paddy land and annual rice production exceeding 10 million metric tons — is acutely vulnerable to ENSO-related climate anomalies. However, **landscape response to El Niño is not homogeneous**: two areas experiencing the same rainfall reduction may exhibit vastly different land-surface impacts, depending on topography, soil type, irrigation access, land cover, and agricultural systems.

### 1.2 Objectives

This research addresses three questions:

1. **How does El Niño influence rainfall and land-surface conditions** across heterogeneous landscapes in East Java? *(RQ1)*
2. **How do the magnitude and timing of land-surface responses** vary among different landscape regimes? *(RQ2)*
3. **Which physical and agricultural landscape characteristics explain the spatial heterogeneity** of El Niño sensitivity, and how can these patterns inform geographically targeted drought preparedness? *(RQ3)*

### 1.3 Scope

- **Study area:** East Java Province (38 regencies/municipalities; ~47,800 km²)
- **Analysis period:** 2001–2025 (25 years)
- **Spatial resolution:** 1 km (regular grid)
- **El Niño episodes analysed:** 8 events (2002, 2004, 2006, 2009, 2014, 2015, 2018, 2023)
- **ENSO-neutral baseline years:** 6 years (2001, 2003, 2012, 2013, 2019, 2025; |ONI| < 0.5°C)

---

## 2. Methodology

### 2.1 Research Design

This study employs a **retrospective earth observation analysis** using cloud computing (Google Earth Engine Python API). The biophysical causal chain is reconstructed sequentially:

```
Month 0    Rainfall ↓
               │
Month 1    Soil moisture ↓
               │
Month 2    Land surface temperature ↑
               │
Month 2–3  Canopy moisture (NDMI) ↓
               │
Month 3    Vegetation greenness (NDVI) ↓
               │
Month 4+   Agricultural exposure → crop failure (puso)
```

### 2.2 Data Sources

| No | Dataset | Source | Resolution | Period | Variable |
|:---:|:---|:---|:---|:---|:---|
| 1 | CHIRPS v2.0 | UCSB/CHG | 0.05° (~5.5 km) | 2001–2025 | Monthly rainfall |
| 2 | ERA5-Land | ECMWF | 0.1° (~11 km) | 2001–2025 | Soil moisture (0–28 cm) |
| 3 | MODIS MOD11A2 | NASA Terra | 1 km | 2001–2025 | Land surface temperature |
| 4 | MODIS MOD09A1 | NASA Terra | 500 m → 1 km | 2001–2025 | NDVI, EVI, NDMI |
| 5 | NASA GPM IMERG V07 | NASA | 0.1° | 2001–2025 | Rainfall (sensor validation) |
| 6 | ESA WorldCover 2021 | ESA | 10 m | 2021 | Land cover / crop density |
| 7 | BPS East Java | BPS | Regency | 2015–2024 | Agricultural statistics |
| 8 | East Java Agriculture Service | Provincial Govt | Regency/month | 2015–2024 | Drought-affected cropland |
| 9 | BPBD East Java | Provincial Govt | Regency/village | 2023 | Drought emergency events |

### 2.3 Analysis

Analysis was conducted across 12 hierarchical phases (milestones):

| Phase | Milestone | Description |
|:---:|:---|:---|
| 1–2 | M1–M2 | Research framework and climate response (CHIRPS rainfall anomalies) |
| 3–4 | M3 | Physical response (ERA5 soil moisture and MODIS LST) |
| 5–7 | M4 | Vegetation response (NDVI, EVI, NDMI from MODIS Terra) |
| 8–9 | M5 | Landscape Sensitivity Index (LSI) and 5-regime clustering |
| 10–11 | M6 | Agricultural Sensitivity Index (ASI), hotspots, and 4 policy zones |
| 12 | M7 | Multi-source validation, uncertainty quantification, and ground truth |

**Landscape Sensitivity Index (LSI)** is computed as a weighted composite of standardised anomalies in rainfall, soil moisture, land surface temperature, and canopy moisture/greenness, normalised to a 0–1 scale (0 = most resilient; 1 = most vulnerable).

**Agricultural Sensitivity Index (ASI)** multiplies LSI by cropland density (from ESA WorldCover 10 m) to identify areas with simultaneously high climate vulnerability *and* high agricultural exposure.

**5-regime clustering** uses an unsupervised Weka k-Means algorithm to group 1 km pixels based on their multi-dimensional biophysical response profiles.

### 2.4 Validation

Validation was conducted in four stages:

1. **Cross-sensor climate validation:** CHIRPS v2.0 (IR/gauge) vs NASA GPM IMERG V07 (radar/microwave) on a 15 km grid (n = 280 points). Result: r = 0.745; 83.1% consistency.
2. **Cross-index vegetation validation:** NDVI vs EVI (different spectral formulations). Result: r = 0.872; 87.2% anomaly agreement.
3. **BPBD 2023 ground truth:** LSI vs BPBD water-crisis villages (benchmark cohort n = 9 regencies). Result: Pearson r = 0.933; Spearman ρ = 0.950; p-spatial = 0.0074.
4. **Agricultural 2023–2024 ground truth:** ASI vs Agriculture Service drought-affected cropland (full census n = 38 regencies/municipalities). Result: r = 0.505; p = 0.001.

### 2.5 Ethical Considerations

- **No individual human data** was collected. All data is aggregate (regency/village level) from public sources.
- **No ethical approval** was required as the study did not directly involve human subjects.
- **Data protection:** Sensitive information about vulnerable village locations is presented at regency aggregate level. No individual names or identities are published.
- **Do no harm principle:** This report avoids stigmatising specific areas. Identification of vulnerable regencies aims to direct assistance, not discredit local governments.

---

## 3. Findings and Discussion

### 3.1 Climate Response: Rainfall Drops Dramatically During El Niño

Across 8 El Niño episodes:
- **Dry-season rainfall deficit:** -151 mm (-45.4%) at peak SON (September–November)
- **Compound events** (El Niño + IOD+) deepen the deficit by an additional -21.5 mm (note: not yet statistically significant due to small n, p = 0.77)
- Standardised anomaly: Z = -0.83 (mean); three worst events (2006: Z = -1.43; 2015: Z = -1.10; 2023: Z = -1.01) breach the meteorological dryness threshold

**Data source:** CHIRPS v2.0 cross-validated against NASA GPM IMERG V07 (83.1% consistency; r = 0.745 on regular 15 km grid).

### 3.2 Physical Response: Soil Dries and Temperature Surges

- **Soil moisture:** Declined by -0.043 m³/m³ (pure El Niño) to -0.053 m³/m³ (compound event)
- **Land surface temperature (LST):** Surged +1.71°C on average; peak +2.8°C in northern lowlands
- **Evaporative decoupling:** Severely dried soils lose their capacity to cool the surface through evaporation, causing disproportionate temperature spikes

### 3.3 Vegetation Response: Canopy Moisture Falls Before Greenness

- **NDMI (canopy moisture):** Z = -0.84 — drops 30–45 days earlier than NDVI
- **NDVI (leaf greenness):** Z = -0.66 — visible only after internal leaf damage has occurred
- **Operational implication:** The 30–45 day window between NDMI signal and NDVI failure represents an untapped intervention opportunity

### 3.4 Landscape Sensitivity Index: Five Spatial Regimes

Unsupervised clustering (Weka k-Means, k = 5) yielded five coherent landscape regimes:

| Regime | Description | % Area | Dominant Characteristics |
|:---:|:---|:---:|:---|
| 1 | Northern coastal lowlands | 22.3% | Severe drought; end-of-line irrigation |
| 2 | Brantas/Bengawan Solo alluvial valleys | 19.5% | Medium-high vulnerability; technical paddies |
| 3 | Mid-slope transitional zones | 23.1% | Mixed dryland and rainfed paddies |
| 4 | Volcanic highlands | 20.0% | Medium resilience; forests and horticulture |
| 5 | Mountain forests and protected areas | 15.2% | Most resilient; water catchment function |

**Robust high-vulnerability zone:** 35.1% of land area (LSI ≥ 0.60, CV ≤ 0.45) exhibits consistently severe vulnerability across all 8 El Niño episodes.

### 3.5 Agricultural Exposure: 10 Extreme Priority Regencies

Multiplying LSI by cropland density yields the **Agricultural Sensitivity Index (ASI)**. Top 10 rankings:

| Rank | Regency | LSI | Crop Density | ASI | Critical Hotspot (%) | Tier |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | Lamongan | 0.71 | 70.2% | 0.479 | 51.5% | Extreme (Tier 1) |
| 2 | Gresik | 0.60 | 45.7% | 0.357 | 36.9% | Extreme (Tier 1) |
| 3 | Bojonegoro | 0.76 | 44.7% | 0.339 | 39.5% | Extreme (Tier 1) |
| 4 | Jombang | 0.68 | 49.4% | 0.335 | 33.1% | Extreme (Tier 1) |
| 5 | Nganjuk | 0.65 | 43.1% | 0.293 | 32.4% | Extreme (Tier 1) |
| 6 | Tuban | 0.67 | 46.0% | 0.291 | 28.3% | Extreme (Tier 1) |
| 7 | Kediri | 0.60 | 43.9% | 0.285 | 25.3% | Extreme (Tier 1) |
| 8 | Mojokerto | 0.62 | 40.5% | 0.285 | 29.4% | Extreme (Tier 1) |
| 9 | Ngawi | 0.76 | 36.9% | 0.281 | 34.5% | Extreme (Tier 1) |
| 10 | Magetan | 0.70 | 38.1% | 0.260 | 27.9% | Extreme (Tier 1) |

### 3.6 Empirical Validation: Model Confirmed by Disaster Data

**Validation 1 — BPBD 2023 (emergency cohort, n = 9):**
- Pearson r = 0.933 (R² = 0.870)
- Spearman ρ = 0.950
- Remains significant after spatial autocorrelation correction (p = 0.0074, N-eff = 5.90)
- 273 of 279 crisis villages (97.8%) are in regencies with LSI ≥ 0.55

**Validation 2 — Agriculture Service 2023–2024 (full census, n = 38):**
- Pearson r = 0.505 (p = 0.001)
- Spearman ρ consistent with risk tiers
- 6 Quadrant I regencies (damage > 3,000 ha AND intensity > 3.65%) capture 92.5% of total damage

### 3.7 The Pacitan Paradox: Vulnerability Is Multi-Dimensional

Pacitan — classified as Tier 4 (Low/Buffered) in the dry-season model — recorded **damage to 43.43% of its entire paddy base**. This occurred because:
- 97.3% of damage (5,719 ha) occurred in **January 2024** due to delayed western monsoon onset (MT-1)
- During the classic dry season (SON 2023), damage was only 28 ha
- Pacitan has a Location Quotient of 11.90× — nearly 12 times the provincial mean

**Implication:** No single vulnerability metric is sufficient. A multi-tier approach is needed that distinguishes absolute volume, local intensity, and inter-regional equity.

---

## 4. Conclusions and Recommendations

### 4.1 Conclusions

1. East Java's landscape sensitivity to El Niño is **spatially deterministic** — high-vulnerability corridors form consistently across every episode.
2. The biophysical causal chain (rainfall → soil → temperature → canopy → harvest) operates **sequentially and predictably**, with a 30–45 day intervention window between canopy moisture signals and crop failure.
3. Agricultural damage is **hyper-concentrated** — 92.5% of losses occur in 6 of 38 regencies/municipalities.
4. Severity assessment must be **multi-dimensional**: absolute volume (for macro food security), local intensity (for livelihood protection), and Location Quotient (for fiscal equity).

### 4.2 Recommendations

| Priority | Recommendation | Responsible Agency | Timeline | Success Indicator |
|:---:|:---|:---|:---|:---|
| 1 | Reallocate BTT using 60/40 Hybrid formula | Governor, BPKAD | Before April | Distribution deviation ≤ 10% from formula |
| 2 | Integrate NDMI as official early warning trigger | BPBD, Pusdalops | 6 months | Response time ≤ 14 days from detection |
| 3 | Fully subsidise AUTP in 6 priority regencies | Agriculture Service, Jasindo | Upon BMKG Advisory | Coverage ≥ 80% of registered farmers |
| 4 | Mandate irrigation quotas during compound events | BBWS Brantas & Bengawan Solo | Immediately upon forecast | No downstream paddy water shortage |

---

## 5. Limitations

1. **1 km spatial resolution:** Adequate for regency/sub-district planning; insufficient for individual field-level decisions. Sentinel-2 (10 m) is needed for precision operations.

2. **Purposive validation cohort:** The high correlation (r = 0.933) was obtained from 9 reporting regencies, not a province-wide random sample.

3. **Small compound event sample size:** Only 3 of 8 episodes were compound (El Niño + IOD+). The amplification effect is consistently observed but not yet statistically significant (p = 0.77).

4. **Unmodeled confounders:** BPBD reporting capacity, population density, baseline water infrastructure, and farmer adaptive behaviour are potential influencing factors not controlled in the analysis.

5. **Stationarity assumption:** The analysis assumes relatively stable climate-landscape relationships over 2001–2025. Long-term climate change (monsoon shifts, global warming) beyond this period is not accounted for.

6. **Implementation cost estimates:** IDR 25–40 billion/year has not undergone formal cost-benefit analysis.

---

## 6. Impact, Achievements, and Accountability

### 6.1 Research Outputs

| Aspect | Detail |
|:---|:---|
| **Geospatial products** | 51+ GeoTIFFs at 1 km resolution (climate anomalies, soil moisture, LST, NDVI, NDMI, LSI, ASI, hotspots) |
| **Visualisations** | 10+ publication-grade figures (300 DPI) |
| **Scientific reports** | 7 technical reports per milestone + 1 validation report + 1 benchmarking report |
| **Source code** | Entire pipeline open on GitHub (Python, MIT License) |
| **Reproducibility** | Every figure in this report is traceable to specific scripts and datasets |

### 6.2 Use of Funds

This research was entirely self-funded by the researcher. No public or donor funds were used. Operational costs included:
- Internet access and local computing
- Google Earth Engine licence (free for research)
- No fieldwork travel costs (remote-sensing-based study)

### 6.3 Dissemination Plan

| Channel | Target Audience | Timeline |
|:---|:---|:---|
| GitHub repository (open-source) | Research community, developers | Already available |
| Zenodo DOI (permanent archive) | Academics, formal citations | Upon final release |
| Policy Brief | East Java provincial decision-makers | September 2026 |
| Public Summary | General public, media | September 2026 |
| Presentation to BPBD/Agriculture Services | Operational practitioners | Scheduled |

---

## 7. Appendices

### Appendix A: Key Output Files

| Milestone | File | Description |
|:---|:---|:---|
| M2 | `outputs/m2_elnino_rainfall_anomalies.png` | Rainfall anomaly atlas across 8 El Niño episodes |
| M3 | `outputs/m3_physical_response.png` | Soil moisture and land surface temperature response |
| M4 | `outputs/m4_vegetation_response.png` | NDVI, EVI, and NDMI response |
| M5 | `outputs/m5_landscape_sensitivity.png` | Landscape Sensitivity Index and 5 regimes |
| M6 | `outputs/m6_agriculture_policy.png` | Agricultural Sensitivity Index and policy zones |
| M7.1 | `outputs/m7_1_sensor_validation.png` | Cross-sensor validation (CHIRPS vs GPM, NDVI vs EVI) |
| M7.2 | `outputs/m7_2_uncertainty_groundtruth.png` | BPBD ground-truth validation |
| M7.3 | `outputs/m7_3_ensemble_uncertainty.png` | 8-episode ensemble uncertainty |
| M7.4 | `outputs/m7_4_agricultural_groundtruth.png` | Empirical agricultural validation 2023–2024 |
| M7.5 | `outputs/m7_5_crop_loss_severity_framework.png` | Multi-tier severity benchmarking framework |

### Appendix B: El Niño Episode Classification (2001–2025)

| Year | Intensity | Peak ONI (°C) | Concurrent IOD+? | Type |
|:---|:---|:---|:---|:---|
| 2002–2003 | Moderate | ~1.3 | No | Pure El Niño |
| 2004–2005 | Weak | ~0.7 | No | Pure El Niño |
| 2006–2007 | Weak | ~0.9 | **Yes** | Compound (El Niño + IOD+) |
| 2009–2010 | Moderate | ~1.6 | No | Pure El Niño |
| 2014–2015 | Weak | ~0.6 | No | Pure El Niño |
| 2015–2016 | **Very Strong** | ~2.6 | No | Pure El Niño |
| 2018–2019 | Weak | ~0.8 | **Yes** | Compound (El Niño + IOD+) |
| 2023–2024 | **Strong** | ~2.0 | **Yes** | Compound (El Niño + IOD+) |

### Appendix C: Glossary

| Term | Explanation |
|:---|:---|
| **ASI** | Agricultural Sensitivity Index — crop vulnerability index (LSI × crop density) |
| **AUTP** | *Asuransi Usaha Tani Padi* — Government-subsidised paddy crop insurance |
| **BPBD** | *Badan Penanggulangan Bencana Daerah* — Regional Disaster Management Agency |
| **BTT** | *Belanja Tidak Terduga* — Unforeseen expenditure (emergency disaster budget) |
| **CHIRPS** | Climate Hazards InfraRed Precipitation with Station — satellite rainfall product |
| **Compound event** | Concurrent El Niño and positive Indian Ocean Dipole |
| **El Niño** | Abnormal warming of the Equatorial Pacific Ocean, causing drought in Indonesia |
| **EVI** | Enhanced Vegetation Index — atmosphere-corrected vegetation index |
| **IOD+** | Positive Indian Ocean Dipole — Indian Ocean SST anomaly that amplifies drought |
| **LQ** | Location Quotient — ratio of local damage rate to provincial average |
| **LSI** | Landscape Sensitivity Index — landscape vulnerability index (0–1) |
| **LST** | Land Surface Temperature — satellite-derived surface temperature |
| **MODIS** | Moderate Resolution Imaging Spectroradiometer — NASA Terra/Aqua sensor |
| **NDMI** | Normalized Difference Moisture Index — canopy water content indicator |
| **NDVI** | Normalized Difference Vegetation Index — vegetation greenness indicator |
| **ONI** | Oceanic Niño Index — El Niño indicator based on Pacific SST anomalies |
| **Puso** | Total crop failure due to drought, flooding, or pest attack |

---

## 8. References

### Primary Data Sources
1. Funk, C., et al. (2015). The Climate Hazards InfraRed Precipitation with Station data (CHIRPS). *Scientific Data*, 2, 150066.
2. Muñoz-Sabater, J., et al. (2021). ERA5-Land: A state-of-the-art global reanalysis dataset. *Earth System Science Data*, 13(9), 4349–4383.
3. Huffman, G. J., et al. (2020). NASA Global Precipitation Measurement (GPM) IMERG Version 07. NASA.
4. Zanaga, D., et al. (2022). ESA WorldCover 10 m 2021 v200.
5. BPS Provinsi Jawa Timur. (2023). *Jawa Timur Dalam Angka 2023*.
6. Kementerian ATR/BPN. (2019). Decree No. 686/SK-PG.03.03/XII/2019.

### Policy Frameworks
7. Republic of Indonesia. (2013). Law No. 19/2013 on the Protection and Empowerment of Farmers.
8. Republic of Indonesia. (2019). Presidential Regulation No. 39/2019 on One Data Indonesia.
9. Republic of Indonesia. (2022). Law No. 27/2022 on Personal Data Protection.
10. United Nations. (2015). Sendai Framework for Disaster Risk Reduction 2015–2030.
11. UNFCCC. (2015). Paris Agreement.
12. United Nations. (2015). Transforming Our World: The 2030 Agenda for Sustainable Development.

---

## 9. Contact Information and Citation

**Author:** Mochamad Khoirul Rifai  
**Affiliation:** Department of Physics, Universitas Negeri Malang, Indonesia  
**Email:** mochamadkhoirulrifai25@gmail.com  
**GitHub:** [@mkrifai](https://github.com/mkrifai)  
**Repository:** [east-java-elnino-sensitivity](https://github.com/mkrifai/east-java-elnino-sensitivity)

**Citation:**
```
Rifai, M. K. (2026). Mapping the Spatial Sensitivity of East Java Landscapes to
El Niño: A 25-Year Multi-Sensor Earth Observation Analysis (2001–2025) for Food
Security and Climate Adaptation. Public Report v0.9, Department of Physics,
Universitas Negeri Malang, Indonesia.
```

---

*This report was prepared with a commitment to transparency, reproducibility, and accountability of scientific research in the public interest.*
