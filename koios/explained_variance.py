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


class ExplainedVariance:
    def __init__(self, left_boundary, k, right_boundary, K_max,
                 K_max_explained_variance,
                 explained_variance,
                 K_max_within_cluster_variance,
                 k_within_cluster_variance,
                 total_variance,
                 percent_explained_variance):
        self.__left_boundary = left_boundary
        self.__current = k
        self.__right_boundary = right_boundary
        self.__K = K_max
        self.__K_explained_variance = K_max_explained_variance
        self.__curr_explained_variance = explained_variance
        self.__K_sse = K_max_within_cluster_variance
        self.__curr_sse = k_within_cluster_variance
        self.__max_sse = total_variance
        self.__percent_explained_variance = percent_explained_variance

    def header(self):
        return "left_bound\tcurrent_model\tright_bound\t" \
               "K_max\tK_expl\tcurrent_expl\tmax_sse\tK_sse\tcurrent_sse\t" \
               "percent_improvement\n"

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
          self.__left_boundary, self.__current, self.__right_boundary,
          self.__K, self.__K_explained_variance, self.__curr_explained_variance,
          self.__max_sse, self.__K_sse, self.__curr_sse,
          self.__percent_explained_variance)
