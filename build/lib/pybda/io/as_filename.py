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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def as_logfile(fl):
    if fl.endswith(".tsv"):
        logfile = fl.replace(".tsv", ".log")
    else:
        logfile = fl + ".log"
    return logfile


def as_ssefile(fl):
    if fl.endswith(".tsv"):
        ssefile = fl.replace(".tsv", "-total_sse.tsv")
    else:
        ssefile = fl + "-total_sse.tsv"
    return ssefile


def as_loglikfile(fl):
    if fl.endswith(".tsv"):
        ssefile = fl.replace(".tsv", "-loglik.tsv")
    else:
        ssefile = fl + "-loglik.tsv"
    return ssefile
