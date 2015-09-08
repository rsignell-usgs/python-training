
# coding: utf-8

# # Modflow2NetCDF
# 
# 

# Example converting Modflow output files to NetCDF, then reading and visualizing data from the NetCDF file created.  The resulting files maybe placed on a THREDDS server where they become available via services such as OPeNDAP and WCS. This is demonstrated by accessing data from Modflow NetCDF files from a remote THREDDS server. 

# In[1]:

# Freyberg config file - a nice small test case
import os
freyberg_config = os.path.join('resources','freyberg','freyberg.geo')

with open(freyberg_config) as f:
    print f.read()


# In[2]:

# Freyberg NAM file

freyberg_nam = os.path.join('resources','freyberg','freyberg.nam')
with open(freyberg_nam) as f:
    print f.read()


# In[3]:

#define the workspace
freyberg_ws = os.path.join('resources','freyberg')


# In[4]:

# Load MODFLOW output files
from modflow2netcdf.output import ModflowOutput
mf = ModflowOutput('freyberg.nam', config_file=freyberg_config, exe_name="mf2005", model_ws=freyberg_ws, verbose=True)


# In[5]:

# Save NetCDF output
freyberg_output = 'temp_freyberg_output.nc'
_ = mf.to_netcdf(output_file=freyberg_output)


# In[8]:

# Let's check out the NetCDF file we created
import numpy as np
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')

from mpl_toolkits.mplot3d.axes3d import Axes3D


# In[9]:

# Load NetCDF output
import netCDF4
nc = netCDF4.Dataset(freyberg_output)


# In[10]:

nc


# In[11]:

ncv = nc.variables


# In[13]:

ncv.keys()


# In[23]:

ncv['recharge'].coordinates


# In[14]:

# List variables
for variable_name in ncv:
    print ncv[variable_name].name


# In[19]:

# Get lon/lat variables
x = ncv['longitude'][:,:]
y = ncv['latitude'][:,:]


# In[20]:

x.shape


# In[28]:

# get the elevation at level 0
z = ncv['elevation'][0, :, :]


# In[29]:

z.shape


# In[30]:


fig = plt.figure(figsize=(20,10))

ax = fig.add_subplot(2, 2, 1, projection='3d')
p = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0, cmap=cm.Spectral, alpha=0.80)
cb = fig.colorbar(p, shrink=0.7)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Elevation')
ax.view_init(40, 30)

ax = fig.add_subplot(2, 2, 2, projection='3d')
p = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0, cmap=cm.Spectral, alpha=0.80)
cb = fig.colorbar(p, shrink=0.7)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Elevation')
ax.view_init(40, 120)

ax = fig.add_subplot(2, 2, 3, projection='3d')
p = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0, cmap=cm.Spectral, alpha=0.80)
cb = fig.colorbar(p, shrink=0.7)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Elevation')
ax.view_init(40, 210)

ax = fig.add_subplot(2, 2, 4, projection='3d')
p = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0, cmap=cm.Spectral, alpha=0.80)
cb = fig.colorbar(p, shrink=0.7)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Elevation')
ax.view_init(40, 300)


# In[ ]:

# Helper plot methods
#mf.to_plot(variable='heads', level=0, time=0)


# In[ ]:

#mf.to_plot(variable='flow_right_face_centered', level=0, time=0, colormap=cm.GnBu)


# ## Accessing data via OPeNDAP

# Sample Modflow netcdf files on THREDDS:
#     http://thredds45.pvd.axiomalaska.com/thredds/catalog/grabbag/modflow2netcdf/catalog.html

# In[32]:

url='http://thredds45.pvd.axiomalaska.com/thredds/dodsC/grabbag/modflow2netcdf/miami-dade.nc'


# In[34]:

nc2 = netCDF4.Dataset(url)


# In[39]:

nc2v=nc2.variables
lon=nc2v['longitude'][0:10][0]
lon


# In[31]:

from IPython.core.display import HTML
HTML('<iframe src=http://thredds45.pvd.axiomalaska.com/thredds/catalog/grabbag/modflow2netcdf/catalog.html width=800 height=400></iframe>')


# In[ ]:

import netCDF4
import numpy as np
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d.axes3d import Axes3D
get_ipython().magic(u'matplotlib inline')
#matplotlib nbagg
# Access existing model output over OPeNDAP
dap = netCDF4.Dataset("http://thredds45.pvd.axiomalaska.com/thredds/dodsC/grabbag/modflow2netcdf/colorado.nc")
#dap = netCDF4.Dataset("http://thredds45.pvd.axiomalaska.com/thredds/dodsC/grabbag/modflow2netcdf/miami-dade.nc")
# List variables
for varname in dap.variables:
    print varname


# In[ ]:

# Variable to plot
varname = 'heads'


# In[ ]:

# Time index to plot
time = 0


# In[ ]:

# Level index to plot
level = 2


# In[ ]:

# Colormap to use
colormap = cm.Reds


# In[ ]:

# Access data over DAP (syntax1)
x = dap.variables.get("longitude")[:]
y = dap.variables.get("latitude")[:]
z = dap.variables.get("elevation")[level, :]
data = dap.variables.get(varname)[time, level, :, :]


# In[ ]:

# Access data over DAP (syntax2)
dapv = dap.variables
x = dapv['longitude'][:]
y = dapv['latitude'][:]
z = dapv['elevation'][level, :]
data = dapv[varname][time, level, :, :]


# In[ ]:

plt.pcolormesh(x,y,data);


# In[ ]:

# Plot the HEADS
fig = plt.figure(figsize=(20, 10))
m = cm.ScalarMappable(cmap=colormap)
m.set_array(data)
colors = m.to_rgba(data)[:, :, 0]

ax = fig.add_subplot(2, 2, 1, projection='3d')
p = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0, alpha=0.80, facecolors=colormap(colors))
fig.colorbar(m, shrink=0.7)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Time: {0} Level: {1} Variable: {2}'.format(level, time, varname))
ax.view_init(60, 30)

ax = fig.add_subplot(2, 2, 2, projection='3d')
p = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0, alpha=0.80, facecolors=colormap(colors))
fig.colorbar(m, shrink=0.7)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Time: {0} Level: {1} Variable: {2}'.format(level, time, varname))
ax.view_init(60, 120)

ax = fig.add_subplot(2, 2, 3, projection='3d')
p = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0, alpha=0.80, facecolors=colormap(colors))
fig.colorbar(m, shrink=0.7)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Time: {0} Level: {1} Variable: {2}'.format(level, time, varname))
ax.view_init(60, 210)

ax = fig.add_subplot(2, 2, 4, projection='3d')
p = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0, alpha=0.80, facecolors=colormap(colors))
fig.colorbar(m, shrink=0.7)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Time: {0} Level: {1} Variable: {2}'.format(level, time, varname))
ax.view_init(60, 300)


# In[ ]:



