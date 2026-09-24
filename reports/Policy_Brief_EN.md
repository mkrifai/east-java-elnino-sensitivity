# El Niño Drought Hits East Java: A 25-Year Satellite Risk Map and Policy Direction

**Document Type:** Policy Brief  
**Author:** Mochamad Khoirul Rifai  
**Affiliation:** Department of Physics, Universitas Negeri Malang, Indonesia  
**Date:** September 2026 (Draft / Pre-release v0.9)  
**Version:** 0.9 — Not yet peer-reviewed; subject to revision  
**License:** CC BY 4.0 International  
**DOI:** *(To be assigned via Zenodo upon final release)*  
**Citation:** Rifai, M. K. (2026). *El Niño Drought Hits East Java: A 25-Year Satellite Risk Map and Policy Direction.* Policy Brief v0.9, Department of Physics, Universitas Negeri Malang.

---

> **Disclaimer:** This policy brief presents findings from independent research and does not represent the official position of Universitas Negeri Malang, the Government of East Java Province, or any other institution. The author received no external funding. All code and data are open-source (MIT / CC BY 4.0) and traceable via a public repository.

---

## Key Messages

1. **El Niño always strikes the same places.** Analysis of 25 years of satellite data (2001–2025) proves that 35.1% of East Java's land area suffers severe drought during *every* El Niño episode — consistently along the northern coastal corridor (Lamongan, Bojonegoro, Tuban, Gresik) and the lower Brantas River valley.

2. **Six regencies bear 92% of agricultural damage.** During the 2023–2024 El Niño, 41,576 hectares of rice paddies and cropland failed. Six regencies alone (Lamongan, Gresik, Pacitan, Bojonegoro, Tulungagung, Tuban) absorbed 92.5% of total losses.

3. **Early warning signals are available 4–6 weeks before crop death.** Canopy moisture (NDMI) drops measurably 30–45 days before leaves visibly yellow (NDVI). This window is sufficient to deploy water pumps, adjust irrigation rotations, and rescue harvests.

4. **Current emergency budget allocation does not match the risk map.** Provincial emergency funds (BTT) are currently distributed evenly based on political pressure rather than empirical vulnerability. A "60/40 Hybrid" formula — 60% by absolute damage volume, 40% by local intensity relative to provincial mean — would protect both major grain baskets and the most devastated smallholder communities.

5. **Existing institutions are sufficient; operational procedures need to change.** No new agencies are required. Integrating satellite vulnerability maps into the existing BPBD Operations Centre (Pusdalops) and Agricultural Services workflows can transform reactive response into preventive preparedness.

---

## Executive Summary

El Niño is the primary driver of agricultural drought in East Java — Indonesia's largest rice-producing province (>10 million metric tons of unhusked rice annually). Yet government response remains reactive: emergency funds flow only after crops have yellowed and wells have dried.

This research leverages **25 years of multi-sensor satellite data** (CHIRPS, ERA5-Land, MODIS, NASA GPM) at 1 km resolution to answer one question: *Where, how severely, and how predictably does El Niño impact East Java's landscapes?*

**Core finding:** El Niño's impact on East Java is **spatially deterministic** — the same areas are hit repeatedly — and **detectable in advance** through canopy moisture monitoring. By directing 70% of drought emergency budgets to 10 validated regencies, integrating satellite NDMI as an official early warning trigger, and fully subsidising crop insurance (AUTP) in critical zones, the East Java Provincial Government can significantly reduce harvest losses and protect food security for 40 million people.

---

## Background and Problem

### Why is this urgent now?

East Java faces a **recurring, patterned threat**:

