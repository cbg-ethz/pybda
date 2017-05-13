# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 08.05.17


import logging
import os

import numpy as np
import pandas

from tix_query.tix_query.globals import WELL, GENE, SIRNA, SAMPLE

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


def mask(df, key, value):
    return df[df[key] == value]
pandas.DataFrame.mask = mask

class ResultSet:
    _filter_attributes_ = [GENE, SIRNA, WELL, SAMPLE]
    _sar_ = ".*"

    def __init__(self, files, sample, **kwargs):
        self._tablefile_set = files
        self._sample = sample
        self._filters = self._set_filter(**kwargs)

    def dump(self, fh=None):
            for i, tablefile in enumerate(self._tablefile_set):
                self._dump(fh, i, tablefile)

    def _dump(self, fh, i, tablefile):
        if os.path.isfile(tablefile.filename):
            data = pandas.read_csv(tablefile.filename, sep="\t", header=0)
            data = data[
                data.well.str.contains(self.__getattribute__("_" + WELL)) &
                data.gene.str.contains(self.__getattribute__("_" + GENE)) &
                data.sirna.str.contains(self.__getattribute__("_" + SIRNA))
            ]
            if self.__getattribute__("_" + SAMPLE) != ResultSet._sar_:
                sample = self.__getattribute__("_" + SAMPLE)
                print("taking samplie", sample)
                fn = lambda obj: obj.loc[np.random.choice(obj.index, sample, False), :]
                data.groupby([WELL, GENE, SIRNA]).apply(fn)
            if i == 0:
                data.to_csv(fh, sep="\t", mode="a")
            else:
                data.to_csv(fh, sep="\t", mode="a", header=False)
        else:
            logger.warning("Could not find file: {}".format(tablefile))

    def _set_filter(self, **kwargs):
        fls = []
        for k, v in kwargs.items():
            if k in ResultSet._filter_attributes_:
                if v is not None:
                    self.__setattr__("_" + k, v)
                else:
                    self.__setattr__("_" + k, ResultSet._sar_)
                fls.append(v)
        return fls
