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
import queue

from koios.config.rule_node import RuleNode
from koios.globals import PREPROCESSING_METHODS__, PARENT_METHODS__


class RuleTree:
    def __init__(self, infile, outfolder):
        self.__root = RuleNode("_", None, None, "", infile)
        self.__curr = self.__root
        self.__nodes = {}
        self.__infile = infile
        self.__outfolder = outfolder

    def __str__(self):
        stack = [self.__root]
        tree = ""
        while len(stack):
            node = stack.pop()
            tree = self.__tree(node, tree)
            for c in node.children:
                stack.append(c)
        return tree

    @staticmethod
    def __tree(node, str):
        str += "\t" * node.level + " -> " + node.method + \
               " (" + node.infile + ", " + node.outfile + ")\n"
        return str

    @property
    def nodes(self):
        return self.__nodes

    def add(self, method, algorithm):
        par = self.__get_proper_parent(method)
        n = RuleNode(method, algorithm, par, self.__infile, self.__outfolder)
        self.__nodes[method] = n
        par.add(n)
        self.__curr = n

    def __get_proper_parent(self, method):
        if self.__curr is self.__root:
            return self.__root
        if method not in PARENT_METHODS__:
            itr = PREPROCESSING_METHODS__
        else:
            itr = PARENT_METHODS__[method]
        if itr is None:
            return self.__root
        n = self.__curr
        while n.method not in itr:
            n = n.parent
        return n
