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
import scipy

import pyspark.sql
from pyspark.ml.feature import VectorAssembler
from pyspark.rdd import reduce
from pyspark.sql.functions import col

from pybda.globals import FLOAT_, FLOAT64_, FEATURES__
from pybda.util.cast_as import as_array

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fill_na(data, what=0):
    """
    Fill NA elements of a data frame with a value.

    :param data: a data frame
    :param what: the value with what the NAs are filled
    :return: returns the data frame with filled values
    """

    return data.fillna(what)


def to_double(data, feature_cols, response=None):
    """
    Convert columns to double.

    :param data: a data frame
    :param feature_cols: the column names of which the data should be converted.
    :type feature_cols: list(str)
    :param response: the name of the response column if any
    :return: returns the data frame with newly cast colunms
    """

    has_feature_col = False
    cols = data.columns
    column_types = {x: y for (x, y) in data.dtypes}

    if FEATURES__ in column_types.keys():
        feature_vec = scipy.array(data.select(FEATURES__).take(1)[0][0])
        if len(feature_vec) != len(feature_cols):
            raise ValueError("Size of DataFrame 'feature' vector != "
                             "Size feature provided file")
        if feature_vec.dtype is not FLOAT64_:
            raise TypeError("'features' column ist not if type float")
        has_feature_col = True

    f_cols = list(filter(lambda x: x.startswith("f_"), cols))
    if len(f_cols):
        logger.info(
            "Found columns with prefix f_ from previous computation: {}.\n"
            "Preferring these columns as features/"
            "".format("\t".join(f_cols)))
        feature_cols = f_cols

    logger.info("Casting columns to double.")
    for x in feature_cols:
        if x in cols and has_feature_col:
            logger.warning("Your DataFrame has a 'features' column "
                           "AND a separate column '{}'".format(x))
        if x not in column_types.keys():
            raise ValueError("Couldn't find column '{}' in DataFrame".format(x))
        if column_types[x] != FLOAT_:
            data = data.withColumn(x, data[x].cast("float"))

    if response:
        if column_types[response] != FLOAT_:
            data = data.withColumn(response, data[response].cast("float"))

    return data


def assemble(data, feature_cols, drop=True):
    """
    Combine multiple features into a feature column. If 'drop' is True will
    drop the columns we dont need.

    :param data: sql.DataFrame
    :param feature_cols: the column names of which the data should be converted.
    :type feature_cols: list(str)
    :param drop: boolean if faeture columns should be dropped
    :return: returns the DataFrame with assembled features
    """

    cols = data.columns
    if FEATURES__ not in cols:
        logger.info("Assembling column to feature vector")
        f_cols = list(filter(lambda x: x.startswith("f_"), cols))
        if len(f_cols):
            logger.info(
                "Found columns with prefix f_ from previous computation: {}. "
                "Preferring these columns as features"
                "".format("\t".join(f_cols)))
            feature_cols = f_cols
        assembler = VectorAssembler(inputCols=feature_cols,
                                    outputCol=FEATURES__)
        data = assembler.transform(data)
    else:
        logger.info("Features already assembled")
    if drop:
        logger.info("Dropping redundant columns")
        data = data.drop(*feature_cols)

    return data


def drop(data, *columns):
    """
    Drop a list of columns
    """
    for column in columns:
        if column in data.columns:
            logger.info("Dropping column '{}'".format(column))
            data = data.drop(column)
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


def split_vector(data, col_name):
    """
    Split a column which is a DenseVector into separate columns.

    :param data: a DataFrame
    :param col_name: column name of the feature to splot
    :return: returns a DataFrame with split columns
    """

    cols = data.columns
    if col_name not in cols:
        logger.info("Vector col '{}' not found. Returning".format(col_name))
        return data

    logger.info("Splitting vector columns: {}".format(col_name))
    cols.remove(col_name)
    initial = col_name[0]
    len_vec = len(data.select(col_name).take(1)[0][0])
    data = (data.withColumn(initial, as_array(
        col(col_name))).select(cols + [col(initial)[i]
                                       for i in range(len_vec)]))

    for _, x in enumerate(data.columns):
        if x.startswith(initial + "["):
            data = data.withColumnRenamed(x,
                                          x.replace("[", "_").replace("]", ""))

    return data


def n_features(data: pyspark.sql.DataFrame, col_name):
    return len(scipy.asarray(data.select(col_name).take(1)).flatten())


def distinct(data: pyspark.sql.DataFrame, col_name):
    return (data.select(col_name).distinct().toPandas().values.flatten())
