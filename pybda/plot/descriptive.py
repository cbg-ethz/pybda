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
import seaborn as sns

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sns.set_style("white", {'axes.grid': False})


def scatter(file_name, data, x, y, xlab, ylab, color=None):
    _, ax = plt.subplots(figsize=(8, 5), dpi=720)
    if color is not None:
        ax = sns.scatterplot(x=x, y=y, hue=color, data=data, palette="muted")
    else:
        ax = sns.scatterplot(x=x, y=y, data=data, palette="muted")
    ax.xaxis.set_label_coords(x=1, y=-0.075)
    ax.yaxis.set_label_coords(x=-0.075, y=.95)
    ax.grid(False)
    sns.despine()
    plt.xlabel(xlab, fontsize=15)
    plt.ylabel(ylab, fontsize=15)
    plt.tight_layout()
    plt.savefig(file_name, dpi=720)
    plt.close('all')


def histogram(file_name, x, xlab, ylab="Frequency"):
    _, ax = plt.subplots(figsize=(8, 5), dpi=720)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)
    ax.xaxis.set_label_coords(x=1, y=-0.075)
    ax.yaxis.set_label_coords(x=-0.075, y=.9)
    ax.grid(False)
    sns.despine()
    plt.hist(x, color="black", alpha=.5, bins=50)

    plt.xlabel(xlab, fontsize=15)
    plt.ylabel(ylab, fontsize=15)
    plt.tight_layout()
    plt.savefig(file_name, dpi=720)
    plt.close('all')
