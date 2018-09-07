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

from koios.logger import set_logger
from koios.spark_session import SparkSession
from koios.util.features import split_vector

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
@click.argument("split", type=bool)
def run(input, output, n, split):

    from koios.util.string import drop_suffix
    from koios.io.io import as_logfile
    import pathlib
    from koios.io.io import read_tsv, read_parquet, write_parquet, write_tsv

    output = drop_suffix(output, "/")
    set_logger(as_logfile(output))

    if input.endswith(".tsv") and pathlib.Path(input).is_file():
        logger.info("Found suffix 'tsv', expecting tsv file as input")
        reader = read_tsv
    elif pathlib.Path(input).is_dir():
        logger.info("Found folder, expecting parquet file as input")
        reader = read_parquet
    if output.endswith(".tsv"):
        logger.info("Found suffix 'tsv', writing RDDs as tsvs")
        output = output.replace(".tsv", "")
        if not split:
            split = True
            logger.info("Setting split=true since 'tsv' output detected.")
        writer = write_tsv
    else:
        logger.info("Found no suffix, writing RDD as parquet!")
        writer = write_parquet

    with SparkSession() as spark:
        try:
            subsamp = sample(reader(spark, input), n)
            if split:
                subsamp = split_vector(subsamp, "features")
            writer(subsamp, output)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
