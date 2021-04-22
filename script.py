#%%
"""Solid Waste Assessment Tool

This script will compute two statistics: the amount of solid waste generated per week per municipal jurisdiction (in metric tonnes), and the amount of uncollected solid waste generated by 'service area', i.e. the area of a jurisdiction for which a service provider (e.g. contractor or municipal department) provides solid waste collection services.

Required source files

The script requires three source files:
    (1) a vector source indicating the administrative boundaries for both a first sub-national government tier (e.g. the state level) and a second tier (e.g. the municipal level):
        - the template below uses the administrative boundaries for Nigeria available here: https://data.humdata.org/dataset/nga-administrative-boundaries#;;
    (2) a vector source representing service areas including an attribute field or column indicating the total amount of solid waste collected per week by each contractor/service provider in metric tonnes ('total_coll'):
        - the template below uses dummy polygons and collection totals assuming a 21% collection rate, the shapefiles are available in the data_files folder of the GitHub repo;        
    (3) the pop GeoTIFF of a CIESIN High-Resolution Settlements Layer providing the number of persons estimated to live in each roughly 30x30m pixel (see 
        - the template below uses the HRSL for Nigeria available at https://ciesin.columbia.edu/data/hrsl/#data ;

Outputs

The script will return three outputs:
    (1) a list of municipalities by amount of solid waste generated per week in metric tonnes, in descending order;
    (2) a list of service providers by amount of uncollected solid waste per week in metric tonnes, in descending order;
    (3) choropleth maps visualizing each list using a scalar colormap (blues for (1) and reds for (2)).

Customizations

    - By changing the "stat_select" variable, other statistics supported by rasterstats (such as min, max, mean etc.) can also be generated.
    - By changing the "state_select" variable, the script will return the same outputs for municipalities in a different state (remember to also provide a source for the service areas, however)
    - By changing the 'sw_ppd' variable, different scenarios can be run with a different amount of solid waste generated per capita per day  

This script requires that `pandas` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * get_spreadsheet_cols - returns the column headers of the file
    * main - the main function of the script
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import rasterio as rio
from rasterstats import zonal_stats
import matplotlib.pyplot as plt

def getNamesStats(vector, array, name_field, feature_list, stat_list, stat_select='sum'):
    """Returns one list each of feature names and zonal statistics.

    Parameters
    ----------
    vector : path to a vector source or geo-like python object
        Python object can be a GeoPandas GeoDataFrame.
    raster : ndarray
        rasterstats alternative arg, 'path to a GDAL raster', not accepted.   
    name_field : str
        The vector source's column name containing feature names.
    feature_list : str
        Temp variable name for feature list. Must be unique in script as run consecutively.
    stat_list : str
        Temp variable name for statistics list. Must be unique in script.
    stat_select : str, optional
        String value for any statistic supported by zonal_stats (the default is 'sum').

    Returns
    ----------
    feature_list : list
        A list in alphabetical order containing the names of polygon features for which zonal stats are computed.
    stat_list : list
        A list containing the zonal statistics in the same order as "feature_list".
    """

    temp = zonal_stats(vector, array, affine=affine, nodata=nodata, stats=stat_select, geojson_out=True)
    
    for feature_dict in temp:
        feature_name = feature_dict['properties'][name_field]
        feature_stat = feature_dict['properties'][stat_select]
        feature_list.append(feature_name)
        stat_list.append(feature_stat)
        

def getPixelCount(vector, array, provider_field):
    stat_list = zonal_stats(vector, array, affine=affine, nodata=nodata, stats='count', geojson_out=True)
    for feature_dict in stat_list:
        provider_name = feature_dict['properties'][provider_field]
        provider_count = feature_dict['properties']['count']
        provider_names.append(provider_name)
        provider_counts.append(provider_count)

# 1. LOAD HIGH RESOLUTION SETTLEMENTS LAYER

# Continuous floating point raster layer by CIESIN representing number of persons per 30x30m grid cell
# Sample: Nigeria

fp_raster = 'data_files/01_input/02_raster/hrsl_nga_pop.tif'

with rio.open(fp_raster) as dataset:

    crs = dataset.crs
    nodata = dataset.nodata
       
    # LOAD ADMINISTRATIVE BOUNDARIES VECTOR DATA

    # load Nigeria Local Government Area boundaries (Level 2, 'ADM2_EN'), and select only those LGAS within the larger Lagos State administrative boundary (Level 1, 'ADM1_EN')

    fp_adm = 'data_files/01_input/01_vector/nga_admbnda_adm2_osgof_20190417.shp'

    municipal_all = gpd.read_file(fp_adm).to_crs(crs)

    state_name_field = 'ADM1_EN'
    state_select = 'Lagos'

    municipal_filter = municipal_all[municipal_all[state_name_field] == state_select]

    # DEFINE STUDY AREA BASED ON VECTOR SELECTION
    
    bbox = municipal_filter.total_bounds
    window = dataset.window(*bbox)

    # coords for centering free text to be plotted later
    minx, miny, maxx, maxy = municipal_filter.total_bounds

    # LOAD VECTOR DATA FOR SERVICE AREAS OF SOLID WASTE SERVICE PROVIDERS

    fp_service_areas = 'data_files/01_input/01_vector/service_areas.shp'
    
    # service_areas = gpd.read_file(fp_service_areas).to_crs(crs)
    service_areas = gpd.read_file(fp_service_areas).to_crs(crs)
    
    # CREATE NUMPY ND ARRAYS

    # loading a subset of the HRSL corresponding to the study area
    pop_array = dataset.read(1, window=window)
    affine = dataset.window_transform(window)
    pop_array[(pop_array < 0)] = np.nan # sets negative NoData values to NaN to enable array algebra
    
    # Calculate tons of solid waste produced per grid cell rson per week

    sw_ppd = 0.79 # solid waste per capita per day in kilograms

    sw_ppd_array = pop_array * sw_ppd # converts population to solid waste per person and day

    sw_ppw_array = sw_ppd_array * 7 # converts daily to weekly figures

    array = sw_ppw_array / 1000 # converts kilograms to tons per week (TPW)
    
    # CALCULATE ZONAL STATS - BASELINE GENERATION PER MUNICIPALITY
    
    # Label and select statistic, identify column containing polygon names
    var_name = 'Tonnes of solid waste generated per week' # variable name displayed as part of the figure title
    stat_select = 'sum' # the rasterstats zonal statistic to be computed for each jurisdiction
    mun_name_field = 'ADM2_EN' # name of the GeoDataFrame field containing the names of jurisdictions
    mun_names = []
    mun_stats = []

    
    # empty lists of all polygon names and zonal stats to be populated by function
   
    getNamesStats(municipal_filter, array, mun_name_field, mun_names, mun_stats)

    # CALCULATE ZONAL STATS - SOLID WASTE COLLECTED PER SERVICE AREA

    provider_name_field = 'psp_name'
    provider_coll_field = 'total_coll'

    provider_names = []
    provider_stats = []
    
    provider_counts = []
   
    provider_coll = service_areas[provider_coll_field].values.tolist()
    
    getPixelCount(service_areas, array, provider_name_field)

    getNamesStats(service_areas, array, provider_name_field, provider_names, provider_stats)

    # subtract the total waste collected from the total waste generated in each service area
    # and add this to new column 'total_uncoll' for the weekly total tonnage of uncollected waste

    
    

    provider_uncoll = []
    zip_object = zip(provider_stats, provider_coll)

    for i, j in zip_object:
        provider_uncoll.append(i - j)

    # REFORMAT RESULTS FOR PRESENTATION

    # combine populated lists into one dictionary
    mun_dict = dict(zip(mun_names, mun_stats))
    provider_dict = dict(zip(provider_names, provider_uncoll))
    
    # sort dictionary by value in descending order into list of tuples
    mun_dict_sorted = sorted(mun_dict.items(), key=lambda x: x[1], reverse=True)
    provider_dict_sorted = sorted(provider_dict.items(), key=lambda x: x[1], reverse=True) 

    # print the items in the sorted list
    print('Municipalities by solid waste generated per week (descending):\n')
    for i in mun_dict_sorted:
        print(i[0],':',f"{int(i[1]):,}", 'tonnes')

    print('\nService providers by total uncollected solid waste per week (descending)\n')
    for i in provider_dict_sorted:
        print(i[0],':',f"{int(i[1]):,}", 'tonnes')
    
    # Assign zonal statistics to new column 'stat_output' in municipal_filter GDF

    municipal_filter = municipal_filter.assign(
        stat_output = pd.Series(mun_stats, index = municipal_filter.index)
    )

    for i, row in service_areas.iterrows():
        service_areas.loc[i, 'total_uncoll'] = provider_stats[i] - row[provider_coll_field]
    
    # DISPLAY RESULTS

    # Define figure CRS and canvas layout

    myCRS = ccrs.Mercator()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7.5), subplot_kw=dict(projection=myCRS))

    # add municipal boundaries to plot

    municipal_feat = ShapelyFeature(municipal_filter['geometry'], myCRS, facecolor='none', edgecolor='k', linewidth=0.5)
    ax1.add_feature(municipal_feat)

    # add dynamic title and annotation

    title = var_name + ' by municipalities in ' + state_select + ' State'
    ax1.set_title(title, fontdict={'fontsize': '12', 'fontweight' : '5'})
    
    ax1.axis('off')
    
    ax1.annotate('Source: CIESIN HRSL, assuming ' + str(sw_ppd) + 'kg of solid waste per capita per day', xy=(0.225, .025), xycoords='figure fraction', fontsize=12, color='#555555')

    # Create colorbar legend

    vmin, vmax =  municipal_filter['stat_output'].min(), municipal_filter['stat_output'].max()

    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))

    sm.set_array([])

    fig.colorbar(sm, ax=ax1, orientation="horizontal")

    municipal_filter.plot(column='stat_output', cmap='Blues', linewidth=0.8, ax=ax1, edgecolor='0.8')

    # Sub-plot 2

    # add dynamic title and annotation

    title2 = 'Tonnes of uncollected solid waste per week by service area (dummy data)'
    ax2.set_title(title2, fontdict={'fontsize': '12', 'fontweight' : '5'})
    
    ax2.axis('off')

    # Create colorbar legend

    vmin2, vmax2 =  service_areas['total_uncoll'].min(), service_areas['total_uncoll'].max()

    sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize(vmin=vmin2, vmax=vmax2))

    sm.set_array([])

    fig.colorbar(sm, ax=ax2, orientation="horizontal")

    municipal_filter.plot(facecolor='none', linewidth=0.5, ax=ax2, edgecolor='k')

    service_areas.plot(column='total_uncoll', cmap='Reds', linewidth=0.8, ax=ax2, edgecolor='k')

    
   
    

# %%
