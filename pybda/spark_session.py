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
import pyspark

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SparkSession:
    def __init__(self):
        pyspark.StorageLevel(True, True, False, False, 2)

    def __enter__(self):
        logger.info("Initializing pyspark session")
        spark = pyspark.sql.SparkSession.builder.getOrCreate()
        for conf in spark.sparkContext.getConf().getAll():
            logger.info("Config: %s, value: %s", conf[0], conf[1])

        self.__session = spark
        return self.__session

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Stopping Spark context")
        self.__session.stop()
