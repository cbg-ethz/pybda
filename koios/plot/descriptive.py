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


import logging
import scipy
import matplotlib.pyplot as plt

from koios.globals import PLOT_FONT_, PLOT_FONT_FAMILY_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

plt.rcParams['font.family'] = PLOT_FONT_FAMILY_
plt.rcParams['font.sans-serif'] = [PLOT_FONT_]


def scatter(file_name, x, y,
            xlab, ylab, xlim=2, ylim=2,
            xlabpos=.95, ylabpos=.885):
    _, ax = plt.subplots(figsize=(8, 5), dpi=720)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_label_coords(x=xlabpos, y=-0.1)
    ax.yaxis.set_label_coords(x=-0.05, y=ylabpos)
    ax.grid(linestyle="")

    plt.xlim(-xlim, xlim)
    plt.ylim(-ylim, ylim)
    plt.xticks(scipy.arange(-xlim, xlim + 1, step=1))
    plt.yticks(scipy.arange(-ylim, ylim + 1, step=1))

    plt.scatter(x, y, color="black", alpha=.5, s=.5)
    plt.xlabel(xlab, fontsize=15)
    plt.ylabel(ylab, fontsize=15)

    plt.savefig(file_name, dpi=720)


def histogram(file_name, x, xlab, ylab="Frequency",
              xlabpos=.95, ylabpos=.885):
    _, ax = plt.subplots(figsize=(8, 5), dpi=720)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)
    ax.xaxis.set_label_coords(x=xlabpos, y=-0.1)
    ax.yaxis.set_label_coords(x=-0.05, y=ylabpos)
    ax.grid(linestyle="")

    plt.hist(x, color="black", alpha=.5, bins=50)

    plt.xlabel(xlab, fontsize=15)
    plt.ylabel(ylab, fontsize=15)
    plt.savefig(file_name, dpi=720)
