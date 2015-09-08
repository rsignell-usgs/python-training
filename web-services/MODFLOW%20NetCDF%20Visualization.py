
# coding: utf-8

# # Modflow2NetCDF
# 
# 

# In[1]:

# Freyberg config file
freyberg_config = '../../modflow2netcdf/tests/resources/freyberg/freyberg.geo'
with open(freyberg_config) as f:
    print f.read()


# In[2]:

# Freyberg NAM file
freyberg_nam = '../../modflow2netcdf/tests/resources/freyberg/freyberg.nam'
with open(freyberg_nam) as f:
    print f.read()


# In[3]:

# Load MODFLOW output files
from modflow2netcdf.output import ModflowOutput
mf = ModflowOutput(freyberg_nam, config_file=freyberg_config, exe_name="mf2005", verbose=False)


# In[4]:

# Save NetCDF output
freyberg_output = 'temp_freyberg_output.nc'
_ = mf.to_netcdf(output_file=freyberg_output)


# In[5]:

# Load NetCDF output
import netCDF4
nc = netCDF4.Dataset(freyberg_output)


# In[6]:

# List variables
for variable_name in nc.variables:
    print nc.variables.get(variable_name).name


# In[7]:

# Save some common variables
x = nc.variables.get("longitude")[:]
y = nc.variables.get("latitude")[:]


# In[8]:

# Plot the Elevation of Layer 0
import numpy as np
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')

from mpl_toolkits.mplot3d.axes3d import Axes3D
fig = plt.figure(figsize=(20,10))

z = nc.variables.get("elevation")[0, :, :]

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


# In[9]:

# Helper plot methods
mf.to_plot(variable='heads', level=0, time=0)


# In[10]:

mf.to_plot(variable='flow_right_face_centered', level=0, time=0, colormap=cm.GnBu)


# In[2]:

import netCDF4
# Access existing model output over OPeNDAP
dap = netCDF4.Dataset("http://thredds45.pvd.axiomalaska.com/thredds/dodsC/grabbag/modflow2netcdf/colorado.nc")
# List variables
for varname in dap.variables:
    print varname


# In[12]:

# Variable to plot
varname = 'heads'


# In[13]:

# Time index to plot
time = 0


# In[14]:

# Level index to plot
level = 2


# In[15]:

# Colormap to use
colormap = cm.Reds


# In[16]:

# Access data over DAP
x = dap.variables.get("longitude")[:]
y = dap.variables.get("latitude")[:]
z = dap.variables.get("elevation")[level, :]
data = dap.variables.get(varname)[time, level, :, :]


# In[17]:

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

