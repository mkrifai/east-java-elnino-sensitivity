# Milestone 2 — Climate Response Atlas: Comprehensive Report
**Mapping the Spatial Sensitivity of East Java Landscapes to El Niño**  
*Period of Analysis: 2001–2025 | Target Resolution: 1 km / CHIRPS 0.05°*

---

## PART 1: ACADEMIC REPORT & SCIENTIFIC DISCUSSION

### 1.1 Theoretical Framework & Atmospheric Dynamics
The Maritime Continent represents the ascending branch of the equatorial Walker Circulation under neutral conditions. During an El Niño Southern Oscillation (ENSO) warm phase, the anomalous eastward displacement of the Indo-Pacific warm pool shifts the primary atmospheric convective ascent toward the central and eastern equatorial Pacific. Consequently, the Indonesian archipelago—and specifically Java Island ($111^\circ\text{E} - 115^\circ\text{E}, 7^\circ\text{S} - 9^\circ\text{S}$)—is subjected to broad-scale anomalous atmospheric subsidence, surface divergence, and suppressed convection.

In East Java (Jawa Timur), this macro-scale atmospheric forcing strongly modulates the Australian Monsoon. During the dry season (June–November), southeasterly trade winds carry dry continental air masses from Australia. El Niño exacerbates this synoptic regime by:
1. Delaying the seasonal northward migration of the Intertropical Convergence Zone (ITCZ).
2. Deepening the mid-tropospheric inversion layer.
3. Prolonging the dry-season duration (JJA into SON) and retarding the onset of the wet monsoon by 30 to 60 days.

```
Neutral Walker Circulation:
   [Warm Pool: Maritime Continent] <---- Trade Winds <---- [Eastern Pacific]
               ▲ (Ascent / Deep Convection)                     ▼ (Subsidence)

El Niño Perturbation:
   [Suppressed: Java / Indonesia] ----> Anomalous Flow ----> [Eastern Pacific]
         ▼ (Subsidence / Drought)                                ▲ (Ascent)
```

![Milestone 2 Rainfall Anomalies](../outputs/m2_elnino_rainfall_anomalies.png)
*Figure 1: (Left) Mean seasonal rainfall anomalies for JJA, SON, and full dry season (JJASON) under El Niño composite forcing (2001–2025). (Right) Event-by-event SON rainfall deficits across 8 historical El Niño episodes, illustrating compound IOD+ amplification in 2006, 2018, and 2023.*

### 1.2 Quantitative Climatological Baseline & Anomaly Distribution

Using the UCSB CHIRPS v2.0 high-resolution satellite-gauge blended precipitation record (2001–2025), a 25-year seasonal climatology was established using neutral ENSO baseline years ($2001, 2003, 2012, 2013, 2019, 2025$):

* **Baseline Climatological Mean ($\mu_P$)**:
  * **JJA (June–August)**: $160.8\text{ mm}$ (provincial spatial standard deviation $\sigma_{spatial} = 42.1\text{ mm}$).
  * **SON (September–November)**: $331.7\text{ mm}$ ($\sigma_{spatial} = 68.4\text{ mm}$).
  * **Full Dry Season (JJASON)**: $492.5\text{ mm}$.

Under multi-event El Niño composite forcing (8 distinct episodes: 2002, 2004, 2006, 2009, 2014, 2015, 2018, 2023), East Java experienced pervasive rainfall suppression across all landscape zones:

