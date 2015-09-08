
# coding: utf-8

# #Testing Xray on weather forecast model data

# In[18]:

import xray
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
get_ipython().magic(u'matplotlib inline')


# In[19]:

URL = 'http://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p5deg/Best'


# In[20]:

ds = xray.open_dataset(URL)


# In[21]:

ds


# In[22]:

# select lat,lon region of interest
# note: slice(20.5,55.0) fails
dsloc = ds.sel(lon=slice(230.5,300.0),lat=slice(55.0,20.5))


# In[23]:

# select closest data to time of interest
#date = datetime.datetime(2015,7,15,3,0,0)
date = datetime.datetime.now()
ds_snapshot = dsloc.sel(time=date,time1=date,time2=date,method='nearest')


# In[24]:

ds.data_vars


# In[25]:

ds.coords


# In[26]:

ds.attrs


# In[27]:

t = ds_snapshot['Temperature_surface']


# In[28]:

t.shape


# In[29]:

plt.pcolormesh(t.lon.data,t.lat.data,t.data)
plt.title(t.name+pd.Timestamp(t.time.values).strftime(': %Y-%m-%d  %H:%M:%S %Z %z'));


# In[30]:

# time series closest to specified lon,lat location
ds_series = ds.sel(lon=250.,lat=33.,method='nearest')


# In[31]:

# Select temperature and convert to Pandas Series
v_series = ds_series['Temperature_surface'].to_series()


# In[32]:

v_series.plot(title=v_series.name);


# In[33]:

ds_snapshot


# In[34]:

#ds_snapshot.to_netcdf('ds_snapshot.nc')


# In[ ]:



