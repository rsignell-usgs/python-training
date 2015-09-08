
# coding: utf-8

# <img style='float: left' width="150px" src="http://bostonlightswim.org/wp/wp-content/uploads/2011/08/BLS-front_4-color.jpg">
# <br><br>
# 
# ## [The Boston Light Swim](http://bostonlightswim.org/)
# 
# ### Fetch Sea Surface Temperature time-series data

# In[1]:

import time

start_time = time.time()


# ### Save configuration

# In[2]:

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

import iris
from datetime import datetime, timedelta
from utilities import CF_names, start_log

# Today +- 4 days
today = datetime.utcnow()
today = today.replace(hour=0, minute=0, second=0, microsecond=0)

start = today - timedelta(days=4)
stop = today + timedelta(days=4)

# Boston harbor.
spacing = 0.25
bbox = [-71.05-spacing, 42.28-spacing,
        -70.82+spacing, 42.38+spacing]

# CF-names.
sos_name = 'sea_water_temperature'
name_list = CF_names[sos_name]

# Units.
units = iris.unit.Unit('celsius')

# Logging.
run_name = '{:%Y-%m-%d}'.format(stop)
log = start_log(start, stop, bbox)

# Config.
fname = os.path.join(run_name, 'config.pkl')
config = dict(start=start,
              stop=stop,
              bbox=bbox,
              name_list=name_list,
              units=units,
              run_name=run_name)

with open(fname, 'wb') as f:
    pickle.dump(config, f)


# ### Create the data filter

# In[3]:

from owslib import fes
from utilities import fes_date_filter

kw = dict(wildCard='*',
          escapeChar='\\',
          singleChar='?',
          propertyname='apiso:AnyText')

or_filt = fes.Or([fes.PropertyIsLike(literal=('*%s*' % val), **kw)
                  for val in name_list])

# Exclude ROMS Averages and History files.
not_filt = fes.Not([fes.PropertyIsLike(literal='*Averages*', **kw)])

begin, end = fes_date_filter(start, stop)
filter_list = [fes.And([fes.BBox(bbox), begin, end, or_filt, not_filt])]


# In[4]:

from owslib.csw import CatalogueServiceWeb

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'
csw = CatalogueServiceWeb(endpoint, timeout=60)
csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')

fmt = '{:*^64}'.format
log.info(fmt(' Catalog information '))
log.info("URL: {}".format(endpoint))
log.info("CSW version: {}".format(csw.version))
log.info("Number of datasets available: {}".format(len(csw.records.keys())))


# In[5]:

from utilities import service_urls

dap_urls = service_urls(csw.records, service='odp:url')
sos_urls = service_urls(csw.records, service='sos:url')

log.info(fmt(' CSW '))
for rec, item in csw.records.items():
    log.info('{}'.format(item.title))

log.info(fmt(' SOS '))
for url in sos_urls:
    log.info('{}'.format(url))

log.info(fmt(' DAP '))
for url in dap_urls:
    log.info('{}.html'.format(url))


# In[6]:

from utilities import is_station

# Filter out some station endpoints.
non_stations = []
for url in dap_urls:
    try:
        if not is_station(url):
            non_stations.append(url)
    except RuntimeError as e:
        log.warn("Could not access URL {}. {!r}".format(url, e))

dap_urls = non_stations

log.info(fmt(' Filtered DAP '))
for url in dap_urls:
    log.info('{}.html'.format(url))


# ### NdbcSos

# In[7]:

from pyoos.collectors.ndbc.ndbc_sos import NdbcSos

collector_ndbc = NdbcSos()

collector_ndbc.set_bbox(bbox)
collector_ndbc.end_time = stop
collector_ndbc.start_time = start
collector_ndbc.variables = [sos_name]

ofrs = collector_ndbc.server.offerings
title = collector_ndbc.server.identification.title
log.info(fmt(' NDBC Collector offerings '))
log.info('{}: {} offerings'.format(title, len(ofrs)))


# In[8]:

from utilities import collector2table, to_html, get_ndbc_longname

ndbc = collector2table(collector=collector_ndbc)

names = []
for s in ndbc['station']:
    try:
        name = get_ndbc_longname(s)
    except ValueError:
        name = s
    names.append(name)

ndbc['name'] = names

ndbc.set_index('name', inplace=True)
to_html(ndbc.head())


# ### CoopsSoS

# In[9]:

from pyoos.collectors.coops.coops_sos import CoopsSos

collector_coops = CoopsSos()

collector_coops.set_bbox(bbox)
collector_coops.end_time = stop
collector_coops.start_time = start
collector_coops.variables = [sos_name]

ofrs = collector_coops.server.offerings
title = collector_coops.server.identification.title
log.info(fmt(' Collector offerings '))
log.info('{}: {} offerings'.format(title, len(ofrs)))


# In[10]:

from utilities import get_coops_metadata

coops = collector2table(collector=collector_coops)

names = []
for s in coops['station']:
    try:
        name = get_coops_metadata(s)[0]
    except ValueError:
        name = s
    names.append(name)

coops['name'] = names

coops.set_index('name', inplace=True)
to_html(coops.head())


# ### Join CoopsSoS and NdbcSos

