
# coding: utf-8

# #Testing Xray on weather forecast model data

# In[21]:

import xray
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
get_ipython().magic(u'matplotlib inline')


# In[22]:

URL = 'http://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p5deg/Best'


# In[23]:

ds = xray.open_dataset(URL)


# In[24]:

ds


# In[25]:

# select lat,lon region of interest
# note: slice(20.5,55.0) fails
dsloc = ds.sel(lon=slice(230.5,300.0),lat=slice(55.0,20.5))


# In[26]:

# select closest data to time of interest
#date = datetime.datetime(2015,7,15,3,0,0)
date = datetime.datetime.now()
ds_snapshot = dsloc.sel(time=date,time1=date,time2=date,method='nearest')


# In[27]:

ds.data_vars


# In[28]:

ds.coords


# In[29]:

ds.attrs


# In[30]:

t = ds_snapshot['Temperature_surface']


# In[40]:

t.time.values


# In[32]:

plt.pcolormesh(t.lon.data,t.lat.data,t.data)
plt.title(t.name+pd.Timestamp(t.time.values).strftime(': %Y-%m-%d  %H:%M:%S %Z %z'));


# In[33]:

# time series closest to specified lon,lat location
ds_series = ds.sel(lon=250.,lat=33.,method='nearest')


# In[34]:

# Select temperature and convert to Pandas Series
v_series = ds_series['Temperature_surface'].to_series()


# In[35]:

v_series.plot(title=v_series.name);


# In[36]:

ds_snapshot


# In[37]:

#ds_snapshot.to_netcdf('ds_snapshot.nc')


# In[ ]:



