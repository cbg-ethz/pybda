#!/usr/bin/env python

import os
import sys
import pandas
import numpy
import findspark

import pyspark
from pyspark.sql.window import Window
import pyspark.sql.functions as func

from pyspark.rdd import reduce
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import VectorAssembler, PCA
from pyspark.ml.clustering import KMeans
from pyspark.ml.linalg import SparseVector, VectorUDT, Vector, Vectors


conf = pyspark.SparkConf()
file_name = "/cluster/home/simondi/simondi/tix/data/screening_data/cells_sample_1000.tsv"

sc = pyspark.SparkContext(conf=conf)
spark = pyspark.sql.SparkSession(sc)

#file_name = "/cluster/home/simondi/simondi/tix/data/screening_data/cells_sample_10_100_lines.tsv"

#spark = pyspark.sql.SparkSession.builder.appName("test").getOrCreate()

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


w = Window().partitionBy(["study", "pathogen"]).rowsBetween(-sys.maxsize,
                                                            sys.maxsize)
for x in df.columns:
    if x.startswith("cells"):
        df = df.withColumn(x, z_score_w(df[x], w))

#df.write.csv(file_name.replace(".tsv", "") + "_normalized_tsv",
#             sep="\t", header=True, mode="overwrite")

df.write.parquet(file_name.replace(".tsv", "") + "_normalized_parquet", mode="overwrite")
#df.toPandas().to_csv(file_name.replace(".tsv", "") + "_normalized.tsv", sep="\t", header=True, index=False)

#sc.stop()
spark.stop()
