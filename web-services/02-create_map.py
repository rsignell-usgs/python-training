
# coding: utf-8

# <img style='float: left' width="150px" src="http://bostonlightswim.org/wp/wp-content/uploads/2011/08/BLS-front_4-color.jpg">
# <br><br>
# 
# ## [The Boston Light Swim](http://bostonlightswim.org/)
# 
# ### Sea Surface Temperature time-series maps

# ### Load configuration

# In[8]:

import os

try:
    import cPickle as pickle
except ImportError:
    import pickle

run_name = '2015-08-17'
fname = os.path.join(run_name, 'config.pkl')
with open(fname, 'rb') as f:
    config = pickle.load(f)


# ### Load skill_score

# In[9]:

try:
    import cPickle as pickle
except ImportError:
    import pickle

fname = os.path.join(run_name, 'skill_score.pkl')
with open(fname, 'rb') as f:
    skill_score = pickle.load(f)


# In[10]:

import numpy as np
from glob import glob
from pandas import Panel
from utilities import nc2df


def load_ncs(run_name):
    fname = '{}-{}.nc'.format
    ALL_OBS_DATA = nc2df(os.path.join(run_name,
                                      fname(run_name, 'OBS_DATA')))
    index = ALL_OBS_DATA.index
    dfs = dict(OBS_DATA=ALL_OBS_DATA)
    for fname in glob(os.path.join(run_name, "*.nc")):
        if 'OBS_DATA' in fname:
            continue
        else:
            model = fname.split('.')[0].split('-')[-1]
            df = nc2df(fname)
            # FIXME: Horrible work around duplicate times.
            if len(df.index.values) != len(np.unique(df.index.values)):
                kw = dict(subset='index', take_last=True)
                df = df.reset_index().drop_duplicates(**kw).set_index('index')
            kw = dict(method='time', limit=30)
            df = df.reindex(index).interpolate(**kw).ix[index]
            dfs.update({model: df})

    return Panel.fromDict(dfs).swapaxes(0, 2)


# In[11]:

from mpld3 import save_html
import matplotlib.pyplot as plt
from mpld3.plugins import LineLabelTooltip, connect

from utilities import make_map

bbox = config['bbox']
units = config['units']
run_name = config['run_name']

kw = dict(zoom_start=12, line=True, states=False, secoora_stations=False)
mapa = make_map(bbox, **kw)


# ### Clusters

# In[12]:

from glob import glob
from operator import itemgetter

import iris
from pandas import DataFrame, read_csv

fname = '{}-all_obs.csv'.format(run_name)
all_obs = read_csv(os.path.join(run_name, fname), index_col='name')

big_list = []
for fname in glob(os.path.join(run_name, "*.nc")):
    if 'OBS_DATA' in fname:
        continue
    cube = iris.load_cube(fname)
    model = fname.split('-')[-1].split('.')[0]
    lons = cube.coord(axis='X').points
    lats = cube.coord(axis='Y').points
    stations = cube.coord('station name').points
    models = [model]*lons.size
    lista = zip(models, lons.tolist(), lats.tolist(), stations.tolist())
    big_list.extend(lista)

big_list.sort(key=itemgetter(3))
df = DataFrame(big_list, columns=['name', 'lon', 'lat', 'station'])
df.set_index('station', drop=True, inplace=True)
groups = df.groupby(df.index)


for station, info in groups:
    sta_name = all_obs['station'][all_obs['station'].astype(str) == station].index[0]
    for lat, lon, name in zip(info.lat, info.lon, info.name):
        location = lat, lon
        popup = '<b>{}</b>\n{}'.format(sta_name, name)
        mapa.simple_marker(location=location, popup=popup,
                           clustered_marker=True)


# ### Model and observations plots

# In[13]:

mean_bias = skill_score['mean_bias'].applymap('{:.2f}'.format).replace('nan', '--')
skill = skill_score['rmse'].applymap('{:.2f}'.format).replace('nan', '--')

resolution, width, height = 75, 7, 3

def make_plot():
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_ylabel('Sea surface Temperature ({})'.format(units))
    ax.grid(True)
    return fig, ax


dfs = load_ncs(run_name)
dfs = dfs.swapaxes('items', 'major').resample('30min').swapaxes('items', 'major')

for station in dfs:
    sta_name = all_obs['station'][all_obs['station'].astype(str) == station].index[0]
    df = dfs[station].dropna(axis=1, how='all')
    if df.empty:
        continue
    labels = []
    fig, ax = make_plot()
    for col in df.columns:
        serie = df[col].dropna()
        lines = ax.plot(serie.index, serie, label=col,
                        linewidth=2.5, alpha=0.5)
        if 'OBS_DATA' not in col:
            text0 = col
            text1 = mean_bias[sta_name][col]
            text2 = skill[sta_name][col]
            tooltip = '{}:\nbias {}\nskill: {}'.format
            labels.append(tooltip(text0, text1, text2))
        else:
            labels.append('OBS_DATA')
    kw = dict(loc='upper center', bbox_to_anchor=(0.5, 1.05), numpoints=1,
              ncol=2, framealpha=0)
    l = ax.legend(**kw)
    l.set_title("")  # Workaround str(None).

    [connect(fig, LineLabelTooltip(line, name))
     for line, name in zip(ax.lines, labels)]

    html = 'station_{}.html'.format(station)
    save_html(fig, '{}/{}'.format(run_name, html))
    plt.close(fig)

    popup = "<div align='center'> {} <br><iframe src='{}' alt='image'"
    popup += "width='{}px' height='{}px' frameBorder='0'></div>"
    popup = popup.format('{}'.format(sta_name), html,
                         (width*resolution)+75, (height*resolution)+50)
    kw = dict(popup=popup, width=(width*resolution)+75)

    if (df.columns == 'OBS_DATA').all():
        kw.update(dict(marker_color="blue", marker_icon="ok"))
    else:
        kw.update(dict(marker_color="green", marker_icon="ok"))
    obs = all_obs[all_obs['station'].astype(str) == station].squeeze()
    mapa.simple_marker(location=[obs['lat'], obs['lon']], **kw)


# ### Map

# In[14]:

from utilities import inline_map


mapa.create_map(path=os.path.join(run_name, 'mapa.html'))
inline_map(os.path.join(run_name, 'mapa.html'))

