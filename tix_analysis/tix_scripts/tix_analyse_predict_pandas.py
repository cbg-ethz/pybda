import uuid
import pandas
import sklearn
from sklearn.ensemble import RandomForestRegressor


def load_data():
    filename = "/Users/simondi/PHD/data/data/target_infect_x/screening_data_subset/cells_sample_10_normalized_cut.tsv"

    data = pandas.read_csv(filename, sep="\t", header=0)

    feature_cols = [(i, x) for i, x in enumerate(data.columns.values) if
                    x.startswith("cells")]
    for i, c in feature_cols:
        data.loc[:, c] = data.loc[:, c].astype('float64')

    X = data.dropna(subset=["cells.children_invasomes_count",
                            "cells.children_bacteria_count"], how='all')
    X["cells.children_invasomes_count"] = X[
        "cells.children_invasomes_count"].fillna(0)
    X["cells.children_bacteria_count"] = X[
        "cells.children_bacteria_count"].fillna(0)
    X = X.dropna()
    X["infection"] = X["cells.children_invasomes_count"] + X[
        "cells.children_bacteria_count"]
    del X["cells.children_invasomes_count"]
    del X["cells.children_bacteria_count"]
    return X


data = load_data()

n = 100
rf = RandomForestRegressor(n_estimators=n, max_features='sqrt')

feature_cols = [x for x in data.columns.values if x.startswith("cells")]
trees = rf.fit(X=data.loc[:, feature_cols], y=data.loc[:, "infection"])

# In[10]:

zippedf = [(x, y) for x, y in zip(feature_cols, trees.feature_importances_)]

# In[26]:

zippedf = sorted(zippedf, key=lambda x: -x[1])

# In[15]:

uid = str(uuid.uuid1())
flout = "/Users/simondi/PROJECTS/target_infect_x_project/src/tix_util/tix_analysis/results/importance"

# In[24]:

flout = flout + "_trees_" + str(n) + "_" + uid + ".txt"

# In[27]:

with open(flout, 'w') as fh:
    for z in zippedf:
        fh.write(z[0] + "\t" + "{0:.2f}".format(z[1]) + "\n")


# In[ ]:




# In[ ]:
