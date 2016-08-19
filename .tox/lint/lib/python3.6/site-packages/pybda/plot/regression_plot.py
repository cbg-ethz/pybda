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


def plot_curves(file_name, pr, roc):
    plt.figure(figsize=(8, 3), dpi=720)
    plt.xticks([0, 0.25, 0.5, 0.75, 1], ["0", "0.25", "0.5", "0.75", "1"])
    plt.yticks([0, 0.5, 1], ["0", "0.5", "1"])

    ax = plt.subplot(221)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines['left'].set_color('grey')
    ax.grid(linestyle="")
    plt.step(pr["recall"], pr["precision"], color='b', alpha=0.5, where='post')
    plt.plot([0, 0.5, 1], [0.5, 0.5, .5], color="black", alpha=.5)
    plt.xlabel("Recall", fontsize=12)
    plt.ylabel("Precision", fontsize=12)
    ax.set_ylim([0, 1])

    ax = plt.subplot(222)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines['left'].set_color('grey')
    ax.grid(linestyle="")
    plt.step(roc["FPR"], roc["TPR"], color='b', alpha=0.5, where='post')
    plt.plot([0, 0.5, 1], [0, 0.5, 1], color="black", alpha=.5)
    plt.xlabel("FPR", fontsize=12)
    plt.ylabel("TPR", fontsize=12)
    ax.set_ylim([0, 1])

    plt.subplots_adjust(wspace=0.3)
    plt.savefig(file_name, dpi=720)
    plt.close('all')
