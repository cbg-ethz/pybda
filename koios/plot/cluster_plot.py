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

import joypy
import matplotlib.pyplot as plt
import numpy

from koios.globals import PLOT_FONT_, PLOT_FONT_FAMILY_, PLOT_STYLE_, RED_, K_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

plt.style.use([PLOT_STYLE_])
plt.rcParams['font.family'] = PLOT_FONT_FAMILY_
plt.rcParams['font.sans-serif'] = [PLOT_FONT_]


def plot_cluster_sizes(file_name, data, labels):
    _, ax = plt.subplots(figsize=(7, 4))
    fig, axes = joypy.joyplot(data, by=K_, hist="True", ax=ax,
                              bins=50, overlap=0, grid="y", color="grey",
                              labels=labels)
    for x in axes:
        x.spines['bottom'].set_color('grey')
        x.grid(color="grey", axis="y")
    plt.title("Cluster size distributions", x=0.05, y=.9, fontsize=12)
    plt.savefig(file_name, dpi=720)


def plot_profile(file_name, profile, col):
    fig, ax = plt.subplots()
    ax.grid(linestyle="")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylabel('#clusters')
    ax.set_ylabel('Explained variance in %')
    bar = plt.bar(list(map(str, profile[K_].values)),
                  profile[col].values, color="black",
                  alpha=.75)
    for rect in bar:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2.0, height,
                 '{}%'.format(int(float(height) * 100)), ha='center',
                 va='bottom')

    plt.savefig(file_name, dpi=720)