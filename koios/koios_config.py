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
import sys

from koios.config.config_tree import ConfigTree
from koios.globals import REQUIRED_ARGS__, REGRESSION_INFILE__, REGRESSION__, \
    CLUSTERING_INFILE__, DIM_RED__, INFILE__, OUTFOLDER__, DIM_RED_INFILE__, \
    OUTLIERS__, OUTLIERS_INFILE__, CLUSTERING__, METHODS__

sys.excepthook = lambda ex, msg, _: print("{}: {}".format(ex.__name__, msg))


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
        self.__config_tree = ConfigTree(getattr(self, INFILE__),
                                        getattr(self, OUTFOLDER__))
        self.__check_required_args()
        self.__check_available_method()
        self.__set_filenames()

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        raise ValueError(
          "Config file does not have required element '{}'".format(item))

    def __contains__(self, item):
        return hasattr(self, item)

    def __check_required_args(self):
        for el in REQUIRED_ARGS__:
            if not hasattr(self, el):
                raise ValueError(
                  "'{}' needs to be a key-value pair in the config".format(el))

    def __check_available_method(self):
        if not any(hasattr(self, x) for x in METHODS__):
            raise ValueError(
              "Provide at least one of the following methods: " +
              "'{}'".format("/".join(METHODS__)))

    def __set_filenames(self):
        for m in METHODS__:
            if hasattr(self, m):
                self.__config_tree.add(m, getattr(self, m))
        for node in self.__config_tree.nodes.values():
            setattr(self, self.__infile_key(node.method), node.infile)

    @staticmethod
    def __infile_key(method):
        return method + "_" + INFILE__
