
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
from abc import abstractmethod, ABC

import numpy
import pandas

from koios.globals import K_
from koios.plot.cluster_plot import plot_cluster_sizes

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FitProfile(ABC):
    def __init__(self, max, models=None):
        self.__maximum = max
        self.__ks = []
        self.__path = []
        self.__models = {} if models is None else models
        self.__loss = numpy.inf

    def __getitem__(self, key):
        return self.__models[key]

    @property
    def maximum(self):
        return self.__maximum

    @property
    def ks(self):
        return self.__ks

    @property
    def path(self):
        return self.__path

    @property
    def models(self):
        return self.__models

    @property
    def loss(self):
        return self.__loss

    @loss.setter
    def loss(self, x):
        self.__loss = x

    @property
    def last_loss(self):
        pass

    @classmethod
    def as_profilefile(cls, fl):
        if fl.endswith(".tsv"):
            profilefile = fl.replace(".tsv", "-profile.tsv")
        else:
            profilefile = fl + "-profile.tsv"
        return profilefile

    def write_files(self, outpath):
        self._write_path(outpath)
        self._write_cluster_quantiles(outpath)
        self._plot(outpath)

    def _write_path(self, outpath):
        lrt_file = FitProfile.as_profilefile(outpath)
        logger.info("Writing fit profile to {}".format(lrt_file))
        with open(lrt_file, "w") as fh:
            fh.write(self._header())
            for el in self.path:
                fh.write(str(el))

    def _write_cluster_quantiles(self, outpath):
        from koios.io.io import write_tsv
        cs_file = outpath + "-cluster_stats.tsv"
        logger.info("Writing cluster quantiles to {}".format(cs_file))

        data, _ = self._cluster_sizes(outpath)
        data[K_] = data[K_].astype(int)
        data = data.groupby(K_).quantile([0, 0.25, 0.5, 0.75, 1])
        data = data.unstack(K_)["c"]
        data.columns = list(map(lambda x: "K{}".format(x), data.columns))
        data.insert(loc=0,
                    column="quantile",
                    value=list(map(lambda x: x, data.index)))

        write_tsv(data, cs_file, index=False)

    def as_pandas(self):
        df = [None] * len(self.__path)
        for i, e in enumerate(self.__path):
            df[i] = e.values
        return pandas.DataFrame(df)

    @abstractmethod
    def _plot(self, outpath):
        pass

    def _cluster_sizes(self, path):
        import glob
        import re

        fls = glob.glob(path + "*/*cluster_sizes.tsv")
        reg = re.compile(".*K(\d+)_cluster_sizes.tsv")
        ll = self.as_pandas()

        frames = [None] * len(fls)
        for i, fl in enumerate(fls):
            t = pandas.read_csv(fl, sep="\t", header=-1, names="c")
            idx = int(reg.match(fl).group(1))
            t[K_] = str(idx).zfill(9)
            frames[i] = [idx, t]

        frames = sorted(frames, key=lambda x: x[0])
        frames = list(filter(lambda x: x[0] in ll["k"].values, frames))

        labels = list(map(lambda x: "K = {}".format(x[0]), frames))
        data = pandas.concat(map(lambda x: x[1], frames))

        return data, labels

    @abstractmethod
    def _header(self):
        pass

    @property
    def current_model(self):
        return self.__models[self.__ks[-1]]

    @property
    def max_model(self):
        if not self.has_max_model():
            return None
        return self.__models[self.__maximum]

    def has_max_model(self):
        return self.__maximum in self.__models.keys()

    def keys(self):
        return self.__models.keys()

    @abstractmethod
    def _loss(self, model):
        pass

    @abstractmethod
    def add(self, model, left, k, right):
        pass