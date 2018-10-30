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


class ConfigNode:
    def __init__(self, method, algorithm, parent, infile, outfolder):
        self.__method = method
        self.__algorithm = algorithm
        self.__parent = parent
        self.__infile = infile if parent is None else parent.outfile
        self.__outfile = os.path.join(outfolder, algorithm)

    def __str__(self):
        return "'{}'".format(self.__method)

    def __repr__(self):
        return " -> {}-{}-{}-{}-{}".format(self.method, self.algorithm,
                                           self.parent,
                                           self.infile, self.outfile)

    @property
    def method(self):
        return self.__method

    @property
    def infile(self):
        return self.__infile

    @property
    def outfile(self):
        return self.__outfile

    @property
    def parent(self):
        return self.__parent

    @property
    def algorithm(self):
        return self.__algorithm
