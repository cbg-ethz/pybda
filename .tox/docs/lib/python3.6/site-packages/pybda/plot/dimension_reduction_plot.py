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

import matplotlib.pyplot as plt
import numpy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def plot_cumulative_variance(file_name, cum_exp_var, xlab):
    _, ax = plt.subplots(figsize=(8, 5), dpi=720)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    ax.xaxis.set_label_coords(x=.9, y=-0.075)
    ax.yaxis.set_label_coords(x=-0.075, y=.80)
    ax.grid(linestyle="")
    ax.grid(which="major", axis="y", linestyle="-", color="gainsboro")

    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    bar = plt.bar(list(map(str, range(1, len(cum_exp_var) + 1))),
                  cum_exp_var,
                  color="#696969")

    for i, rect in enumerate(bar):
        cum_exp_var[i] = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2.0,
                 cum_exp_var[i],
                 '%s' % str(round(cum_exp_var[i], 2)),
                 ha='center',
                 va='bottom')

    plt.xlabel(xlab, fontsize=15)
    plt.ylabel("Cumulative Variance", fontsize=15)
    plt.tight_layout()
    plt.savefig(file_name, dpi=720)
    plt.close('all')


def biplot(file_name, data, xlab, ylab):
    vals = data.transpose().values
    cols = numpy.array(list(data.columns), dtype="str")
    nms = numpy.empty(len(cols), dtype="<U43")

    good_x_idx = numpy.argwhere(numpy.abs(vals[:, 0]) > .25)
    good_y_idx = numpy.argwhere(numpy.abs(vals[:, 1]) > .25)
    nms[good_x_idx] = cols[good_x_idx]
    nms[good_y_idx] = cols[good_y_idx]

    _, ax = plt.subplots(figsize=(9, 6), dpi=720)
    for i in ["top", "bottom", "left", "right"]:
        ax.spines[i].set_visible(False)
    ax.xaxis.set_label_coords(x=1, y=-0.075)
    ax.yaxis.set_label_coords(x=-0.075, y=1)
    ax.grid(which="major", axis="both", linestyle="-", color="gainsboro")

    for i, nm in enumerate(nms):
        plt.arrow(0, 0, vals[i, 0], vals[i, 1], color='#696969', alpha=0.75)
        plt.text(vals[i, 0] * 1.15, vals[i, 1] * 1.15, nm, color='black',
                 ha='center', va='center', size=6)
    plt.scatter(vals[:, 0], vals[:, 1], color='#696969')
    plt.xlabel(xlab, fontsize=15)
    plt.ylabel(ylab, fontsize=15)
    plt.tight_layout()
    plt.savefig(file_name, dpi=720)
    plt.close('all')