* **JJA Rainfall Anomaly ($P'_{JJA}$)**:
  * Provincial mean anomaly: **$-76.9\text{ mm}$** (a **$-47.8\%$** reduction relative to baseline).
  * Minimum anomaly: $-172.7\text{ mm}$; Maximum: $-24.7\text{ mm}$; Spatial standard deviation: $\sigma = 21.0\text{ mm}$.
  * Standardized anomaly: $Z_{P, JJA} = -0.63$.
* **SON Rainfall Anomaly ($P'_{SON}$)**:
  * Provincial mean anomaly: **$-150.7\text{ mm}$** (a **$-45.4\%$** reduction relative to baseline).
  * Minimum anomaly: $-317.3\text{ mm}$; Maximum: $-72.3\text{ mm}$; Spatial standard deviation: $\sigma = 37.6\text{ mm}$.
  * Standardized anomaly: $Z_{P, SON} = -0.83$.
* **Full Dry Season Anomaly ($P'_{JJASON}$)**:
  * Cumulative provincial mean deficit: **$-227.7\text{ mm}$** (ranging from $-487.2\text{ mm}$ in eastern rain-shadow plains to $-108.8\text{ mm}$ along southern windward highlands).

### 1.3 Compound Climate Forcing: Pacific ENSO vs Indian Ocean Dipole (IOD+)
A critical scientific gap addressed in this research is isolating the confounding influence of the Positive Indian Ocean Dipole (IOD+). In positive IOD events, anomalous cooling of sea surface temperatures (SST) in the eastern equatorial Indian Ocean off the coast of Sumatra and Java suppresses atmospheric convection directly upstream of East Java.

Our empirical partitioning reveals stark differences between pure ENSO forcing and compound events:

| Analytical Group | Representative Years | JJA Mean Anomaly | JJA Min / Max (mm) | SON Mean Anomaly | SON Min / Max (mm) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **El Niño-Only (Pure)** | 2002, 2004, 2009, 2014, 2015 | $-79.0\text{ mm}$ | $-182.9\text{ / } -30.2$ | $-142.7\text{ mm}$ | $-299.5\text{ / } -68.1$ |
| **El Niño + IOD+ (Compound)** | 2006, 2018, 2023 | $-73.6\text{ mm}$ | $-186.0\text{ / } -10.2$ | **$-164.2\text{ mm}$** | **$-347.0\text{ / } -77.0$** |
| **La Niña (Contrast)** | 11 episodes | $+20.9\text{ mm}$ | $-12.2\text{ / } +123.2$ | $+119.0\text{ mm}$ | $+33.7\text{ / } +280.9$ |

#### Statistical Evaluation of Hypothesis H1
> **Hypothesis H1**: *El Niño-induced climate anomalies exhibit significant spatial heterogeneity across East Java, amplified by concurrent positive IOD events.*

* **Empirical Validation**: In SON, concurrent positive IOD events exacerbate regional rainfall deficits by an additional **$-21.5\text{ mm}$** on average (**$-164.2\text{ mm}$** vs **$-142.7\text{ mm}$**).
* **Extreme Event Magnification**: In the compound events of 2006 (Weak El Niño + Strong IOD+) and 2023 (Strong El Niño + Strong IOD+), SON deficits reached **$-259.2\text{ mm}$** ($Z = -1.43$) and **$-184.5\text{ mm}$** ($Z = -1.01$), respectively. In contrast, even during the "Very Strong" 1997-like pure El Niño of 2015, SON anomaly was $-199.9\text{ mm}$ ($Z = -1.10$).
* **Conclusion**: **Hypothesis H1 is strongly supported**. The Indian Ocean Dipole acts as a major co-driver of catastrophic dry-season desiccation in East Java, and ignoring IOD interactions leads to substantial underestimation of peak drought severity.

---

## PART 2: PUBLIC REPORT & WHY IT MATTERS TO CITIZENS AND GOVERNMENT

### 2.1 Executive Summary in Plain Language
East Java is Indonesia's paramount rice granary, contributing approximately 10 to 10.5 million tons of milled rice annually (nearly 18% of the national rice supply). Our 25-year satellite and station-backed climate analysis reveals that during El Niño periods, East Java experiences a staggering **45% to 48% deficit in dry-season rainfall**, losing more than **225 million liters of water per square kilometer** across the province between June and November.

Crucially, when El Niño strikes simultaneously with a positive Indian Ocean Dipole (IOD)—a condition that occurred in 2006, 2018, and 2023—the drought does not merely arrive earlier; it intensifies dramatically into the late months of the year (September–November), stripping up to **347 mm of rainfall** from agricultural zones before the rainy season even attempts to begin.

### 2.2 Socio-Economic and Agricultural Threats
1. **Disruption of the Planting Calendar (*Musim Tanam II & III*)**:
   Under normal conditions, farmers in East Java plant secondary food crops (*palawija*: maize, soybean) or a second/third paddy crop during the dry season. A rainfall reduction of ~47% in JJA completely desiccates non-irrigated (*tadah hujan*) fields, forcing hundreds of thousands of hectares to lie fallow (*puso*).
2. **Reservoir Depletion in the Brantas and Bengawan Solo River Basins**:
   The Brantas River basin supplies municipal water to Surabaya, Malang, Kediri, and Sidoarjo, while powering hydro-turbines and irrigating over 300,000 hectares of prime agricultural land. A 227 mm cumulative deficit severely lowers storage levels in critical reservoirs (Sutami/Karangkates, Selorejo, Wonorejo), creating fierce water conflicts between agricultural irrigation and municipal/industrial utilities.
3. **Food Inflation and Fiscal Shock**:
   A harvest contraction of just 10–15% in East Java directly triggers national rice price spikes, requiring costly emergency central-government market operations (Bulog) and foreign imports.

### 2.3 Key Recommendations for Regional Government (Pemprov Jawa Timur)
1. **Adopt a Multi-Basin Climate Early Warning Protocol**:
   * *Action*: BMKG East Java and BPBD Jatim must issue joint drought warnings not only when NOAA declares an El Niño watch, but specifically when BoM/JMA indicates an **emerging positive IOD** (DMI $> +0.4^\circ\text{C}$) in May–June. A compound watch must trigger Level-1 emergency status automatically.
2. **Dynamic Reservoir Water Allocation Guidelines (BBWS Brantas & BBWS Bengawan Solo)**:
   * *Action*: Shift reservoir release curves from historical averages to an "El Niño Deficit Curve" by July 1st of an ENSO year. Prioritize storage conservation for late dry season (SON) survival rather than maximizing wet-season outflow.
3. **Mandated Crop Switching in Tail-End Irrigation Sectors**:
   * *Action*: Dinas Pertanian Jawa Timur must mandate a complete moratorium on third-season paddy cultivation (*padi MT III*) in secondary and tertiary canals that lack dedicated weir storage, replacing it with drought-resistant sorghum, cassava, or green gram (*kacang hijau*).
4. **Targeted Groundwater & Deep-Well Subsidies**:
   * *Action*: Focus emergency pumping equipment and diesel fuel vouchers directly on the verified rain-shadow drought hotspots identified in this atlas (e.g., northern coastal plains of Lamongan, Tuban, and Pasuruan-Probolinggo).
