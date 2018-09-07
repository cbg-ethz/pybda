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
from pyspark.sql.functions import udf, col
from pyspark.sql.types import ArrayType, DoubleType

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def feature_columns(data):
    """
    Takes a DataFrame and returns a list of feature columns

    :param data: sql.DataFrame
    :return: list of feature columns
    """

    return list(filter(
      lambda x: any(x.startswith(f) for f in ["cells", "perin", "nucle"]),
      data.columns))


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


def _as_array(vector):
    def to_array(col):
        def to_array_(v):
            return v.toArray().tolist()

        return udf(to_array_, ArrayType(DoubleType()))(col)

    return to_array(vector)


def split_vector(data, col_name):
    """
    Split a column which is a DenseVector into separate columns.

    :param data: a DataFrame
    :param col_name: column name of the feature to splot
    :return: returns a DataFrame with split columns
    """

    cols = data.columns
    if col_name not in cols:
        logger.info("Vector columns '{}' not found. Returning".format(col_name))
        return data

    logger.info("Splitting vector columns: {}".format(col_name))

    cols.remove(col_name)
    len_vec = len(data.select(col_name).take(1)[0][0])
    data = (
        data.withColumn("f", _as_array(col(col_name)))
            .select(cols + [col("f")[i] for i in range(len_vec)])
    )

    for i, x in enumerate(data.columns):
        if x.startswith("f["):
            data = data.withColumnRenamed(
              x, x.replace("[", "_").replace("]", ""))

    return data
