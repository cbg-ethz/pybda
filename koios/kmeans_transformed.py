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
import pathlib

from pyspark.sql.functions import col

from koios.io.io import write_parquet
from koios.util.features import split_vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeansTransformed:
    def __init__(self, data):
        self.__data = data

    def write_files(self, outfolder):
        import os
        if not os.path.exists(outfolder):
            os.mkdir(outfolder)
        write_parquet(self.__data, outfolder)
        self._write_clusters(outfolder)

    @staticmethod
    def _write_clusters(data, outfolder, suff="", sort_me=True):
        outpath = outfolder + "-clusters" + str(suff)
        if not pathlib.Path(outpath).exists():
            pathlib.Path(outpath).mkdir()
        data = split_vector(data, "features")

        logger.info("Writing clusters to: {}".format(outpath))
        if sort_me:
            data.sort(col('prediction')).write.csv(
              path=outpath, sep='\t', mode='overwrite', header=True)
        else:
            data.write.csv(path=outpath, sep='\t', mode='overwrite', header=True)
