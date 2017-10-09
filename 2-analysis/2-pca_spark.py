import argparse
import logging
import pathlib
import re
import sys
import pandas
import pyspark

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pyspark.ml.feature import PCA
from pyspark.ml.linalg import Vector, Vectors
from pyspark.sql.window import Window
from pyspark.ml.feature import StandardScaler
from pyspark.sql.functions import row_number

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(description='PCA on a clustered dataset.')
    parser.add_argument('-f',
                        type=str,
                        help='the folder where the clustered/transformed data lie,'
                             ' i.e. kmeans_transform-*_K005',
                        required=True,
                        metavar="input-folder")

    opts = parser.parse_args(args)

    return opts.f, opts


def pca_transform_path(folder):
    return folder.replace("kmeans_transform-", "pca_transform-")


def pca_transform_tsv_path(folder):
    return pca_transform_path(folder) + "_sample.tsv"


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    logger.info("Writing parquet: {}".format(file_name))
    data.write.parquet(file_name, mode="overwrite")


def write_pandas_tsv(file_name, data):
    data.to_csv(file_name, sep="\t", index=False)


def transform_pca(folder):
    if not pathlib.Path(folder).is_dir():
        logger.error("Directory doesnt exist: {}".format(folder))
        return

    logger.info("Loading/clustering Kmeans clustering")
    data = read_parquet_data(folder)

    scaler = StandardScaler(inputCol="features",
                            outputCol="scaledFeatures",
                            withStd=True,
                            withMean=True)
    scalerModel = scaler.fit(data)
    data = scalerModel.transform(data)

    pca = PCA(k=2, inputCol="scaledFeatures", outputCol="pcs")

    model = pca.fit(data)
    data = model.transform(data)
    opath = pca_transform_path(folder)
    write_parquet_data(opath, data)

    data = data.withColumn(
      "row_num",
      row_number().over(Window.partitionBy(["pathogen", "gene"])
                        .orderBy(["pathogen", "gene"])))

    data = data.filter("row_num <= 10")
    datap = data.select(
      ["pathogen", "gene", "sirna", "prediction", "pcs"]).toPandas()
    datap[['pc1', 'pc2']] = pandas.DataFrame(datap.pcs.values.tolist())
    del datap['pcs']
    opandname = pca_transform_tsv_path(folder)
    write_pandas_tsv(opandname, datap)


def loggername(outpath):
    name = pca_transform_path(outpath)
    return name + ".log"


def run():
    # check files
    folder, opts = read_args(sys.argv[1:])
    if not pathlib.Path(folder).is_dir():
        logger.error("Folder does not exist: " + folder)
        return

    hdlr = logging.FileHandler(loggername(folder))
    hdlr.setFormatter(frmtr)
    logger.addHandler(hdlr)

    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)
    try:
      transform_pca(folder)
    except Exception as e:
        logger.error("Random exception: {}".format(str(e)))
    spark.stop()


if __name__ == "__main__":
    run()
