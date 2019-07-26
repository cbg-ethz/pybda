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
import numpy

import click

from pybda.decorators import timing
from pybda.io.as_filename import as_logfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _sample(data, variable, el, min_cnt, sample_ratio):
    df = data.filter("{} == '{}'".format(variable, el)).limit(min_cnt)
    df = df.sample(withReplacement=False, fraction=sample_ratio, seed=23)
    return df


@timing
def sample(data, n, variable=None):

    if variable:
        mcnt = data.groupby(variable).count().toPandas()
        els, cnts = mcnt[variable].values, mcnt["count"].values
        min_cnt = int(cnts.min())
        sample_ratio = float(min(n / min_cnt, 1)) / len(els)
        df = _sample(data, variable, els[0], min_cnt, sample_ratio)
        for i in range(1, len(els)):
            df_0 = _sample(data, variable, els[i], min_cnt, sample_ratio)
            df = df.union(df_0)
        return df

    sample_ratio = float(min(n / data.count(), 1))
    return data.sample(withReplacement=False, fraction=sample_ratio, seed=23)


@click.command()
@click.argument("file", type=str)
@click.argument("n", type=int)
@click.argument("outpath", type=str)
@click.option("-v", "--variable", default=None)
def run(file, n, outpath, variable):
    from pybda.logger import set_logger
    from pybda.spark_session import SparkSession
    from pybda.util.string import drop_suffix
    from pybda.io.io import write_tsv

    output = drop_suffix(outpath, "/")
    set_logger(as_logfile(output))

    with SparkSession() as spark:
        try:
            from pybda.io.io import read
            data = read(spark, file)
            subsamp = sample(data, n, variable)
            import os
            write_tsv(subsamp, output)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