- **Scale of impact:** During the 2023–2024 El Niño (Strong, + positive IOD), the province lost **41,576 hectares** of cropland to drought — an area four times the size of Surabaya city.
- **Who is affected:** Approximately 1.14 million hectares of official paddy land (*luas baku sawah*) are distributed across 38 regencies/municipalities. But the damage is hyper-concentrated: **6 regencies bear 92.5%** of all losses. Hundreds of thousands of smallholder farming families depend on paddy rice as their sole livelihood.
- **Recurrent pattern:** Eight El Niño episodes occurred in the past 25 years (2002, 2004, 2006, 2009, 2014, 2015, 2018, 2023). Each time, the same areas were affected — yet this pattern has not been leveraged for preventive preparedness.
- **Escalating risk:** Compound events (El Niño + positive Indian Ocean Dipole) deepen rainfall deficit by an additional -21.5 mm and dry soils 23% deeper than standalone El Niño events.

### What decisions need to be taken?

| Decision | Decision-Maker | Timeline |
|:---|:---|:---|
| Reallocate drought BTT funds based on satellite risk map | Governor of East Java, BPKAD | Before next dry season (April) |
| Integrate NDMI as official early warning trigger | Head of BPBD East Java, Pusdalops PB | 6 months post-approval |
| Fully subsidise AUTP insurance in 6 priority regencies | Dinas Pertanian East Java, Jasindo | Upon BMKG El Niño Advisory |
| Mandate upstream–downstream irrigation quotas during compound events | BBWS Brantas & Bengawan Solo | Immediately upon El Niño + IOD+ detection |

### Alignment with national and international commitments

