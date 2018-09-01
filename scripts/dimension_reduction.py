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
import pyspark
from koios.factor_analysis import FactorAnalysis

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')


def factor_analysis(outpath, file, factors, maxit=25):
    if outpath.endswith("/"):
        outpath = outpath[:-1]
    hdlr = logging.FileHandler(outpath + ".log")
    hdlr.setFormatter(frmtr)
    logger.addHandler(hdlr)

    logger.info("Initializing pyspark session")
    pyspark.StorageLevel(True, True, False, False, 1)
    spark = pyspark.sql.SparkSession.builder.getOrCreate()

    try:
        from koios.io.io import read_tsv
        data = read_tsv(file)
        fl = FactorAnalysis(spark, max_iter=maxit)
        fit = fl.fit(data, factors)
        fit.write_files(outpath)
    except Exception as e:
        logger.error("Some error: {}".format(str(e)))

    logger.info("Stopping pyspark context")
    spark.stop()
