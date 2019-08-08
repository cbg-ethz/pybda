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
import datetime
import os
import re
import sys

import yaml

from pybda.config.rule_tree import RuleTree
from pybda.globals import (
    REQUIRED_ARGS__, INFILE__, OUTFOLDER__, METHODS__, DEBUG__
)
from pybda.util.string import drop_suffix

sys.excepthook = lambda ex, msg, _: print("{}: {}".format(ex.__name__, msg))


class PyBDAConfig:
    """
    Config class to
    - setup all required infiles,
    - check correct config-file arguments
    - some utility.
    """

    def __init__(self, config):
        date = datetime.datetime.now().strftime("%Y_%m_%d")

        for key, value in config.items():
            if key == OUTFOLDER__:
                value = os.path.join(value, date)
                if not os.path.exists(value):
                    os.makedirs(value)
            setattr(self, key, value)

        self.__tree = RuleTree(
          getattr(self, INFILE__),
          getattr(self, OUTFOLDER__))

        self.__check_required_args()
        self.__check_available_method()
        self.__set_filenames()

    def __getitem__(self, item):
        if isinstance(item, str):
            if hasattr(self, item):
                attr = getattr(self, item)
                return attr
        # TODO: this needs to be solved better
        # e.g. when dimred is called, we need to check arguments here
        # otherwise we can just return ""
        return ""

    def __contains__(self, item):
        return hasattr(self, item)

    def infiles(self, algorithm):
        infiles = self.__tree.infiles(algorithm)
        return infiles

    def outfiles(self, algorithm):
        return self.__tree.outfiles(algorithm)

    def outfiles_no_suffix(self, algorithm):
        outfiles = self.__tree.outfiles(algorithm)
        outfiles = [drop_suffix(out, '.tsv') for out in outfiles]
        return outfiles

    def outfiles_basename(self, algorithm):
        outfiles = self.__tree.outfiles(algorithm)
        reg = re.compile(r"(?:.*/)?(.*)\.tsv")
        outfiles = [reg.match(out).group(1) for out in outfiles]
        if len(outfiles) == 0:
            return '<none>'
        if len(outfiles) == 1:
            return outfiles[0]
        return outfiles

    def __check_required_args(self):
        for el in REQUIRED_ARGS__:
            if not hasattr(self, el):
                raise ValueError(
                  "'{}' needs to be a key-value pair in the config".format(el))

    def __check_available_method(self):
        if not any(hasattr(self, x) for x in METHODS__):
            raise ValueError("Provide at least one of the following methods: " +
                             "'{}'".format("/".join(METHODS__)))

    def __set_filenames(self):
        for m in METHODS__:
            if hasattr(self, m):
                attr = getattr(self, m)
                attr = attr.replace(" ", "").split(",")
                for el in attr:
                    self.__tree.add(m, el)
        for node in self.__tree.nodes.values():
            setattr(self, self.__infile_key(node.method), node.infile)
        if hasattr(self, DEBUG__):
            print("\033[1;33m Printing rule tree:")
            print(str(self.__tree) + "\033[0m")

    @staticmethod
    def __infile_key(method):
        return method + "_" + INFILE__