- **RPJMN 2025–2029:** Food security and climate change adaptation are national development priorities.
- **SDG Goal 2 (Zero Hunger):** Protecting harvests from recurrent climate shocks.
- **SDG Goal 13 (Climate Action):** Building adaptive capacity to climate hazards.
- **Sendai Framework for DRR 2015–2030:** Target E — reducing economic losses from disasters through risk-based strategies.
- **Paris Agreement (Indonesia's NDC):** National contribution through agricultural sector adaptation to climate variability.
- **NAP-API (National Adaptation Plan for Climate Change):** Food security and water availability sectors.

---

## About the Research

**Research question:** How does landscape sensitivity to El Niño vary spatially across East Java, and how can these patterns inform geographically targeted drought preparedness?

**Methods:** Cloud-based earth observation analysis (Google Earth Engine Python API) reconstructing the full biophysical response chain — from rainfall anomaly → soil moisture → land surface temperature → canopy moisture → greenness index → agricultural exposure — across all of East Java at 1 km resolution.

**Data:** Five primary satellite sources (CHIRPS v2.0, ERA5-Land, MODIS Terra, NASA GPM IMERG V07, ESA WorldCover) plus official BPS and East Java Agriculture Service data for ground-truth validation.

**Location and period:** East Java Province (38 regencies/municipalities), 2001–2025 (25 years, covering 8 El Niño episodes and 6 ENSO-neutral years as baseline).

*Full methodological detail is available in the appendix and open-source repository.*

---

## Main Findings

### Finding 1: El Niño drought is spatially deterministic — not random

Ensemble analysis across 8 El Niño episodes demonstrates that **35.1% of East Java's land area** consistently exhibits high vulnerability (Landscape Sensitivity Index / LSI ≥ 0.60 with low inter-event variation, CV ≤ 0.45). These areas form a continuous corridor from Lamongan–Bojonegoro–Tuban in the north and the lower Brantas valley (Jombang–Nganjuk–Mojokerto).

**Implication:** Government need not wait for drought to occur to identify priority areas. The vulnerability map is already available and validated.

**Confidence level:** *High.* Consistent across 8 independent El Niño episodes of varying intensity.

### Finding 2: Six regencies bear 92% of agricultural damage

During the 2023–2024 El Niño, **41,576 hectares** of paddies and cropland failed across East Java. The distribution was extremely uneven:

| Rank | Regency | Damage (ha) | % of Province | Local Paddy Damage (%) |
|:---:|:---|---:|---:|---:|
| 1 | **Lamongan** | 12,997 | 31.3% | 14.9% |
| 2 | **Gresik** | 6,008 | 14.5% | 15.8% |
| 3 | **Pacitan** | 5,880 | 14.1% | **43.4%** |
| 4 | **Bojonegoro** | 5,747 | 13.8% | 7.4% |
| 5 | **Tulungagung** | 4,426 | 10.6% | 16.7% |
| 6 | **Tuban** | 3,393 | 8.2% | 6.3% |
| | *32 other regencies/cities* | 3,125 | 7.5% | < 2.3% |

**Critical note (Pacitan Paradox):** Pacitan — classified as "low sensitivity" in dry-season models — lost **43.4% of its entire paddy base** in a single month (January 2024) due to delayed monsoon onset (MT-1 delay), not classic dry-season drought. This shows that vulnerability is multi-dimensional.

**Confidence level:** *High.* Data from a full census of 38 regencies/municipalities by the East Java Agriculture Service.

### Finding 3: 4–6 week early warning available through satellite canopy moisture

Leaf water content (NDMI index) drops significantly (Z = -0.84) **30–45 days earlier** than the greenness index (NDVI, Z = -0.66). When leaves are still green but water content has fallen, water pumps and irrigation rotations can still save the harvest.

**Confidence level:** *Medium-high.* Consistently observed in MODIS Terra 1 km data, but not yet tested in field operations.

### Finding 4: Satellite model confirmed by official disaster data

Landscape Sensitivity Index (LSI) values show strong correlation with 2023 BPBD East Java water-crisis village data:

- **Pearson correlation:** r = 0.933 (87% of village crisis variance explained by LSI scores)
- **Spearman rank agreement:** ρ = 0.950
- **Remains significant after spatial autocorrelation correction:** p = 0.0074

**Limitation:** Validation covers 9 regencies that *officially reported* drought emergencies (purposive benchmark cohort, not a random sample). The R² of 87% reflects statistical association, not causal determinism — administrative reporting capacity, population density, and baseline infrastructure are unmodeled covariates.

**Confidence level:** *Medium.* Strong association but limited to reporting cohort.

### Finding 5: Compound events (El Niño + IOD+) deepen the crisis

Three of eight El Niño episodes were compound (concurrent positive IOD: 2006, 2018, 2023). These yielded:

- Additional mean rainfall deficit of -21.5 mm during peak dry season (SON)
- 23% deeper soil drying (-0.053 m³/m³ vs -0.043 m³/m³)
- Three of the four worst droughts on record occurred during compound years

**Statistical note:** This difference is not yet statistically significant (p = 0.77, small sample n = 3 vs 5). Evidence is suggestive rather than conclusive.

**Confidence level:** *Medium-low* for statistical significance; *high* for directional effect based on atmospheric physics.

---

## Policy Options Analysis

| Aspect | **Option A: Status Quo** (Reactive Response) | **Option B: Partial Reform** (AUTP Subsidy + NDMI) | **Option C: Comprehensive Reform** *(Recommended)* |
|:---|:---|:---|:---|
| **Description** | BTT distributed evenly post-damage. No satellite early warning. Voluntary AUTP. | Full AUTP subsidy in 6 priority regencies + NDMI dashboard integration. BTT not yet reallocated. | BTT 60/40 Hybrid + NDMI early warning + 100% AUTP in hotspots + irrigation quotas during compound events. |
| **Benefits** | No regulatory changes needed. Zero upfront cost. | Farmer financial protection increases. Early detection available. Moderate cost. | Comprehensive protection: macro food production + micro livelihood. High fiscal efficiency. |
| **Estimated additional cost** | IDR 0 (baseline) | IDR 15–25 billion/year | IDR 25–40 billion/year |
| **Risks** | Recurring losses IDR 100+ billion/episode. Farmer impoverishment. Delayed response. | BTT remains inefficient. Non-priority regencies may object. No irrigation protection. | Political resistance to budget redistribution. Requires technical capacity at BPBD/Agriculture Services. |
| **Prerequisites** | None | Jasindo–Agriculture Services cooperation. Monitoring system procurement. | Governor's regulation, cross-BBWS MoU, staff training, cross-agency data integration. |
| **SDG 2 & 13 effectiveness** | Low | Medium | High |

### Recommended: **Option C (Comprehensive Reform)** with phased implementation

---

## Recommendations

### Recommendation 1: Reallocate BTT Funds Using the "60/40 Hybrid Formula" *(Highest Priority)*
- **Who:** Governor of East Java, BPKAD, Provincial BTT Team
- **What:** Issue a Governor's Regulation establishing BTT drought allocation formula: 60% proportional to absolute damage volume (ha) + 40% proportional to Location Quotient (local intensity vs provincial mean).
- **When:** Draft regulation ready by March; effective before the next dry season.
- **Resources:** No additional budget required — redistribution of existing allocation.

### Recommendation 2: Integrate Satellite NDMI as Official Early Warning Trigger
- **Who:** Head of BPBD East Java, Pusdalops PB, Agriculture Services
- **What:** Add automated 8-day canopy moisture (NDMI) monitoring from MODIS/Sentinel-2 to the Pusdalops operational dashboard. When NDMI Z-score drops below -0.7 in priority sub-districts, automatically trigger mobile pump deployment and irrigation rotation orders.
- **When:** System development 6 months; fully operational before April of the following year.
- **Resources:** IDR 3–5 billion for dashboard development, training, and data integration.

### Recommendation 3: Fully Subsidise Crop Insurance (AUTP) in 6 Catastrophic Regencies
- **Who:** East Java Agriculture Services, PT Jasindo, regional OJK
- **What:** Provide 100% premium subsidy for AUTP for all registered farmer groups in Lamongan, Gresik, Pacitan, Bojonegoro, Tulungagung, and Tuban, auto-activated upon BMKG El Niño Advisory.
- **When:** Effective upon next BMKG advisory.
- **Resources:** IDR 12–18 billion/year depending on coverage and claims.

### Recommendation 4: Mandate Upstream–Downstream Irrigation Quotas During Compound Events
- **Who:** BBWS Brantas and BBWS Bengawan Solo, Public Works Water Resources Service
- **What:** When BMKG forecasts concurrent El Niño + positive IOD, immediately enforce 30% restriction on industrial water allocation and prioritise food crop paddy discharge in primary and secondary canals.
- **When:** Immediately upon compound event forecast confirmation (typically April–May).
- **Resources:** Cross-agency coordination; BBWS–Agriculture Services–ESDM MoU.

---

## Implementation and Monitoring

### Implementation Roadmap

| Phase | Period | Key Activities |
|:---:|:---|:---|
| **Phase 1** | Months 1–6 | Draft Governor's Regulation for BTT 60/40; Develop Pusdalops NDMI dashboard; Coordinate AUTP subsidy with Jasindo |
| **Phase 2** | Months 7–12 | Pilot NDMI dashboard in 3 regencies (Lamongan, Pacitan, Tulungagung); Socialise BTT regulation |
| **Phase 3** | Year 2 | Full implementation of all 4 recommendations; Evaluate impact during first post-implementation El Niño |
| **Evaluation** | Year 3 | Independent effectiveness review; Update vulnerability maps with latest data |

### Success Indicators

| Indicator | Target | Monitoring Method |
|:---|:---|:---|
| Crop failure area during next El Niño | Decrease ≥ 25% vs 2023–2024 baseline | Agriculture Services comparison data |
| Response time from NDMI signal | ≤ 14 days from anomaly detection to pump deployment | Pusdalops BPBD operational logs |
| AUTP coverage in 6 priority regencies | ≥ 80% of registered paddy farmers | PT Jasindo claims data |
| BTT distribution alignment with 60/40 formula | Deviation ≤ 10% from formula | BPKAD audit |

---

## Limitations and Uncertainties

1. **1 km spatial resolution** — Sufficient for regency/sub-district planning but not for individual field-level decisions. Higher resolution (Sentinel-2, 10 m) is needed for precision implementation.

2. **Validation limited to reporting cohort** — The 0.933 correlation with BPBD data covers only 9 regencies that officially reported emergencies. Non-reporting regencies are excluded, potentially introducing selection bias.

3. **Compound events (El Niño + IOD+)** — The amplification effect is consistently observed but not statistically significant due to small sample size (3 compound events from 8 total). More events or model simulations are needed for confirmation.

4. **Implementation costs are estimates** — IDR 25–40 billion/year has not undergone formal cost-benefit analysis. Actual figures depend on inter-agency negotiations.

5. **Social and institutional factors are unmodeled** — BPBD reporting capacity, population density, baseline water infrastructure, and farmer adaptive behaviour are potential confounders.

6. **Temporal scope** — Analysis based on 2001–2025 data; long-term climate change trends beyond this period are not accounted for.

---

## Acknowledgements, Funding, and Conflict of Interest

- **Funding:** Entirely self-funded. No government, industry, or donor funding received.
- **Conflict of interest:** The author declares no financial or non-financial conflicts of interest.
- **Author's role:** The author presents research findings and proposes policy recommendations based on data interpretation, not political advocacy.
- **Public data:** All satellite data sourced from public repositories. Agricultural data from BPS and East Java Agriculture Services. Disaster data from BPBD East Java.

---

## References and Appendices

### Primary Data Sources
1. CHIRPS v2.0 — Climate Hazards InfraRed Precipitation with Station (UCSB, 0.05°, 2001–2025)
2. ERA5-Land — ECMWF Reanalysis (Soil Moisture 0–28 cm, 0.1°, 2001–2025)
3. MODIS Terra — MOD09A1 Surface Reflectance & MOD11A2 LST (1 km, 2001–2025)
4. NASA GPM IMERG V07 — Global Precipitation Measurement (0.1°, 2001–2025)
5. ESA WorldCover 2021 — Global Land Cover (10 m)
6. BPS East Java — Agricultural Statistics & Official Paddy Land Area
7. East Java Agriculture and Food Security Service — Drought-Affected Cropland Data (2015–2024)
8. BPBD East Java — Drought and Water-Crisis Disaster Reports (2023)
9. Minister of Agrarian Affairs Decree No. 686/2019 — National Paddy Land Area Designation

### Appendices (available in repository)
- Full methodology: [`research_framework.md`](../research_framework.md)
- Source code: [`scripts/`](../scripts/) (Python, open-source, MIT License)
- Output data: [`outputs/`](../outputs/) (GeoTIFF, PNG, JSON)
- Technical reports per milestone: [`reports/`](../reports/)

---

## Contact Information

**Author:** Mochamad Khoirul Rifai  
**Affiliation:** Department of Physics, Universitas Negeri Malang, Indonesia  
**Email:** mochamadkhoirulrifai25@gmail.com  
**GitHub:** [@mkrifai](https://github.com/mkrifai)  
**Repository:** [east-java-elnino-sensitivity](https://github.com/mkrifai/east-java-elnino-sensitivity) (Open-Source, MIT License)

---

## Glossary

| Term | Explanation |
|:---|:---|
| **AUTP** | *Asuransi Usaha Tani Padi* — Government-subsidised paddy crop insurance |
| **BPBD** | *Badan Penanggulangan Bencana Daerah* — Regional Disaster Management Agency |
| **BTT** | *Belanja Tidak Terduga* — Unforeseen expenditure (emergency disaster budget line in regional government budgets) |
| **BBWS** | *Balai Besar Wilayah Sungai* — Major River Basin Authority (manages rivers and irrigation) |
| **Compound Event** | Concurrent El Niño and positive Indian Ocean Dipole (IOD+) |
| **El Niño** | Abnormal warming of the Equatorial Pacific Ocean, causing drought in Indonesia |
| **IOD+** | Positive Indian Ocean Dipole — sea surface temperature anomaly deepening Indonesian drought |
| **Location Quotient (LQ)** | Ratio of local damage rate to provincial average; LQ > 1 = more severe than average |
| **LSI** | Landscape Sensitivity Index — landscape vulnerability index (0–1), higher = more vulnerable |
| **NDMI** | Normalized Difference Moisture Index — satellite-derived canopy moisture indicator |
| **NDVI** | Normalized Difference Vegetation Index — satellite-derived leaf greenness indicator |
| **Puso** | Total crop failure due to drought, flooding, or pest attack |
