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


import glob
import logging
import pathlib

import pandas
from abc import abstractmethod

from pyspark.sql.functions import col

from pybda.fit.predicted_data import PredictedData
from pybda.io.io import rm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ClusteringTransformed(PredictedData):
    def __init__(self, data):
        super().__init__(data)

    def write(self, outpath, k):
        outpath = outpath + "-transformed-K{}".format(k)
        self.write_clusters(outpath)

    @abstractmethod
    def write_clusters(self, outpath, suff="", sort_me=True):
        pass

    @staticmethod
    def _write_clusters(data, outpath, sort_me):
        if sort_me:
            data.sort(col('prediction'))
        data.write.csv(path=outpath, sep='\t', mode='overwrite', header=True)
        files = [x for x in glob.glob(outpath + "/*") if x.endswith(".csv")]
        for fl in files:
            df = pandas.read_csv(fl, sep="\t")
            for i in df["prediction"].unique():
                sub = df[df.prediction == i]
                out = outpath + "/cluster_" + str(i) + ".tsv"
                header = False if pathlib.Path(out).exists() else True
                sub.to_csv(out, sep="\t", mode="a", header=header, index=False)
        rm(files)
