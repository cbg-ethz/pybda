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

from koios.globals import PLOT_FONT_, PLOT_FONT_FAMILY_, PLOT_STYLE_, RED_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

plt.style.use([PLOT_STYLE_])
plt.rcParams['font.family'] = PLOT_FONT_FAMILY_
plt.rcParams['font.sans-serif'] = [PLOT_FONT_]


def plot_profile(file_name, profile):
    profile["Iteration"] = list(range(0, profile.shape[0]))
    ref_mod = profile.loc[[profile["k"].idxmax()]]
    sel_mod = profile.loc[[profile.shape[0] - 1]]
    min_mod = profile.loc[[profile["k"].idxmin()]]
    min_idx = profile["k"].values.argsort()[1]

    _ = plt.figure(figsize=(12, 7), dpi=720)

    ax = plt.subplot(221)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines['left'].set_color('grey')
    ax.xaxis.set_label_coords(x=.85, y=-0.1)
    ax.yaxis.set_ticks([min_mod["k"].values,
                        sel_mod["k"].values,
                        ref_mod["k"].values])
    ax.yaxis.set_label_coords(x=-0.05, y=.885)
    ax.xaxis.set_ticks([1, profile["Iteration"].values[-1]])
    ax.grid(linestyle="")

    plt.scatter(profile["Iteration"].values, profile["k"].values, color="black",
                alpha=.75)
    plt.plot(profile["Iteration"].values, profile["k"].values, color="black",
             alpha=.35, lw=1)
    plt.scatter(ref_mod["Iteration"].values,
                ref_mod["k"].values, color=RED_, alpha=1)
    plt.scatter(sel_mod["Iteration"].values, sel_mod["k"].values,
                color=RED_, alpha=1)

    ax.text(ref_mod["Iteration"].values, ref_mod["k"].values,
            "Reference", ha="left", va="bottom", fontsize="smaller")
    ax.text(sel_mod["Iteration"].values, sel_mod["k"].values,
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

    plt.scatter(profile["Iteration"].values[1:],
                profile["explained_variance"].values[1:],
                color="black", alpha=.75)
    plt.plot(profile["Iteration"].values[1:],
             profile["explained_variance"].values[1:],
             color="black", alpha=.35, lw=1)
    plt.scatter(ref_mod["Iteration"].values,
                ref_mod["explained_variance"].values,
                color="#990000", alpha=1)
    plt.scatter(sel_mod["Iteration"].values,
                sel_mod["explained_variance"].values,
                color="#990000", alpha=1)

    ax.text(ref_mod["Iteration"].values,
            ref_mod["explained_variance"].values, "Reference",
            ha="left", va="bottom", fontsize="smaller")
    ax.text(sel_mod["Iteration"].values,
            sel_mod["explained_variance"].values, "Selected K",
            ha="right", va="bottom", fontsize="smaller")

    ax.set_xlim([0, ax.get_xlim()[1]])
    ax.xaxis.set_ticks([1, profile["Iteration"].values[-1]])

    plt.xlabel("# of recursions", fontsize=12)
    plt.ylabel("", fontsize=15)
    plt.title("Explained Variance", x=0.13, fontsize=12)

    plt.savefig(file_name, dpi=720)
