# Copyright (C) 2018 Simon Dirmeier
#
# This file is part of koios.
#
# koios is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# koios is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with koios. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import logging

import click
import pyspark
from koios.util.features import split_features


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def sample(data, n):
    data_row_cnt = data.count()
    sample_ratio = float(min(n / data_row_cnt, 1))

    return data.sample(withReplacement=False, fraction=sample_ratio, seed=23)


@click.command()
@click.argument("input", type=str)
@click.argument("output", type=str)
@click.argument("n", type=int)
@click.option("--split", type=bool )
def run(input, output, n, split):

    if output.endswith("/"):
        output = output[:-1]
    if output.endswith(".tsv"):
        logfile = output.replace(".tsv", ".log")
    else:
        logfile = output + ".log"

    hdlr = logging.FileHandler(logfile)
    hdlr.setFormatter(
      logging.Formatter(
        '[%(asctime)s - %(levelname)s - %(name)s]: %(message)s')
    )
    root_logger = logging.getLogger()
    root_logger.addHandler(hdlr)

    logger.info("Initializing pyspark session")
    pyspark.StorageLevel(True, True, False, False, 1)
    spark = pyspark.sql.SparkSession.builder.getOrCreate()
    for conf in spark.sparkContext.getConf().getAll():
        logger.info("Config: {}, value: {}".format(conf[0], conf[1]))

    import pathlib
    from koios.io.io import read_tsv, read_parquet, write_parquet, write_tsv
    if input.endswith(".tsv") and pathlib.Path(input).is_file():
        logger.info("Found suffix 'tsv', expecting tsv file as input")
        reader = read_tsv
    elif pathlib.Path(input).is_folder():
        logger.info("Found folder, expecting parquet file as input")
        reader = read_parquet,
    if output.endswith(".tsv"):
        logger.info("Found suffix 'tsv', writing tsv file as output")
        writer = write_tsv
    else:
        logger.info("Writing parquet as output")
        writer = write_parquet

    subsamp = sample(spark, reader(spark, input), n)
    if output.endswith(".tsv") and split:
        subsamp = split_features(subsamp)
    writer(subsamp, output)

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
