
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FitProfile(ABC):
    @classmethod
    def as_profilefile(cls, fl):
        if fl.endswith(".tsv"):
            profilefile = fl.replace(".tsv", "-profile.tsv")
        else:
            profilefile = fl + "-profile.tsv"
        return profilefile

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
