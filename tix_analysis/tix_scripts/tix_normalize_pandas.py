

import pandas
from functools import reduce
import numpy

file = "/Users/simondi/PHD/data/data/target_infect_x/screening_data_subset/cells_sample_10.tsv"
data = pandas.read_csv(file, sep="\t", header=0)

min_feature_idx = reduce(lambda x, y: x if x[0] < y[0] else y, [(i, x) for i, x in enumerate(data.columns.values) if x.startswith("cells")])
meta_colnames = data.columns[min_feature_idx[0]:]

feature_cols = [(i, x) for i, x in enumerate(data.columns.values) if x.startswith("cells")]

gr = data.groupby(['study', 'pathogen', 'library', 'design', 'replicate', 'plate'])

for name, group in gr:
    idxs = list(group.index)
    for i, c in feature_cols:
        data.loc[idxs, c] = (data.loc[idxs, c] - numpy.mean(data.loc[idxs, c])) / numpy.std(data.loc[idxs, c])

file_out = file.replace(".tsv", "") + "_normalized.tsv"
data.write_csv(file_out, header=True, sep="\t")
