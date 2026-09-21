"""
Project Configuration
======================
Mapping the Spatial Sensitivity of East Java Landscapes to El Niño

Shared parameters, ENSO classification, and utility functions
used across all milestones (M2-M7).
"""

import ee

# ================================================================
#  STUDY AREA
# ================================================================

def get_east_java():
    """
    Get East Java (Jawa Timur) province boundary from FAO GAUL Level 1.
    Returns ee.FeatureCollection with the province geometry.
    """
    gaul = ee.FeatureCollection('FAO/GAUL/2015/level1')
    east_java = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Jawa Timur'))
    return east_java


def get_east_java_districts():
    """
    Get East Java district (kabupaten/kota) boundaries from FAO GAUL Level 2.
    Returns ee.FeatureCollection with district-level geometries.
    """
    gaul = ee.FeatureCollection('FAO/GAUL/2015/level2')
    districts = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Jawa Timur'))
    return districts


# ================================================================
#  STUDY PERIOD
# ================================================================

START_YEAR = 2001
END_YEAR = 2025


# ================================================================
#  ENSO CLASSIFICATION (DRY-SEASON YEAR: JJA-SON)
# ================================================================
#
# El Niño episodes are assigned to the year containing their
# primary dry-season impact on Java (JJA-SON), which corresponds
# to the developing/peak phase of the ENSO event.
#
# Example: El Niño 2015-16 → dry season 2015
#

# --- El Niño years ---
EL_NINO_ONLY = [2002, 2004, 2009, 2014, 2015]   # Pure ENSO forcing
EL_NINO_IOD  = [2006, 2018, 2023]                # Compound El Niño + positive IOD
EL_NINO_ALL  = EL_NINO_ONLY + EL_NINO_IOD

# --- La Niña years ---
LA_NINA = [2005, 2007, 2008, 2010, 2011, 2016, 2017, 2020, 2021, 2022, 2024]

# --- Neutral years ---
ALL_YEARS = list(range(START_YEAR, END_YEAR + 1))
NEUTRAL = [y for y in ALL_YEARS if y not in EL_NINO_ALL and y not in LA_NINA]
# Result: [2001, 2003, 2012, 2013, 2019, 2025]

# --- Positive IOD years (for confounding analysis) ---
IOD_POSITIVE = [2006, 2008, 2012, 2018, 2019, 2023]

# --- El Niño intensity lookup ---
ENSO_INTENSITY = {
    2002: 'Moderate',  2004: 'Weak',       2006: 'Weak',
    2009: 'Moderate',  2014: 'Weak',       2015: 'Very Strong',
    2018: 'Weak',      2023: 'Strong',
}


# ================================================================
#  SEASON DEFINITIONS
# ================================================================

JJA = [6, 7, 8]          # June-July-August (dry-season onset)
SON = [9, 10, 11]        # September-October-November (peak dry season)
DRY_SEASON = JJA + SON   # Full dry season: June-November


# ================================================================
#  GEE DATASET COLLECTION IDS
# ================================================================

CHIRPS_DAILY  = 'UCSB-CHG/CHIRPS/DAILY'
GPM_MONTHLY   = 'NASA/GPM_L3/IMERG_MONTHLY_V07'
ERA5_LAND     = 'ECMWF/ERA5_LAND/MONTHLY_AGGR'
MODIS_LST     = 'MODIS/061/MOD11A2'
MODIS_NDVI    = 'MODIS/061/MOD13A2'
SRTM          = 'USGS/SRTMGL1_003'
WORLDCOVER    = 'ESA/WorldCover/v200'
MODIS_LC      = 'MODIS/061/MCD12Q1'


# ================================================================
#  EXPORT SETTINGS
# ================================================================

EXPORT_SCALE   = 1000          # 1 km target resolution
CHIRPS_SCALE   = 5566          # CHIRPS native resolution (~0.05°)
EXPORT_CRS     = 'EPSG:4326'
DRIVE_FOLDER   = 'EastJava_ElNino_Sensitivity'


# ================================================================
#  UTILITY FUNCTIONS
# ================================================================

