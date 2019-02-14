# Copyright (C) 2018, 2019 Simon Dirmeier
#
# This file is part of pybda.
#
# pybda is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pybda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybda. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import logging

import click

from pybda.io.as_filename import as_logfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def sample(data, n):
    data_row_cnt = data.count()
    sample_ratio = float(min(n / data_row_cnt, 1))
    return data.sample(withReplacement=False, fraction=sample_ratio, seed=23)


@click.command()
@click.argument("file", type=str)
@click.argument("output", type=str)
@click.argument("n", type=int)
def run(file, output, n):
    from pybda.logger import set_logger
    from pybda.spark_session import SparkSession
    from pybda.util.string import drop_suffix
    from pybda.io.io import write_tsv

    output = drop_suffix(output, "/")
    set_logger(as_logfile(output))

    with SparkSession() as spark:
        try:
            from pybda.io.io import read
            data = read(spark, file)
            subsamp = sample(data, n)
            write_tsv(subsamp, output)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
