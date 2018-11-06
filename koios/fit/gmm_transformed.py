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


import glob
import logging
import pathlib

import pandas
from pyspark.sql.functions import col

from koios.fit.clustering_transformed import ClusteringTransformed
from koios.globals import FEATURES__, RESPONSIBILITIES__
from koios.io.io import rm
from koios.spark.features import split_vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMMTransformed(ClusteringTransformed):
    def __init__(self, data):
        super().__init__(data)

    def _write(self, outfolder, suff="", sort_me=True):
        import os
        if not os.path.exists(outfolder):
            os.mkdir(outfolder)
        self._write_components(outfolder + "-components" + str(suff))

    def _write_components(self, outpath, sort_me=True):
        logger.info("Writing components to: {}".format(outpath))
        data = split_vector(self.__data, FEATURES__)
        data = split_vector(data, RESPONSIBILITIES__)
        if sort_me:
            data = data.sort(col('prediction'))
        data.write.csv(path=outpath, sep='\t', mode='overwrite', header=True)
        files = [x for x in glob.glob(outpath + "/*") if x.endswith(".csv")]
        for fl in files:
            df = pandas.read_csv(fl, sep="\t")
            for i in df["prediction"].unique():
                sub = df[df.prediction == i]
                out = outpath + "/component_" + str(i) + ".tsv"
                ind = False if pathlib.Path(out).exists() else True
                sub.to_csv(out, sep="\t", mode="a", header=False, index=ind)
        rm(files)

