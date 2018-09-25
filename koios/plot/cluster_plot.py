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


def plot_profile(file_name, profile):
    profile["iteration"] = list(range(0, profile.shape[0]))
    ref_mod = profile.loc[[profile[K_].idxmax()]]
    sel_mod = profile.loc[[profile.shape[0] - 1]]
    min_mod = profile.loc[[profile[K_].idxmin()]]
    min_idx = profile[K_].values.argsort()[1]

    fig = plt.figure(figsize=(7, 3), dpi=720)

    ax = plt.subplot(221)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines['left'].set_color('grey')
    ax.xaxis.set_label_coords(x=.85, y=-0.1)
    ax.yaxis.set_ticks([min_mod[K_].values,
                        sel_mod[K_].values,
                        ref_mod[K_].values])
    ax.yaxis.set_label_coords(x=-0.05, y=.885)
    ax.xaxis.set_ticks([1, profile["iteration"].values[-1]])
    ax.grid(linestyle="")

    plt.scatter(profile["iteration"].values, profile[K_].values, color="black",
                alpha=.75)
    plt.plot(profile["iteration"].values, profile[K_].values, color="black",
             alpha=.35, lw=1)
    plt.scatter(ref_mod["iteration"].values,
                ref_mod[K_].values, color=RED_, alpha=1)
    plt.scatter(sel_mod["iteration"].values, sel_mod[K_].values,
                color=RED_, alpha=1)

    ax.text(ref_mod["iteration"].values, ref_mod[K_].values,
            "Reference", ha="left", va="bottom", fontsize="smaller")
    ax.text(sel_mod["iteration"].values, sel_mod[K_].values,
            "Selected K", ha="right", va="bottom", fontsize="smaller")

    plt.xlabel("# of recursions", fontsize=12)
    plt.ylabel("", fontsize=15)
    plt.title("Number of clusters", x=0.13, fontsize=12)

    ax = plt.subplot(222)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines['left'].set_color('grey')
    ax.xaxis.set_label_coords(x=.85, y=-0.1)
    ax.yaxis.set_ticks([profile["explained_variance"].values[min_idx],
                        sel_mod["explained_variance"].values,
                        ref_mod["explained_variance"].values])
    ax.yaxis.set_label_coords(x=-0.05, y=.885)
    ax.grid(linestyle="")

    plt.scatter(profile["iteration"].values[1:],
                profile["explained_variance"].values[1:],
                color="black", alpha=.75)
    plt.plot(profile["iteration"].values[1:],
             profile["explained_variance"].values[1:],
             color="black", alpha=.35, lw=1)
    plt.scatter(ref_mod["iteration"].values,
                ref_mod["explained_variance"].values,
                color="#990000", alpha=1)
    plt.scatter(sel_mod["iteration"].values,
                sel_mod["explained_variance"].values,
                color="#990000", alpha=1)

    ax.text(ref_mod["iteration"].values,
            ref_mod["explained_variance"].values, "Reference",
            ha="left", va="bottom", fontsize="smaller")
    ax.text(sel_mod["iteration"].values,
            sel_mod["explained_variance"].values, "Selected K",
            ha="right", va="bottom", fontsize="smaller")

    ax.set_xlim([0, ax.get_xlim()[1]])
    ax.xaxis.set_ticks([1, profile["iteration"].values[-1]])

    plt.xlabel("# of recursions", fontsize=12)
    plt.ylabel("", fontsize=15)
    plt.title("Explained Variance", x=0.13, fontsize=12)
    plt.subplots_adjust(bottom=-.75)
    plt.savefig(file_name, dpi=720)