def build_monthly_chirps(start_year, end_year, aoi=None):
    """
    Aggregate CHIRPS daily rainfall into monthly totals.

    Returns an ee.ImageCollection where each image represents
    total monthly precipitation (mm) with 'year' and 'month' properties.
    """
    chirps = ee.ImageCollection(CHIRPS_DAILY)
    if aoi is not None:
        chirps = chirps.filterBounds(aoi)

    years = ee.List.sequence(start_year, end_year)
    months = ee.List.sequence(1, 12)

    def _year_month_pairs(y):
        return months.map(lambda m: ee.List([y, m]))

    ym_pairs = years.map(_year_month_pairs).flatten()

    def _monthly_sum(ym):
        ym = ee.List(ym)
        y  = ee.Number(ym.get(0))
        m  = ee.Number(ym.get(1))
        start = ee.Date.fromYMD(y, m, 1)
        end   = start.advance(1, 'month')
        img   = (chirps.filterDate(start, end)
                       .sum()
                       .rename('precipitation')
                       .set({'year': y, 'month': m,
                             'system:time_start': start.millis()}))
        return img

    return ee.ImageCollection(ym_pairs.map(_monthly_sum))


def build_seasonal_collection(season_months, start_year, end_year, aoi=None):
    """
    Compute seasonal total rainfall for each year.

    Parameters
    ----------
    season_months : list
        Calendar months defining the season, e.g. [6,7,8] for JJA.
    start_year, end_year : int
        Study period.
    aoi : ee.Geometry, optional
        Spatial filter to speed up processing.

    Returns
    -------
    ee.ImageCollection
        One image per year with total seasonal precipitation (mm).
    """
    chirps = ee.ImageCollection(CHIRPS_DAILY)
    if aoi is not None:
        chirps = chirps.filterBounds(aoi)

    first_month = season_months[0]
    last_month  = season_months[-1]
    years = ee.List.sequence(start_year, end_year)

    def _seasonal_total(year):
        year  = ee.Number(year)
        start = ee.Date.fromYMD(year, first_month, 1)
        end   = ee.Date.fromYMD(year, last_month, 1).advance(1, 'month')
        total = (chirps.filterDate(start, end)
                       .sum()
                       .rename('precipitation')
                       .set({'year': year,
                             'system:time_start': start.millis()}))
        return total

    return ee.ImageCollection(years.map(_seasonal_total))


def export_image(image, description, aoi, scale=None, folder=None):
    """
    Export an ee.Image to Google Drive as GeoTIFF.

    Returns the export task (already started).
    """
    if scale is None:
        scale = EXPORT_SCALE
    if folder is None:
        folder = DRIVE_FOLDER

    task = ee.batch.Export.image.toDrive(
        image=image.toFloat(),
        description=description,
        folder=folder,
        region=aoi.geometry() if hasattr(aoi, 'geometry') else aoi,
        scale=scale,
        crs=EXPORT_CRS,
        maxPixels=1e10,
    )
    task.start()
    return task


def download_image_local(image, description, aoi, out_dir, scale=None):
    """
    Directly download an ee.Image to local computer as GeoTIFF.

    Parameters
    ----------
    image : ee.Image
    description : str
        Base filename without extension
    aoi : ee.FeatureCollection or ee.Geometry
    out_dir : str
        Local output directory path
    scale : int, optional
        Pixel resolution in meters

    Returns
    -------
    str : Path to downloaded local GeoTIFF file
    """
    import urllib.request
    import os

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{description}.tif")
    if scale is None:
        scale = EXPORT_SCALE
    region = aoi.geometry() if hasattr(aoi, 'geometry') else aoi

    url = image.toFloat().clip(region).getDownloadURL({
        'name': description,
        'scale': scale,
        'crs': EXPORT_CRS,
        'region': region,
        'format': 'GEO_TIFF'
    })
    urllib.request.urlretrieve(url, out_path)
    return out_path



def compute_region_stats(image, aoi, scale=None, band=None):
    """
    Compute mean, min, max, stdDev of an image over the study area.
    Returns a Python dict.
    """
    if scale is None:
        scale = CHIRPS_SCALE
    if band is not None:
        image = image.select(band)

    stats = image.reduceRegion(
        reducer=(ee.Reducer.mean()
                   .combine(ee.Reducer.minMax(), sharedInputs=True)
                   .combine(ee.Reducer.stdDev(), sharedInputs=True)),
        geometry=aoi.geometry() if hasattr(aoi, 'geometry') else aoi,
        scale=scale,
        maxPixels=1e10,
    )
    return stats.getInfo()
