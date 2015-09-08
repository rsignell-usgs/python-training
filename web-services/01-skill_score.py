
# coding: utf-8

# <img style='float: left' width="150px" src="http://bostonlightswim.org/wp/wp-content/uploads/2011/08/BLS-front_4-color.jpg">
# <br><br>
# 
# ## [The Boston Light Swim](http://bostonlightswim.org/)
# 
# ### Sea Surface Temperature time-series model skill

# ### Load configuration

# In[1]:

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle


run_name = '2015-08-17'
fname = os.path.join(run_name, 'config.pkl')
with open(fname, 'rb') as f:
    config = pickle.load(f)


# In[2]:

import numpy as np
from pandas import DataFrame, read_csv
from utilities import to_html, save_html, apply_skill


fname = '{}-all_obs.csv'.format(run_name)
all_obs = read_csv(os.path.join(run_name, fname), index_col='name')


def rename_cols(df):
    columns = dict()
    for station in df.columns:
        mask = all_obs['station'].astype(str) == station
        name = all_obs['station'][mask].index[0]
        columns.update({station: name})
    return df.rename(columns=columns)


# In[3]:

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


# ### Skill 1: Model Bias (or Mean Bias)
# 
# The bias skill compares the model mean temperature against the observations.
# It is possible to introduce a Mean Bias in the model due to a mismatch of the
# boundary forcing and the model interior.
# 
# $$ \text{MB} = \mathbf{\overline{m}} - \mathbf{\overline{o}}$$

# In[4]:

from utilities import mean_bias

dfs = load_ncs(run_name)

df = apply_skill(dfs, mean_bias, remove_mean=False, filter_tides=False)
df = rename_cols(df)
skill_score = dict(mean_bias=df.copy())

# Filter out stations with no valid comparison.
df.dropna(how='all', axis=1, inplace=True)
df = df.applymap('{:.2f}'.format).replace('nan', '--')

html = to_html(df.T)
fname = os.path.join(run_name, 'mean_bias.html'.format(run_name))
save_html(fname, html)
html


# ### Skill 2: Central Root Mean Squared Error
# 
# Root Mean Squared Error of the deviations from the mean.
# 
# $$ \text{CRMS} = \sqrt{\left(\mathbf{m'} - \mathbf{o'}\right)^2}$$
# 
# where: $\mathbf{m'} = \mathbf{m} - \mathbf{\overline{m}}$ and $\mathbf{o'} = \mathbf{o} - \mathbf{\overline{o}}$

# In[5]:

from utilities import rmse

dfs = load_ncs(run_name)

df = apply_skill(dfs, rmse, remove_mean=True, filter_tides=False)
df = rename_cols(df)
skill_score['rmse'] = df.copy()

# Filter out stations with no valid comparison.
df.dropna(how='all', axis=1, inplace=True)
df = df.applymap('{:.2f}'.format).replace('nan', '--')

html = to_html(df.T)
fname = os.path.join(run_name, 'rmse.html'.format(run_name))
save_html(fname, html)
html


# ### Skill 3: R$^2$
# https://en.wikipedia.org/wiki/Coefficient_of_determination

# In[6]:

from utilities import r2

dfs = load_ncs(run_name)

df = apply_skill(dfs, r2, remove_mean=True, filter_tides=False)
df = rename_cols(df)
skill_score['r2'] = df.copy()

# Filter out stations with no valid comparison.
df.dropna(how='all', axis=1, inplace=True)
df = df.applymap('{:.2f}'.format).replace('nan', '--')

html = to_html(df.T)
fname = os.path.join(run_name, 'r2.html'.format(run_name))
save_html(fname, html)
html


# In[7]:

fname = os.path.join(run_name, 'skill_score.pkl')
with open(fname,'wb') as f:
    pickle.dump(skill_score, f)


# ### Normalized Taylor diagrams
# 
# The radius is model standard deviation error divided  by observations deviation,
# azimuth is arc-cosine of cross correlation (R), and distance to point (1, 0) on the
# abscissa is Centered RMS.

# In[8]:

get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
from utilities.taylor_diagram import TaylorDiagram


def make_taylor(samples):
    fig = plt.figure(figsize=(9, 9))
    dia = TaylorDiagram(samples['std']['OBS_DATA'],
                        fig=fig,
                        label="Observation")
    colors = plt.matplotlib.cm.jet(np.linspace(0, 1, len(samples)))
    # Add samples to Taylor diagram.
    samples.drop('OBS_DATA', inplace=True)
    for model, row in samples.iterrows():
        dia.add_sample(row['std'], row['corr'], marker='s', ls='',
                       label=model)
    # Add RMS contours, and label them.
    contours = dia.add_contours(colors='0.5')
    plt.clabel(contours, inline=1, fontsize=10)
    # Add a figure legend.
    kw = dict(prop=dict(size='small'), loc='upper right')
    leg = fig.legend(dia.samplePoints,
                     [p.get_label() for p in dia.samplePoints],
                     numpoints=1, **kw)
    return fig


# In[9]:

dfs = load_ncs(run_name)

# Bin and interpolate all series to 1 hour.
freq = '30min'
for station, df in list(dfs.iteritems()):
    df = df.resample(freq).interpolate().dropna(axis=1)
    if 'OBS_DATA' in df:
        samples = DataFrame.from_dict(dict(std=df.std(),
                                           corr=df.corr()['OBS_DATA']))
    else:
        continue
    samples[samples < 0] = np.NaN
    samples.dropna(inplace=True)
    if len(samples) <= 2:  # 1 obs 1 model.
        continue
    fig = make_taylor(samples)
    fig.savefig(os.path.join(run_name, '{}.png'.format(station)))
    plt.close(fig)

