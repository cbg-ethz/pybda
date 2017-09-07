import pandas
import sklearn
from sklearn import preprocessing


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

meta_cols_idxs = ["pathogen", "library", "design", "gene"]
for c in meta_cols_idxs:
    label_enc = preprocessing.LabelEncoder()
    int_labels = label_enc.fit_transform(data[c])

    enc = preprocessing.OneHotEncoder()
    dummy = enc.fit_transform(int_labels.reshape(-1, 1)).toarray()

    del data[c]
    for idx in range(dummy.shape[1]):
        data[c + "_" + str(idx)] = dummy[:, idx]

dummy_filename = "/Users/simondi/PHD/data/data/target_infect_x/screening_data_subset/cells_sample_10_normalized_cut_dummied.tsv"

data.to_csv(dummy_filename, header=True, sep="\t", index=False)
