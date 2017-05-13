# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 08.05.17

import logging
import os
import pandas

from tix_query.tix_query.globals import WELL, GENE, SIRNA, SAMPLE
from tix_query.tix_query.io import IO

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class ResultSet:
    _filter_attributes_ = [GENE, SIRNA, WELL, SAMPLE]

    def __init__(self, files, sample, **kwargs):
        self._tablefile_set = files
        self._sample = sample
        self._filters = self._set_filter(**kwargs)
        self._lambda_filter = lambda x: all(f in x for f in self._filters)

    def dump(self, fh=None):
        with IO(fh) as handle:
            for tablefile in self._tablefile_set:
                self._dump(handle, tablefile)

    def _dump(self, handle, tablefile):
        if os.path.isfile(tablefile.filename):
            with open(tablefile.filename, "r") as fh:
                lines = filter(self._lambda_filter, fh.readlines())
                for line in lines:
                    # todo sampling
                    # maybe with pandas and group by
                    handle.print(line)
        else:
            logger.warning("Could not find file: {}".format(tablefile))

    def _set_filter(self, **kwargs):
        fls = []
        for k, v in kwargs.items():
            if k in ResultSet._filter_attributes_:
                self.__setattr__("_" + k, v)
                fls.append(v)
        return fls
