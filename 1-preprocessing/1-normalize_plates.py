#!/usr/bin/env python


import os
import click
import logging
import findspark
from sparkhpc import sparkjob

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command()
@click.argument("file",
                type=str,
                help="A tsv-file generated from `rnai-parse parse`")
@click.argument("spark",
                type=str,
                help="Folder where you Spark installation lies.")
def run(file, spark):
    """
    Do a normalization on plates.
    """

    findspark.init(spark)
    import pyspark

    conf = pyspark.SparkConf().setAppName("normalize")
    sc = pyspark.SparkContext(conf=conf)
    spark = pyspark.sql.SparkSession(sc)
    normalize(spark, file)


def normalize(spark, file_name):
    df = spark.read.csv(path=file_name, sep="\t", header='true')
    df.groupby("")

if __name__ == '__main__':
    run()
