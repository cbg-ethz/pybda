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

import re


def drop_suffix(string, suffix):
    if string.endswith(suffix):
        string = string.rstrip(suffix)
    return string


def matches(string, regex):
    reg = re.compile(regex).match(string)
    if reg is None:
        return False
    return True


def split(els, split):
    if not isinstance(els, list):
        raise TypeError("'els' should be list.")
    return [x.replace(" ", "").split(split) for x in els]


def paste(string, array):
    return list(map(string + '_{}'.format, array))
