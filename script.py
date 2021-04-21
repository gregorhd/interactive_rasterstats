#%%

# Total population for each of Lagos State's 20 Local Government Areas
import numpy as np
import pandas as pd
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import rasterio as rio
from rasterstats import zonal_stats
import matplotlib.pyplot as plt

# This script calculates zonal statistics for a set of polygons

def getNamesStats(name_select, stat_select):
    stat_list = zonal_stats(municipal_filter, array, affine=affine, nodata=nodata, stats=stat_select, geojson_out=True)
    for feature_dict in stat_list:
        mun_name = feature_dict['properties'][name_select]
        mun_stat = feature_dict['properties'][stat_select]
        mun_names.append(mun_name)
        mun_stats.append(mun_stat)

# 1. LOAD HIGH RESOLUTION SETTLEMENTS LAYER

# Continuous floating point raster layer by CIESIN representing number of persons per 30x30m grid cell
# Source (Nigeria): https://ciesin.columbia.edu/data/hrsl/#data

with rio.open('data_files/01_input/02_raster/hrsl_nga_pop.tif') as dataset:

    crs = dataset.crs
    nodata = dataset.nodata
       
    # LOAD ADMINISTRATIVE BOUNDARIES VECTOR DATA

    # load Nigeria Local Government Area boundaries (Level 2, 'ADM2_EN'), and select only those LGAS within the larger Lagos State administrative boundary (Level 1, 'ADM1_EN')
    # Source: https://data.humdata.org/dataset/nga-administrative-boundaries#

    fp_adm = 'data_files/01_input/01_vector/nga_admbnda_adm2_osgof_20190417.shp'

    municipal_all = gpd.read_file(fp_adm).to_crs(crs)

    state_select = 'Lagos'

    municipal_filter = municipal_all[municipal_all['ADM1_EN'] == state_select]

    # DEFINE STUDY AREA BASED ON VECTOR SELECTION
    
    bbox = municipal_filter.total_bounds
    window = dataset.window(*bbox)

    # coords for centering free text to be plotted later
    minx, miny, maxx, maxy = municipal_filter.total_bounds
    centery = maxy - ((maxy - miny) / 2)


    # CREATE NUMPY ND ARRAYS

    # loading a subset of the HRSL corresponding to the study area
    pop_array = dataset.read(1, window=window)
    affine = dataset.window_transform(window)
    pop_array[(pop_array < 0)] = np.nan # sets negative NoData values to NaN to enable array algebra
    
    # Calculate tons of solid waste produced per grid cell rson per week

    sw_ppd = 0.79 # solid waste per capita per day in kilograms

    sw_ppd_array = pop_array * sw_ppd # converts population to solid waste per person and day

    sw_ppw_array = sw_ppd_array * 7 # converts daily figures to weekly

    array = sw_ppw_array / 1000 # converts kilograms to tons per week (TPW)
    
    # CALCULATE ZONAL STATS
    
    # Label and select statistic, identify column containing polygon names
    var_name = 'Tonnes of solid waste per week' # variable name displayed as part of the figure title
    stat_select = 'sum' # the rasterstats zonal statistic to be computed for each jurisdiction
    name_select = 'ADM2_EN' # name of the GeoDataFrame field containing the names of jurisdictions
    
    # empty lists of all polygon names and zonal stats to populated by function
    mun_names = []
    mun_stats = []    

    # run function
    getNamesStats(name_select, stat_select)

    # REFORMAT RESULTS FOR PRESENTATION

    # combine populated lists into one dictionary
    mun_dict = dict(zip(mun_names, mun_stats))
    
    # sort dictionary by value in descending order into list of tuples
    mun_dict_sorted = sorted(mun_dict.items(), key=lambda x: x[1], reverse=True) 

    # print the items in the sorted list
    print('LGAs in descending order by solid waste generated per week\n')
    for i in mun_dict_sorted:
        print(i[0],':',f"{int(i[1]):,}", 'tonnes')
    
    # Find the top 3 municipalities, sorted by zonal stat

    top1 = mun_dict_sorted[0][0]
    top2 = mun_dict_sorted[1][0]
    top3 = mun_dict_sorted[2][0]

    # Assign zonal statistics to new column 'stat_output' in municipal_filter GDF

    municipal_filter = municipal_filter.assign(
        stat_output = pd.Series(mun_stats, index = municipal_filter.index)
    )
    
    # DISPLAY RESULTS

    # Define figure CRS and canvas layout

    myCRS = ccrs.Mercator()

    fig, ax = plt.subplots(1, 1, figsize=(10, 5), subplot_kw=dict(projection=myCRS))

    # add municipal boundaries to plot

    municipal_feat = ShapelyFeature(municipal_filter['geometry'], myCRS, facecolor='none', edgecolor='k', linewidth=0.5)
    ax.add_feature(municipal_feat)

    # add name of top 3 municipalities to plot
    ax.text(minx, centery, '1. ' + top1 + '\n' + '2. ' + top2 + '\n' + '3. ' + top3, transform=myCRS, fontsize=12)

    # add dynamic title and annotation

    title = var_name + ' by LGA in ' + state_select + ' State'
    ax.set_title(title, fontdict={'fontsize': '12', 'fontweight' : '5'})
    
    ax.axis('off')
    
    ax.annotate('Source: CIESIN HRSL, assuming ' + str(sw_ppd) + 'kg of solid waste per capita per day', xy=(0.225, .025), xycoords='figure fraction', fontsize=12, color='#555555')

    # Create colorbar legend

    vmin, vmax =  municipal_filter['stat_output'].min(), municipal_filter['stat_output'].max()

    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))

    sm.set_array([])

    fig.colorbar(sm, ax=ax, orientation="horizontal")

    municipal_filter.plot(column='stat_output', cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')

    # Show the plot
    

# %%
