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
    logger.info("Subsampling data")
    if not outpath.endswith(".tsv"):
        outpath += ".tsv"

    data_row_cnt = data.count()
    sample_ratio = float(min(100000 / data_row_cnt, 1))
    data = data\
        .sample(withReplacement=False, fraction=sample_ratio, seed=23)\
        .select("features").toPandas()

    logger.info("Writing tsv: {}".format(outpath))
    data.to_csv(outpath, sep="\t", index=False, header=False)
    subprocess.run(['sed', '-i', ".bak", 's/\[//g', outpath])
    subprocess.run(['sed', '-i', ".bak", 's/\]//g', outpath])
    subprocess.run(['sed', '-i', ".bak", "s/\,/\t/g", outpath])
    subprocess.run(['rm', outpath + '.bak'])


def run():
    # check files
    file_name, outpath, opts = read_args(sys.argv[1:])

    if outpath.endswith("/"):
        outpath = outpath[:-1]
    elif outpath.endswith(".tsv"):
        outpath = outpath.replace(".tsv", "")
    hdlr = logging.FileHandler(outpath + ".log")
    hdlr.setFormatter(frmtr)
    logger.addHandler(hdlr)

    logger.info("Starting Spark context")

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

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
