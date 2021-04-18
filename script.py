#%%

# Total population for each of Lagos State's 20 Local Government Areas
import numpy as np
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import rasterio as rio
from rasterio.plot import show
from rasterstats import zonal_stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# 1. LOAD HIGH RESOLUTION SETTLEMENTS LAYER

# Continuous floating point raster layer by CIESIN representing population estimates per 30m cell
# Source (Nigeria): https://ciesin.columbia.edu/data/hrsl/#data

with rio.open('data_files/01_input/02_raster/hrsl_nga_pop.tif') as dataset:

    crs = dataset.crs
    affine = dataset.transform
   
    # 2. LOAD VECTOR DATA

    # 2.a load Nigeria Local Government Area boundaries (Level 2), and select only those LGAS within Lagos State
    # Source: https://data.humdata.org/dataset/nga-administrative-boundaries#

    municipal_all = gpd.read_file('data_files/01_input/01_vector/nga_admbnda_adm2_osgof_20190417.shp').to_crs(crs)

    municipal_filter = municipal_all[municipal_all['ADM1_EN'] == 'Lagos']

    # 2.b Define the study area
    xmin, ymin, xmax, ymax = municipal_filter.total_bounds

    # 2.c Create nd array based on study area
    # load a subset of the HRSL corresponding to the study area
    
    top, lft = dataset.index(xmin, ymax) # turns real coords for top left into pixel indices
    bot, rgt = dataset.index(xmax, ymin) # turns real coords for bottom right into pixel indices

    pop_array = dataset.read(1, window=((top, bot), (lft, rgt)))
   
    # 3. CALCULATING ZONAL STATS

    municipal_pop_sum = zonal_stats(municipal_filter, pop_array, affine=affine, nodata=0, stats=['sum'], geojson_out=False)

    # 3.a Extract sums only

    print(municipal_pop_sum)

    # 4. DISPLAY RESULTS

    # 4.a Define figure CRS and canvas layout (subplot 2 to present further results)

    myCRS = ccrs.Mercator()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), subplot_kw=dict(projection=myCRS), gridspec_kw=dict(height_ratios=[1, 2]))

    # 4.b Add raster image

    ax1.imshow(pop_array, cmap='viridis', transform=myCRS, extent=[xmin, xmax, ymin, ymax])

    # 4.c Add LGA boundaries

    municipal_feat = ShapelyFeature(municipal_filter['geometry'], myCRS, facecolor='none', edgecolor='w', linewidth=1)
    ax1.add_feature(municipal_feat)

    




# %%

# %%
