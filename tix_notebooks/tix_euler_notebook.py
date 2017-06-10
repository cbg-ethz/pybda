#!/usr/bin/env python

import sys
import pandas

import matplotlib.pyplot
from matplotlib.backends.backend_pdf import PdfPages
from sklearn import manifold

import findspark
from sparkhpc import sparkjob

#spark_path = "/cluster/home/simondi/spark/"
#findspark.init(spark_path)

import pyspark
from pyspark.sql.window import Window
import pyspark.sql.functions as func
from pyspark.rdd import reduce
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import VectorAssembler, PCA
from pyspark.ml.clustering import KMeans
from pyspark.ml.linalg import SparseVector, VectorUDT, Vector, Vectors

# conf = pyspark.SparkConf().setAppName("app")
# sc = pyspark.SparkContext(conf=conf)

#sj = sparkjob.sparkjob(ncores=4)
#sj.wait_to_start()
#sc = sj.start_spark()
# spark = pyspark.sql.SparkSession(sc)
.builder \
    .appName("PythonPi") \
    .getOrCreate()


file_name = "/cluster/home/simondi/simondi/tix/data/screening_data/cells_sample_10.tsv"

df = spark.read.csv(path=file_name, sep="\t", header='true')
df.cache()
old_cols = df.schema.names
new_cols = list(map(lambda x: x.replace(".", "_"), old_cols))

df = reduce(
  lambda data, idx: data.withColumnRenamed(old_cols[idx], new_cols[idx]),
  range(len(new_cols)), df)
for i, x in enumerate(new_cols):
    if x.startswith("cells"):
        df = df.withColumn(x, df[x].cast("double"))


def z_score_w(col, w):
    avg = func.avg(col).over(w)
    sd = func.stddev(col).over(w)
    return (col - avg) / sd


w = Window() \
    .partitionBy(["study", "pathogen", "plate", "replicate"]) \
    .rowsBetween(-sys.maxsize, sys.maxsize)

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
