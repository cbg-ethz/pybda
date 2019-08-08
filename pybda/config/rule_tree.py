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


from pybda.config.rule_node import RuleNode
from pybda.globals import PREPROCESSING_METHODS__, PARENT_METHODS__


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

    def __iter__(self):
        st = [self.__root]
        while len(st):
            n = st.pop()
            for el in n.children:
                st.append(el)
            yield n

    @staticmethod
    def __tree(node, stri):
        stri += "\t" * node.level + " -> " + node.method + \
                " (" + node.infile + ", " + node.outfile + ")\n"
        return stri

    @property
    def nodes(self):
        return self.__nodes

    def infiles(self, algorithm):
        infiles = [n.infile for n in self if n.algorithm == algorithm]
        return infiles

    def outfiles(self, algorithm):
        outfiles = [n.outfile for n in self if n.algorithm == algorithm]
        return outfiles

    def add(self, method, algorithm):
        par = self.__get_proper_parents(method)
        for el in par:
            n = RuleNode(method, algorithm, el, self.__infile, self.__outfolder)
            self.__nodes[method] = n
            el.add(n)
            self.__curr = n

    def __get_proper_parents(self, method):
        if self.__curr is self.__root:
            return [self.__root]
        if method not in PARENT_METHODS__:
            itr = PREPROCESSING_METHODS__
        else:
            itr = PARENT_METHODS__[method]
        if itr is None:
            return [self.__root]

        parents = []
        for n in self:
            if n.method in itr:
                parents.append(n)
        if not parents:
            return [self.__root]
        return parents
