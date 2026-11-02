# Course data

Small files used by the lessons, kept tiny so the course works offline.

## Part A

| File | What it is | Source |
| --- | --- | --- |
| `nepal_peaks.csv` | Nepal's eight peaks above 8,000 m: height, first ascent year, province, approximate summit coordinates (WGS84) | Heights and ascent years are standard published values; coordinates are approximate |
| `practice_rainfall.csv` | Monthly rainfall at six stations | **Made-up practice data.** Station names are labels (Station A–F); values follow a realistic monsoon pattern but are not measurements |
| `practice_landslides.csv` | 40 landslide records: date, district, location, area, trigger | **Made-up practice data.** Real district names, and each point lies inside its district, but the records are invented for exercises |

## Part B

| File | What it is | Source and licence |
| --- | --- | --- |
| `nepal_districts.geojson` | The 77 districts of Nepal: `district`, `district_code`, `province_code` | [geoJSON-Nepal](https://github.com/mesaugat/geoJSON-Nepal) by Saugat Acharya (MIT licence), derived from the OCHA common operational boundaries produced by the Survey Department of Nepal. Simplified to about 300 m so the file stays small; neighbouring districts still share exactly the same borders |
| `nepal_provinces.geojson` | The 7 provinces, made by dissolving the districts above | As above |
| `province_names.csv` | Province code, number and name (a plain table, joined to the maps in Lesson B6) | Official province names |
| `district_headquarters.geojson` | 75 district headquarters (points). There are 75, not 77, because this layer predates the split of Nawalparasi and Rukum | geoJSON-Nepal (MIT licence) |
| `world_countries.geojson` | Countries of the world at 1:110 million scale, for location maps | [Natural Earth](https://www.naturalearthdata.com/) (public domain) |
| `everest_trek.csv` | Eight stops on the Lukla–Everest Base Camp trek with elevation | Approximate coordinates and commonly cited elevations, for teaching |

## Part C

| File | What it is | Source and licence |
| --- | --- | --- |
| `dem_kathmandu_melamchi.tif` | Digital elevation model of the Kathmandu Valley and Sindhupalchok (85.2–85.8° E, 27.55–28.0° N), 1 arc-second (about 30 m) cells, WGS84, elevations in whole metres (`int16`) | Clipped from the Copernicus DEM GLO-30 tile N27 E085 (see the notice below) |
| `practice_landslides_melamchi.csv` | 60 landslide points inside the DEM area, with area | **Made-up practice data.** Points were placed at random, more often on slopes steeper than about 15°, to imitate how real landslides favour steep ground. They are not observations |
| `practice_rain_gauges.csv` | 24 rain gauges with elevation and annual rainfall | **Made-up practice data.** Rainfall was set to rise with elevation plus random noise; the values are not measurements |

**Copernicus DEM notice (required by its licence).** `dem_kathmandu_melamchi.tif` was produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30. This course is not endorsed by the Copernicus programme, the European Union, ESA, DLR or Airbus. Anyone who redistributes this file must keep this notice.

## Part D

| File | What it is | Source and licence |
| --- | --- | --- |
| `s2_melamchi_before.tif` | Sentinel-2 Level-2A surface reflectance of the Melamchi valley, 29 October 2020: 10 bands (B02, B03, B04, B05, B06, B07, B08, B8A, B11, B12), resampled to one 20 m grid in UTM 45N (EPSG:32645), 1006 × 702 cells, `uint16`, nodata 0. Multiply by 0.0001 for reflectance | Copernicus Sentinel-2 (free and open), through Microsoft Planetary Computer; made with `get_sentinel2_melamchi.py` |
| `s2_melamchi_after.tif` | The same grid and bands, 11 November 2021, after the June 2021 Melamchi flood | As above |
| `s2_melamchi_scenes.csv` | The two scenes used, with dates and cloud cover | As above |
| `worldcover_melamchi_2021.tif` | ESA WorldCover 2021 land cover on the same 20 m grid as the Sentinel-2 images (the most common 10 m class in each 20 m cell), `uint8`, nodata 0. Codes: 10 tree cover, 30 grassland, 40 cropland, 50 built-up, 60 bare or sparse vegetation, 80 permanent water | [ESA WorldCover](https://esa-worldcover.org/) 2021 (v200), CC BY 4.0, through Microsoft Planetary Computer; made with `get_worldcover_melamchi.py` |

**Sentinel-2 credit (required).** Contains modified Copernicus Sentinel data 2020–2021, processed by ESA.

**WorldCover credit (required, CC BY 4.0).** © ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.

## Extra lessons (A11, D5, D6)

| File | What it is | Source and licence |
| --- | --- | --- |
| `rain_daily_melamchi_kathmandu.csv` | Daily rainfall (`rain_mm`) and mean air temperature (`temp_mean_c`) for 2001–2024 at two places, Melamchi (27.83° N, 85.57° E) and Kathmandu (27.70° N, 85.32° E): 8,766 days each. Columns `date`, `place`, `rain_mm`, `temp_mean_c` | Open-Meteo historical weather API (CC BY 4.0), values from the **ERA5 reanalysis** of the Copernicus Climate Change Service. ERA5 cells are about 25–30 km wide: these are model estimates for a large area, not rain-gauge measurements, and they smooth out local extremes |
| `osm_melamchi_roads.graphml` | The road network of the Melamchi valley (854 junctions, 1,942 road segments): motorable roads and tracks, as a graph for osmnx and networkx | © OpenStreetMap contributors, ODbL; downloaded with osmnx |
| `osm_melamchi.gpkg` | The same roads as lines (layer `roads`), rivers and streams (`rivers`) and named places (`places`) | © OpenStreetMap contributors, ODbL |
| `s2_melamchi_timeseries_100m.nc` | Sentinel-2 L2A time series of the Part D box, 2019–2023: the 2 clearest dates of each month (112 dates), bands B04, B08, B11 and the scene classification `SCL`, 100 m cells, UTM 45N, NetCDF. Reflectance = value × 0.0001 (ESA's 2022 offset removed), 0 = no data | Copernicus Sentinel-2 (free and open), through Microsoft Planetary Computer |

**Credits (required).** Weather data by Open-Meteo.com (CC BY 4.0), from the ERA5 reanalysis of the Copernicus Climate Change Service. Map data © OpenStreetMap contributors, available under the Open Database Licence (ODbL). Contains modified Copernicus Sentinel data 2019–2023, processed by ESA.

Spellings follow the source data, which sometimes differ from common usage: for example the boundary layer writes **Chitawan**, while the practice landslide file writes **Chitwan**. Lesson B6 shows how to find and fix such mismatches, a very common problem with real data.

`make_data.py` rebuilds the Part B files and the Part C DEM from the original sources. The made-up practice files are kept as they are.

`get_sentinel2_melamchi.py` downloads the two Sentinel-2 images of Part D, `get_worldcover_melamchi.py` the ESA WorldCover 2021 land-cover map on the same grid, and `get_extra_data.py` the files of lessons A11, D5 and D6. They use Microsoft Planetary Computer, Open-Meteo and OpenStreetMap, none of which needs an account; run them once in the PyGILE-Plus container or the `pygile` environment.
