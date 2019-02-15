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


import numpy


def sample(x, n, replace=False):
    return x if n >= len(x) else numpy.random.choice(x, n, replace=replace)


def mtrand(ncol,  nrow, seed=None):
    if not seed:
        seed = numpy.random.randint(0, 100)
    random_state = numpy.random.RandomState(seed)
    return numpy.asarray(random_state.normal(size=(nrow, ncol)))
