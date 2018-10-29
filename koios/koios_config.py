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


import os

from koios.config.config_tree import ConfigTree
from koios.config.node import Node


class KoiosConfig:
    """
    Config class to
    - setup all required infiles,
    - check correct config-file arguments
    - some utility.
    """

    def __init__(self, config):
        for key, value in config.items():
            setattr(self, key, value)
        self.__check_required_args()
        self.__check_available_method()
        self.__set_filenames()

    def __check_required_args(self):
        for el in KoiosConfig.__REQUIRED_ARGS__:
            if not hasattr(self, el):
                raise ValueError(
                  "'{}' needs to be a key-value pair in the config".format(el))

    def __check_available_method(self):
        if not any(hasattr(self, x) for x in KoiosConfig.__METHODS__):
            raise ValueError(
              "Provide at least one of the following methods: " +
              "'{}'".format("/".join(KoiosConfig.__METHODS__)))

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        raise ValueError("Config does not have element '{}'".format(item))

    def __set_filenames(self):
        self.__set_dimred()
        self.__set_outliers()
        self.__set_clustering()
        self.__set_regression()

    def __base_infile(self):
        return getattr(self, KoiosConfig.__INFILE__)

    def __set_infile(self, attr, name):
        setattr(self, attr, name)
        self.keys.add(attr)

    @staticmethod
    def __build_path(folder):
        return os.path.join(KoiosConfig.__OUTFOLDER__, folder)

    def __set_dimred(self):
        if not hasattr(self, KoiosConfig.__DIM_RED__):
            return
        inf = self.__base_infile()
        self.__set_infile(KoiosConfig.__DIM_RED_INFILE__, inf)

    def __set_outliers(self):
        if not hasattr(self, KoiosConfig.__OUTLIERS__):
            return
        if hasattr(self, KoiosConfig.__DIM_RED__):
            inf = self.__build_path(getattr(self, KoiosConfig.__DIM_RED__))
        else:
            inf = self.__base_infile()
        self.__set_infile(KoiosConfig.__OUTLIERS_INFILE__, inf)

    def __set_clustering(self):
        if not hasattr(self, KoiosConfig.__CLUSTERING__):
            return
        if hasattr(self, KoiosConfig.__OUTLIERS__):
            inf = self.__build_path(getattr(self, KoiosConfig.__OUTLIERS__))
        elif hasattr(self, KoiosConfig.__DIM_RED__):
            inf = self.__build_path(getattr(self, KoiosConfig.__DIM_RED__))
        else:
            inf = self.__base_infile()
        self.__set_infile(KoiosConfig.__CLUSTERING_INFILE__, inf)

    def __set_regression(self):
        if not hasattr(self, KoiosConfig.__REGRESSION__):
            return
        inf = self.__base_infile()
        self.__set_infile(KoiosConfig.__REGRESSION_INFILE__, inf)

    __SPARK__ = "spark"

    __INFILE__ = "infile"
    __OUTFOLDER__ = "outfolder"

    __META__ = "meta"
    __FEATURES__ = "features"
    __RESPONSE__ = "response"

    __DIM_RED__ = "dimension_reduction"
    __DIM_RED_INFILE__ = "dimension_reduction_infile"
    __PCA__ = "pca"
    __KPCA__ = "kpca"
    __FACTOR_ANALYSIS__ = "factor_analysis"
    __N_COMPONENTS__ = "N_components"

    __OUTLIERS__ = "outliers"
    __OUTLIERS_INFILE__ = "outliers_infile"

    __CLUSTERING__ = "clustering"
    __CLUSTERING_INFILE__ = "clustering_infile"
    __KMEANS__ = "kmeans"
    __GMM__ = "gmm"
    __MAX_CENTERS__ = "max_centers"
    __N_CENTERS__ = "n_centers"

    __REGRESSION__ = "regression"
    __REGRESSION_INFILE__ = "regression_infile"
    __GLM__ = "glm"
    __FAMILY__ = "family"

    __RULE_INFILE__ = "rule_infile"

    __REQUIRED_ARGS__ = [
        __SPARK__,
        __INFILE__,
        __OUTFOLDER__
    ]
    __METHODS__ = [
        __DIM_RED__,
        __OUTLIERS__,
        __CLUSTERING__,
        __REGRESSION__
    ]
