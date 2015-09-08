
# coding: utf-8

# #Query `apiso:ServiceType` on geoport pycsw 

# In[11]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np


# In[12]:

endpoint = 'http://geoport.whoi.edu/csw'   # NODC/UAF Geoportal: granule level
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[13]:

csw.get_operation_by_name('GetRecords').constraints


# In[15]:

#val = 'CMG_Portal'
val = 'modflow'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[16]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 
    


# In[17]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# Add bounding box constraint. To specify lon,lat order for bbox (which we want to do so that we can use the same bbox with either geoportal server or pycsw requests), we need to request the bounding box specifying the CRS84 coordinate reference system.   The CRS84 option is available in `pycsw 1.1.10`+. The ability to specify the `crs` in the bounding box request is available in `owslib 0.8.12`+.  For more info on the bounding box problem and how it was solved, see this [pycsw issue](https://github.com/geopython/pycsw/issues/287), this [geoportal server issue](https://github.com/Esri/geoportal-server/issues/124), and this [owslib issue](https://github.com/geopython/OWSLib/issues/201)

# In[ ]:

bbox = [-87.40, 34.25, -63.70, 66.70]    # [lon_min, lat_min, lon_max, lat_max]
bbox_filter = fes.BBox(bbox,crs='urn:ogc:def:crs:OGC:1.3:CRS84')
filter_list = [fes.And([filter1, bbox_filter])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)


# In[ ]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# In[ ]:

val = 'opendap'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2, bbox_filter])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)


# In[ ]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# In[ ]:



