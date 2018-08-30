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
from pyspark.rdd import reduce

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def parquet_data_path(file_name):
    """
    Takes a file name with '.tsv' suffix and converts into a 'parquet' file
    name

    :param file_name: the file name from which the parquet name is computed
    :return: string of parquet file name
    """

    return file_name.replace(".tsv", "_parquet")


def write_parquet_data(outpath, data):
    """
    Write a data frama to an outpath in parquet format.
    Overwrites existing files!

    :param outpath: the path where the dataframe is written to
    :param data: data frame
    """

    logger.info("Writing parquet: {}".format(outpath))
    data.write.parquet(outpath, mode="overwrite")


def read_tsv(spark, file_name, header='true'):
    """
    Reads a tsv file as data frame

    :param spark: a running spark session
    :type spark: pyspark.sql.SparkSession
    :param file_name: the name of the tsv as string
    :param header: boolean if the tsv has a header
    :return: returns a data frame
    """

    return spark.read.csv(path=file_name, sep="\t", header=header)


def get_frame_from_tsv(file_name, spark):
    """
    Reads a data frame from a tsv file.

    :param file_name: the tsv file name as string
    :param spark: a running sparksession
    :type spark: pyspark.sql.SparkSession
    :return: returns a dataframe
    """

    logger.info("Reading: {}".format(file_name))
    return read_tsv(spark, file_name)


def fill_na(data, what=0):
    """
    Fill NA elements of a data frame with a value.

    :param data: a data frame
    :param what: the value with what the NAs are filled
    :return: returns the data frame with filled values
    """

    return data.fillna(what)


def to_double(data, columns):
    """
    Convert columns to double.

    :param data: a data frame
    :param columns: the column names of which the data should be converted.
    :type columns: list(str)
    :return: returns the data frame with newly cast colunms
    """

    feature_columns = columns
    for x in feature_columns:
        data = data.withColumn(x, data[x].cast("double"))

    return data


def replace_column_names(data, fro=".", to="_"):
    """
    Rename single characters columns of a data frame. After renaming the columns
    returns the data frame as well as the vector of new column names.

    :param data: the data frame of which you want to rename the columns
    :param fro: sequence which you want to replace in the column name
    :param to: sequence to which the columns are renamed
    :return: returns a tuple consisting of a data frame with new column names as
      well as the vector of new column names
    """

    old_cols = data.columns
    new_cols = list(map(lambda x: x.replace(fro, to), old_cols))

    data = reduce(
      lambda d, idx: d.withColumnRenamed(old_cols[idx], new_cols[idx]),
      range(len(new_cols)), data)

    return data, new_cols
