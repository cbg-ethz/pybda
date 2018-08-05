import argparse
import logging
import sys
import pandas
import pathlib
import pyspark
import numpy
import re
import glob

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(
      description="Write the clusters for easier downstream analysis.")
    parser.add_argument('-f',
                        type=str,
                        help="the folder where the clustered files lie,"
                             " i.e. 'kmeans-transformed-recursive-clusters'",
                        required=True, metavar="input-folder")

    opts = parser.parse_args(args)
    return opts.f, opts



def write_clustered(outfolder):
    files = (x for x in glob.glob(fl + "*") if x.endswith(".csv"))
    for fl in files:
        df = pandas.read_csv(fl, sep="\t")
        for i in df["prediction"].unique():
            sub  = df[df.prediction == i]
            out = outfolder + "/cluster_" + str(i) + ".tsv"
            if not pathlib.Path(out).exists():
                logging.logger("Logging to {}".format(out))
                sub.to_csv(out, sep="\t", header=True, index=False)
            else:
                logging.logger("Re-logging to {}".format(out))
                sub.to_csv(out, sep="\t", mode="a", header=False, index=False)


def run():
    # check files
    folder, opts = read_args(sys.argv[1:])
    if not pathlib.Path(folder).is_dir():
        logger.error("Folder does not exist: " + folder)
        return

        # logging format
    hdlr = logging.FileHandler(folder + "-write-clusters-statistics.log")
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
        write_clustered(folder)
    except Exception as e:
        logger.error("Random exception: {}".format(str(e)))

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
