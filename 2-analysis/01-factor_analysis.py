
import pandas
import sklearn
import numpy
from sklearn.decomposition import FactorAnalysis

file_name = "/Users/simondi/PHD/data/data/target_infect_x/query_data/cells_sample_10_normalized_cut_100.tsv"

data = pandas.read_csv(file_name, sep="\t")
feat = [x for x in data.columns if x.startswith("cells") and not x.startswith("cells.children_invasomes_count")]
data = data[feat]
X = data.as_matrix().astype(numpy.float64)
print(data.columns)
fa = FactorAnalysis(2, svd_method="lapack", max_iter=5)
fit = fa.fit(X)
Xtran = fit.transform(X)
k = 2