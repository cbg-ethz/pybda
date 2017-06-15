
# coding: utf-8

# In[2]:

import pandas
import sklearn
import numpy

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

import matplotlib


# In[3]:

filename = "/Users/simondi/PHD/data/data/target_infect_x/screening_data_subset/cells_sample_10_normalized.tsv"


# In[4]:

data = pandas.read_csv(filename, sep="\t", header=0)


# In[5]:

feature_cols = [(i, x) for i, x in enumerate(data.columns.values) if x.startswith("cells")]
for i, c in feature_cols:
    data.loc[:, c] = data.loc[:, c].astype('float64')


# In[6]:

grops = ['pathogen', 'library', 'design', 'replicate', 'gene']


# In[7]:

grop_cnt = data.query("design=='p' and library=='d' and replicate==1 and study=='infectx'").groupby("gene").size()


# In[8]:

#data.query("design=='p' and library=='d' and replicate==1 and study=='infectx'").groupby("gene").filter(lambda x: len(x) >= 40).groupby("gene").size()


# In[9]:

data_new = data.query("library=='d' and design=='p' and replicate==1 and (pathogen=='brucella' or pathogen=='listeria' or pathogen=='adeno' or pathogen=='bartonella')").groupby(["gene"]).filter(lambda x: len(x) == 40)


# In[10]:

data_new.loc[numpy.isnan(data_new["cells.children_invasomes_count"])].groupby("pathogen").size()


# In[11]:

data_new.loc[numpy.isfinite(data_new["cells.children_invasomes_count"])].groupby("pathogen").size()


# In[12]:

del data_new["cells.children_invasomes_count"]
del data_new["cells.children_bacteria_count"]


# In[13]:

feature_cols_idxs = [ x for x in data_new.columns.values if x.startswith("cells")]
feature_cols_idxs
X = data_new.dropna()
#data_new[numpy.isfinite(data_new.loc[:, feature_cols_idxs]) | numpy.isnan(data_new[:, feature_cols_idxs])]


# In[17]:

X[1:5]


# In[14]:

pca = PCA(n_components=2)
tsne = TSNE(n_components=2)


# In[230]:

#X.dropna(axis=0, how='any')


# In[15]:

X_ = pca.fit_transform(X.loc[:, feature_cols_idxs])


# In[ ]:

X_ = tsne.fit_transform(X.loc[:, feature_cols_idxs])


# In[20]:

uniq = list(set(X['pathogen']))


# In[28]:

import matplotlib.pyplot as plt

import matplotlib.colors as colors
import matplotlib.cm as cmx


hot = plt.get_cmap('hot')
cNorm  = colors.Normalize(vmin=0, vmax=len(uniq))
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=hot)

for i in range(len(uniq)):
    indx = X['pathogen'] == uniq[i]
    plt.scatter(X_[indx,1], X_[indx,0], color=scalarMap.to_rgba(i), label=uniq[i], marker=".")

plt.show()


# In[ ]:




# In[ ]:




# In[ ]:



