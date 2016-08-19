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

import collections
from pybda.globals import (DIM_RED__, REGRESSION__, INFILE__, SPARK__,
                           OUTFOLDER__, FEATURES__, CLUSTERING__,
                           N_COMPONENTS__, N_CENTERS__, META__, RESPONSE__,
                           FAMILY__, LDA__)

REQUIRED_ARGS = [SPARK__, INFILE__, OUTFOLDER__, META__, FEATURES__]
METHOD_REQUIRED_ARGS = collections.OrderedDict(
    [(DIM_RED__, REQUIRED_ARGS + [DIM_RED__, N_COMPONENTS__]),
     (CLUSTERING__, REQUIRED_ARGS + [CLUSTERING__, N_CENTERS__]),
     (REGRESSION__, REQUIRED_ARGS + [REGRESSION__, FAMILY__, RESPONSE__])])
ALGORITHM_REQUIRED_ARGS = collections.OrderedDict([(LDA__, [RESPONSE__])])


def _check_missing_arg(config, arg):
    if arg not in config.keys():
        print("\033[1;31mMissing argument in config file. "
              "Could not find argument: {} \033[0m".format(arg))
        exit(-1)


def _check_args(config, method):
    reg_args = METHOD_REQUIRED_ARGS[method]
    if config[method] in ALGORITHM_REQUIRED_ARGS.keys():
        reg_args = reg_args + ALGORITHM_REQUIRED_ARGS[LDA__]
    for reg_arg in reg_args:
        _check_missing_arg(config, reg_arg)


def check_args(config, method):
    print("Checking command line arguments for method: {}".format(method))
    _check_missing_arg(config, method)
    for alg in [DIM_RED__, CLUSTERING__, REGRESSION__]:
        if alg in config.keys():
            _check_args(config, alg)
