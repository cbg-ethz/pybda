import argparse
import logging
import subprocess
import sys
import pandas
import numpy
import pyspark
from pyspark.ml.linalg import Vectors

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(
      description='Convert a pqrquet folder to a tsv')
    parser.add_argument('-o',
                        type=str,
                        help='outfile',
                        required=True,
                        metavar="output-folder")
    parser.add_argument('-f',
                        type=str,
                        help='input folder that storres parquet files',
                        required=True,
                        metavar="input-folder")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_tsv_data(outpath, data):
    logger.info("Writing tsv: {}".format(outpath))
    if not outpath.endswith(".tsv"):
        outpath += ".tsv"
    data = data.select("features").toPandas()
    data.to_csv(outpath, sep="\t", index=False, header=False)
    subprocess.run(['sed', '-i', "''", 's/\[//g', outpath])
    subprocess.run(['sed', '-i', "''", 's/\]//g', outpath])
    subprocess.run(['sed', '-i', "''", "s/\,/\t/g", outpath])


def run():
    # check files
    file_name, outpath, opts = read_args(sys.argv[1:])
    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)

    try:
        write_tsv_data(outpath, read_parquet_data(file_name))
    except Exception as e:
        logger.error("Some error: {}".format(str(e)))

    spark.stop()


if __name__ == "__main__":
    run()
