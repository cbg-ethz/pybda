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


from koios.config.config_node import ConfigNode
from koios.globals import PREPROCESSING_METHODS__


class ConfigTree:
    def __init__(self, infile, outfolder):
        self.__curr = None
        self.__nodes = {}
        self.__infile = infile
        self.__outfolder = outfolder

    @property
    def nodes(self):
        return self.__nodes

    def add(self, method, algorithm):
        par = self.__get_proper_parent()
        n = ConfigNode(method, algorithm, par, self.__infile, self.__outfolder)
        self.__nodes[method] = n
        self.__curr = n

    def __get_proper_parent(self):
        if self.__curr is None:
            return self.__curr
        n = self.__curr
        while n.method not in PREPROCESSING_METHODS__:
            n = n.parent
        return n

