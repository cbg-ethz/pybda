import argparse
import logging
import sys
import pandas
import pathlib
import pyspark

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(
      description='Compute statistics of a clustered PCA-dataset.')
    parser.add_argument('-f',
                        type=str,
                        help='the folder where the pca data lie,'
                             ' i.e. transform-*_K005',
                        required=True, metavar="input-folder")

    opts = parser.parse_args(args)
    return opts.f, opts


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    logger.info("Writing parquet: {}".format(file_name))
    data.write.parquet(file_name, mode="overwrite")


def write_pandas_tsv(file_name, data):
    data.to_csv(file_name, sep="\t", index=False)


def count_statistics(data, folder, what):
    dnts = data.groupby(what).count()
    dnts = dnts.select(what + ["count"]).dropDuplicates().toPandas()

    outfile = folder + "_" + "_".join(what) + "_count.tsv"
    logger.info("Writing sample table to: {}".format(outfile))
    write_pandas_tsv(outfile, dnts)


def statistics(folder):
    if not pathlib.Path(folder).is_dir():
        logger.error("Directory doesnt exist: {}".format(folder))
        return

    logger.info("Loading PCA/Kmeans clustering")
    data = read_parquet_data(folder)

    count_statistics(data, folder, ["gene", "prediction"])
    count_statistics(data, folder, ["sirna", "prediction"])
    count_statistics(data, folder, ["pathogen", "prediction"])

    for i in range(5):
        pred = "prediction={}".format(i)
        data_i = data.filter(pred)
        data_i.toPandas().to_csv(
          "{}_{}.tsv".format(folder, i), sep="\t", index=0)


def run():
    # check files
    folder, opts = read_args(sys.argv[1:])
    if not pathlib.Path(folder).is_dir():
        logger.error("Folder does not exist: " + folder)
        return

    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)
    try:
        statistics(folder)
    except Exception as e:
        logger.error("Random exception: {}".format(str(e)))
    spark.stop()


if __name__ == "__main__":
    run()
