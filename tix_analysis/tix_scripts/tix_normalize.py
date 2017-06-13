#!/usr/bin/env python

import sys
import pandas
import os
import numpy

if os.path.isdir("/cluster/home/simondi/spark/"):
    is_cluster = True
else:
    is_cluster = False

if is_cluster:
    file_name = "/cluster/home/simondi/simondi/tix/data/screening_data/cells_sample_10.tsv"
else:
    file_name = "/Users/simondi/PHD/data/data/target_infect_x/screening_data_subset/cells_sample_10.tsv"


df = pandas.read_csv(file_name, sep="\t", header=0)

old_cols = df.columns
new_cols = list(map(lambda x: x.replace(".", "_"), old_cols))
df.columns = new_cols

def z_score_w(col, w):
    avg = func.avg(col).over(w)
    sd = func.stddev(col).over(w)
    return (col - avg) / sd


for x in df.columns:
    if x.startswith("cells"):
        df = df.withColumn(x, z_score_w(df[x], w))

df = df.na.fill(value=0)

X = df.sample(fraction=.01, withReplacement=False)

assembler = VectorAssembler(
  inputCols=[x for x in X.columns if x.startswith("cells")],
  outputCol='features')
X = assembler.transform(X)
X.cache()

kmeans = KMeans(k=5, seed=23)
model = kmeans.fit(X)

X = X.toPandas()

X_index = [i for i, x in enumerate(X.columns) if x.startswith("cells")]

tsne = manifold.TSNE(n_components=2, init='pca', random_state=23)
trans_data = tsne.fit_transform(X.values[:, X_index])

transe = pandas.DataFrame(trans_data)
transe["pathogen"] = X["pathogen"]
transe["design"] = X["design"]
transe["cluster"] = model.summary.cluster.toPandas()["prediction"]
transe.columns = ['a', 'b', 'pathogen', 'design', "kmeans"]


def plot(dat, grp):
    fig, ax = matplotlib.pyplot.subplots()
    matplotlib.pyplot.rc(
      'axes', prop_cycle=(matplotlib.pyplot.cycler('color',
                                                   ['r', 'g', 'b',
                                                    'y', 'm'])))
    ax.margins(0.05)
    groups = dat.groupby(grp)
    for name, group in groups:
        ax.plot(group.a, group.b, marker='o', linestyle='', ms=3, label=name)
    ax.legend()
    pp = PdfPages("plots/clustering_by_" + grp + ".pdf")
    matplotlib.pyplot.savefig(pp, format='pdf')
    pp.close()


plot(transe, "pathogen")
plot(transe, "kmeans")

sc.stop()
