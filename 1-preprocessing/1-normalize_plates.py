#!/usr/bin/env python


import re
import click
import logging
import pandas
import numpy
from statsmodels import robust
import findspark
from sparkhpc import sparkjob

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command()
@click.argument("file", type=str)
def run(file):
    """
    Do a normalization on plates from a tsv-FILE generated from `rnai-parse parse`
    """

    # findspark.init(spark)
    # import pyspark

    #    conf = pyspark.SparkConf().setAppName("normalize")
    #   sc = pyspark.SparkContext(conf=conf)
    #  spark = pyspark.sql.SparkSession(sc)
    spark = None
    normalize(spark, file)


def _normalize(lines, header):
    df = pandas.DataFrame(lines, columns=header)
    feature_columns = list(filter(
      lambda x: x.startswith("cells") or x.startswith(
        "perinucl") or x.startswith("nucle"),
      df.columns))
    df[feature_columns] = df[feature_columns].apply(pandas.to_numeric)

    # well_df = df.groupby(
    #   ['study', 'pathogen', 'library',
    #    'design', 'replicate', 'plate',
    #    'well'])[feature_columns].mean()

    # log norm
    #for feature_column in feature_columns:
    #    df[feature_column] = numpy.log(df[feature_column])
    # z-score
    for feature_column in feature_columns:
        df[feature_column] = (df[feature_column] -
                              numpy.nanmean(df[feature_column], )) / \
                             (numpy.nanstd(df[feature_column]) + 0.00000001)
    return df.values.tolist()


def _write(fw, arr, is_header):
    if is_header:
        fw.write("\t".join(arr) + "\n")
    else:
        for el in arr:
            fw.write("\t".join(map(lambda x: str(x), el)) + "\n")


def normalize(spark, file_name):
    # df = spark.read.csv(path=file_name, sep="\t", header='true')
    # df.groupby({})
    out_reg = re.match("(.+)\.(\w+)", file_name)
    outfile = out_reg.group(1) + "_normalize." + out_reg.group(2)
    lines, prefix = [None] * 100000, None
    header = []
    run = 0
    with open(file_name, "r") as fr, open(outfile, "w") as fw:
        for line in fr.readlines():
            st = line.rstrip().split("\t")
            if line.startswith("study"):
                header = st
                _write(fw, st, True)
            elif lines[0] is None or not line.startswith(prefix):
                if lines[0] is not None and not line.startswith(prefix):
                    dat = _normalize(lines[:run], header)
                    _write(fw, dat, False)
                    lines, prefix, run = [None] * 100000, None, 0
                lines[run] = st
                run += 1
                prefix = "\t".join(st[:6])
            elif line.startswith(prefix):
                if run < len(lines):
                    lines[run] = st
                    run += 1
                else:
                    lines.append(st)
        dat = _normalize(lines[:run], header)
        _write(fw, dat, False)


if __name__ == '__main__':
    run()
