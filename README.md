# Solid Waste Quick Assessment Tool
> Quickly compute, and display on a map, the amount of solid waste generated per week per municipal jurisdiction, and the amount of uncollected solid waste per service area. Applicable to any of the around 30+ countries covered by the [HRSL](https://ciesin.columbia.edu/data/hrsl/#data) at 1 arc-second resolution (2015 data) or globally at 30 arc-second resolution through the [GPW](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count-rev11/data-download) raster (2000, 2005, 2010, 2015 and 2020 data).   

This script will compute two statistics (both in metric tonnes): the amount of solid waste generated per week per municipal jurisdiction, and the amount of uncollected solid waste generated in each 'service area', i.e. the area of a municipal jurisdiction for which a service provider (e.g. contractor or municipal department) provides solid waste collection services.

Both statitistcs are presented in a rank-ordered list and as a choropleth map. The example below shows the outputs for Lagos State in Nigeria, using dummy data for service areas.

![Screen capture of outputs 1 and 2](output1and2.png)
![Screen capture of output 3](output3.png)

## Installation

If you are new to Python, the easiest way to run the script on a specific jurisdiction would be to first install a scientific Python distribution like [Anaconda](https://docs.anaconda.com/anaconda/install/). Anaconda comes with 250 scientific and analytic so-called 'packages' such as NumPy, Pandas, SciPy, Matplotlib, and IPython pre-installed. The Anaconda [Cheat Sheet](https://docs.anaconda.com/_downloads/9ee215ff15fde24bf01791d719084950/Anaconda-Starter-Guide.pdf) offers a good 2-page introduction.

Anaconda includes the [conda](https://conda.io/en/latest/) command line interface as well the graphical user interface (GUI) **Navigator**.

> Anaconda is available for Windows 7 and newer, macOS 10.10 and newer, or any Linux distribution with a glibc version greater than 2.12 (CentOS 6). It requires 3GB of free hard drive space (Miniconda, a much smaller installer containing only Conda and its dependencies, needs only 400 MB). The environment required for this script (usually to then be found under `C:\User\YOURUSERNAME\anaconda3\env\` will take up an additional 1.9GB.

The following dependencies are required:

```sh
  - python=3.8.8
  - geopandas=0.9.0
  - cartopy=0.18.0
  - notebook=6.2.0
  - rasterio=1.2.0
  - rasterstats=0.14.0
```

To ensure access to these packages and avoid [dependency hell](https://en.wikipedia.org/wiki/Dependency_hell), it is necessary to set up an _environment_, the requirements for which are contained in the `environment.yml` file in the root of this repository (or 'repo').

After [forking](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) this repo, open Navigator, click on the **Import** button at the bottom of the **Environments** tab, navigate to the `environment.yml` file in the root folder of your local repo, and click **Import**. Setting up the environment with all its packages and dependencies may take a few minutes.

## Running the script

#### Required source files

The script requires three source files:

1. a vector source indicating the administrative boundaries for a superordinate sub-national government tier (e.g. the state level) and a second subordinate tier (e.g. the municipal level):
 > the present sample script uses the administrative boundaries for Nigeria available at [humdata.org](https://data.humdata.org/dataset/nga-administrative-boundaries);
2. another vector source representing service areas including an attribute field or column indicating the total amount of solid waste collected per week by each contractor/service provider in metric tonnes:
 > the present sample script uses dummy polygons and hypothetical collection totals assuming a 21% collection rate, the sample shapefiles are available in the `data_files` folder of the GitHub repo;        
3. the pop GeoTIFF of the CIESIN [High-Resolution Settlements Layer (HRSL)](https://ciesin.columbia.edu/data/hrsl/#data) providing the number of persons estimated to haved lived in each 1 arc-second pixel (roughly 30m) in 2015, available for roughly 30 countries in Africa, Asia and Latin America, **or** the [Gridded World Population](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4) layer which has global coverage, covers 5 year periods from 2000 to 2020 but only has a 30 arc-second resolution (roughly 1km).
 > the present sample script uses the HRSL for Nigeria available [here](https://ciesin.columbia.edu/data/hrsl/#data).

#### Required script adjustments

The script will need to be adjusted in the `# USER INPUTS` section to specify data sources and adjust variables according to context. These are:

1. the `fp_adm` variable indicating the filepath to the administrative boundaries data source;
2. the `state_name_field` variable indicating the name of the column containing the names of the superordinate (e.g. state-level) jurisdictions. If this information is in a data source separate from the subordinate tier, a spatial join via GeoPandas or a desktop GIS may be necessary;
3. the `state_select` variable to select which state you want to perform the analysis on;
4. the `mun_name_field` variable indicating the name of the column containing the names of municipalities;
5. the `fp_service_areas` variable indicating the filepath to the service areas data source;
6. the `provider_name_field` variable indicating the name of the column containing the names of service providers;
7. the `provider_coll_field` variable indicating the name of the column containing the weekly collection totals reported
8. the `fp_raster` variable indicating the filepath to the raster data source;
9. the `sw_ppd` variable indicating the amount of solid waste generated per capita per day in kilograms, according to your particular context (the map annotation will be adjusted automatically)

#### How to run the script from the command line

Still in Navigator, head to the **Home** tab, select **'swmtool'** from the **Applications on:** drop-down menu, and click the **Launch** button underneath **'CMD.exe Prompt'** or **Install** if you do not see the Launch button.

![Screen capture of Anaconda Home tab][instructions_01.png]

A command prompt window will open starting with `(swmtool)` followed by your location in the starting directory, usually `C:\Users\YOURUSERNAME>`. Copy the path to your local repo to your clipboard and enter (without the square brackets)

```sh
cd [PATH]
```
followed by

```sh
ipython -i script.py
```
to have the IPython interpreter execute the script in interactive mode. This will produce outputs 1 and 2. To see the choropleth maps, enter

```sh
plt.show()
```

Edits to the script will be reflected in the IPython command prompt window.

#### How to run the script from inside an IDE or text editor

To more fluidly edit the script and see the results side-by-side in the same window, you may want to consider using an IDE or code editor with a Python extension. A number of options like [PyCharm](https://www.jetbrains.com/pycharm/) or [Spyder](https://www.spyder-ide.org/) are available, with [Visual Studio Code's Python Extension](https://code.visualstudio.com/docs/languages/python) pictured below. 

![Screenshot of the Visual Studio Code Python Extension][instructions_02.png]

Adding `# %%` to the top of the script turns the script into a [Jupyter-like code cell](https://code.visualstudio.com/docs/python/jupyter-support-py) which allows for a seamless workflow of editing and results visualization in the same window. Simply edit the script on the left and hit `Shift + Enter`to execute and display the results in the interactive interpreter on the right.

#### Expected Outputs

The script will return three outputs:
1. a list of municipalities by amount of solid waste generated per week in metric tonnes, in descending order;
2. a list of service providers by amount of uncollected solid waste per week in metric tonnes, in descending order;
3. choropleth maps visualizing each list using a scalar colormap (blues for (1) and reds for (2)).

#### Optional customization

Changing the `stat_select` variable to another statistic supported by rasterstats (such as min, max, mean etc.) is also possible, though then the array algebra and the title of the choropleth maps (via `var_name`) will need to be adjusted accordingly.  

## Release History

* 0.1.0
    * first release

## Meta

Gregor Herda – gregorherda at gmail.com

The Solid Waste Quick Assessment Tool is licensed under the terms of the GNU General Public License v3.0 and is available for free. See ``LICENSE`` for more information.

[https://github.com/gregorhuh](https://github.com/gregorhuh)

## How to Contribute

1. Fork it (<https://github.com/gregorhuh/UU_egm722_project/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request with comprehensive description of changes

## Acknowledgements

* @iamdonovan for his assistance in fixing the affine argument

<!-- Markdown link & img dfn's -->
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square


