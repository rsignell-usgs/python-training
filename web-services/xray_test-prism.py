
# coding: utf-8

# ##Testing Xray on the PRISM data

# In[2]:

import xray
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
get_ipython().magic(u'matplotlib inline')


# In[3]:

URL = 'http://cida.usgs.gov/thredds/dodsC/prism_v2'


# In[4]:

ds = xray.open_dataset(URL)


# In[5]:

ds


# In[6]:

# select lat,lon region of interest
# note: slice(20.5,55.0) fails
dsloc = ds.sel(lon=slice(-75.0,-69.0),lat=slice(45.0,40.0))


# In[7]:

dsloc


# In[8]:

# select closest data to time of interest
date = datetime.datetime(2005,8,1,0,0)
#date = datetime.datetime.now()
ds_snapshot = dsloc.sel(time=date,method='nearest')


# In[10]:

ds_snapshot.data_vars
# ds.coords
# ds.attrs


# In[11]:

t = ds_snapshot['ppt']


# In[12]:

t.shape


# In[15]:

tvals = t.data


# In[16]:

tvals


# In[18]:

tvals = np.ma.masked_invalid(t.data)


# In[19]:

tvals


# In[20]:

plt.pcolormesh(t.lon.data,t.lat.data,tvals)
plt.title(t.name+pd.Timestamp(t.time.values).strftime(': %Y-%m-%d  %H:%M:%S %Z %z'));
plt.colorbar();


# In[21]:

tvals.min()


# In[22]:

# time series closest to specified lon,lat location
ds_series = ds.sel(lon=-72.,lat=42.,method='nearest')


# In[23]:

# Select temperature and convert to Pandas Series
v_series = ds_series['ppt'].to_series()


# In[24]:

v_series.plot(title=v_series.name);


# In[25]:

ds_snapshot


# In[ ]:

#ds_snapshot.to_netcdf('ds_snapshot.nc')


# In[ ]:



