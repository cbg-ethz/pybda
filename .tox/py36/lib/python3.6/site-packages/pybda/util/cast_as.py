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

from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType, ArrayType

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def as_array(vector):
    def to_array(col):
        def to_array_(v):
            return v.toArray().tolist()

        return udf(to_array_, ArrayType(DoubleType()))(col)

    return to_array(vector)


def as_pandas(data):
    """
    Takes a sqlDataFrame and returns a pandas data frame

    :param data: sql.DataFrame
    :return: pandas.DataFrame
    """

    return data.toPandas()


def as_rdd_of_array(data):
    return data.rdd.map(numpy.array)
