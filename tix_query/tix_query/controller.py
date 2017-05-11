# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


import logging

from tix_query.tix_query.filesets import table_file_sets
from tix_query.tix_query.result_set import ResultSet

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

logger = logging.getLogger(__name__)


class Controller:
    _features_ = "features"
    _elements_ = "elements"
    _sample_ = "sample"

    def __init__(self):
        # filesets of meta files
        self._table = table_file_sets.TableFileSets()

    def query(self, sample=None, **kwargs):
        """
        Get a lazy file result set from some filtering criteria and a fixed 
        sample size.
        
        :param sample: the number of objects to sample 
         (i.e. bacteria/cells/nuclei/...)
        :param kwargs: the filtering criteria. 
        :return: 
        """
        fls = self._table.filter(**kwargs)
        return ResultSet(fls, sample, **kwargs)
