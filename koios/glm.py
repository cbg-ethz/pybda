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

from koios.regression import Regression

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GLM(Regression):
    def __init__(self, spark, family="gaussian", ):
        super().__init__(spark, threshold, max_iter)



@click.command()
@click.argument("family", type=int)
@click.argument("", type=str)
@click.argument("outpath", type=str)
def run(factors, file, outpath):
    from koios.util.string import drop_suffix
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.io.io import read_tsv
    from koios.io.as_filename import as_logfile

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            data = read_tsv(spark, file)
            data = to_double(data, feature_columns(data))
            data = fill_na(data)

            fl = FactorAnalysis(spark, factors, max_iter=25)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