# In[11]:

from pandas import concat

all_obs = concat([coops, ndbc])

to_html(all_obs.head())


# In[12]:

fname = '{}-all_obs.csv'.format(run_name)
fname = os.path.join(run_name, fname)
all_obs.to_csv(fname)


# ### Download the observed data series

# In[13]:

from pandas import DataFrame
from owslib.ows import ExceptionReport
from utilities import pyoos2df, save_timeseries

iris.FUTURE.netcdf_promote = True

log.info(fmt(' Observations '))
outfile = '{:%Y-%m-%d}-OBS_DATA.nc'.format(stop)
outfile = os.path.join(run_name, outfile)


log.info(fmt(' Downloading to file {} '.format(outfile)))
data = dict()
col = 'sea_water_temperature (C)'
for station in all_obs.index:
    try:
        idx = all_obs['station'][station]
        df = pyoos2df(collector_ndbc, idx, df_name=station)
        if df.empty:
            df = pyoos2df(collector_coops, idx, df_name=station)
        data.update({idx: df[col]})
    except ExceptionReport as e:
        log.warning("[{}] {}:\n{}".format(idx, station, e))


# ### Uniform 1-hour time base for model/data comparison

# In[14]:

from pandas import date_range

index = date_range(start=start, end=stop, freq='1H')
for k, v in data.iteritems():
    data[k] = v.reindex(index=index, limit=1, method='nearest')

obs_data = DataFrame.from_dict(data)


# In[15]:

comment = "Several stations from http://opendap.co-ops.nos.noaa.gov"
kw = dict(longitude=all_obs.lon,
          latitude=all_obs.lat,
          station_attr=dict(cf_role="timeseries_id"),
          cube_attr=dict(featureType='timeSeries',
                         Conventions='CF-1.6',
                         standard_name_vocabulary='CF-1.6',
                         cdm_data_type="Station",
                         comment=comment,
                         url=url))

save_timeseries(obs_data, outfile=outfile,
                standard_name=sos_name, **kw)

to_html(obs_data.head())


# ### Loop discovered models and save the nearest time-series

# In[16]:

import warnings
from iris.exceptions import (CoordinateNotFoundError, ConstraintMismatchError,
                             MergeError)
from utilities import (TimeoutException, quick_load_cubes, proc_cube,
                       time_limit, is_model, get_model_name, get_surface)

log.info(fmt(' Models '))
cubes = dict()
with warnings.catch_warnings():
    warnings.simplefilter("ignore")  # Suppress iris warnings.
    for k, url in enumerate(dap_urls):
        log.info('\n[Reading url {}/{}]: {}'.format(k+1, len(dap_urls), url))
        try:
            with time_limit(60*5):
                cube = quick_load_cubes(url, name_list,
                                        callback=None, strict=True)
                if is_model(cube):
                    cube = proc_cube(cube, bbox=bbox,
                                     time=(start, stop), units=units)
                else:
                    log.warning("[Not model data]: {}".format(url))
                    continue
                cube = get_surface(cube)
                mod_name, model_full_name = get_model_name(cube, url)
                cubes.update({mod_name: cube})
        except (TimeoutException, RuntimeError, ValueError,
                ConstraintMismatchError, CoordinateNotFoundError,
                IndexError, AttributeError) as e:
            log.warning('Cannot get cube for: {}\n{}'.format(url, e))


# In[17]:

from iris.pandas import as_series
from utilities import (make_tree, get_nearest_water,
                       add_station, ensure_timeseries, remove_ssh)

for mod_name, cube in cubes.items():
    fname = '{:%Y-%m-%d}-{}.nc'.format(stop, mod_name)
    fname = os.path.join(run_name, fname)
    log.info(fmt(' Downloading to file {} '.format(fname)))
    try:
        tree, lon, lat = make_tree(cube)
    except CoordinateNotFoundError as e:
        log.warning('Cannot make KDTree for: {}'.format(mod_name))
        continue
    # Get model series at observed locations.
    raw_series = dict()
    for station, obs in all_obs.iterrows():
        try:
            kw = dict(k=10, max_dist=0.08, min_var=0.01)
            args = cube, tree, obs.lon, obs.lat
            series, dist, idx = get_nearest_water(*args, **kw)
        except ValueError as e:
            status = "No Data"
            log.info('[{}] {}'.format(status, obs.name))
            continue
        if not series:
            status = "Land   "
        else:
            raw_series.update({obs['station']: series})
            series = as_series(series)
            status = "Water  "
        log.info('[{}] {}'.format(status, obs.name))
    if raw_series:  # Save cube.
        for station, cube in raw_series.items():
            cube = add_station(cube, station)
            cube = remove_ssh(cube)
        try:
            cube = iris.cube.CubeList(raw_series.values()).merge_cube()
        except MergeError as e:
            log.warning(e)
        ensure_timeseries(cube)
        iris.save(cube, fname)
        del cube
    log.info('Finished processing [{}]'.format(mod_name))


# In[18]:

elapsed = time.time() - start_time
log.info('{:.2f} minutes'.format(elapsed/60.))
log.info('EOF')

with open('{}/log.txt'.format(run_name)) as f:
    print(f.read())

