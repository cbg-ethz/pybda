

import argparse
import logging
import pathlib
import sys
import numpy
import scipy
import pyspark
import pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(description='Convert a pqrquet folder to a tsv')
    parser.add_argument('-o',
                        type=str,
                        help='output folder',
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
    logger.info("Writing tsvt: {}".format(outpath))
    data.write.csv(path=outpath, sep="\t", header=True)


def run():
    # check files
    file_name, outpath, opts = read_args(sys.argv[1:])
    if not file_name.endswith(".tsv"):
        logger.error("Please provide a tsv file: " + file_name)
        return

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
