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

from pybda.globals import FEATURES__, RAW_PREDICTION__, PROBABILITY__
from pybda.io.io import write_tsv

from pybda.spark.features import drop, split_vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TransformedData:
    def __init__(self, data):
        self.__data = data

    def write_files(self, outpath):
        """
        Write a transformed data set to tsv.

        :param outpath: the path to where the files are written.
        """

        outpath = outpath + "-transformed"
        data = drop(self.data, FEATURES__, RAW_PREDICTION__)
        data = split_vector(data, PROBABILITY__)
        write_tsv(data, outpath)

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data
