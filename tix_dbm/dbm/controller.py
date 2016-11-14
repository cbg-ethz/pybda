# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16


import logging
import os
import re

logging.basicConfig(format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

__skippable_features__ = [x.lower() for x in
                          ["comet", "image", "dapif", "neighbors"]]


class Controller:
    def __init__(self):
        self._data_base_headers = {}
        self._data_bases = {}

    def create(self, folder):
        for f in self._find_files(folder):
            self._add_file(f)
        print(self._data_base_headers.keys())
        print(self._data_bases.keys())

    def query(self, query):
        pass

    def _find_files(self, folder):
        for d, _, f in os.walk(folder):
            for b in f:
                if b.endswith(".mat"):
                    yield os.path.join(d, b)

    def _add_file(self, filename):
        toks = filename.strip().lower().split("/")
        try:
            org, feature = toks[-1].replace(".mat", "").split(".")
            if self._skip(toks[-1]):
                return
            screen, plate = self._screen_name(filename)
            self._add(self._data_base_headers, org, feature)
            self._add(self._data_bases, screen, plate)
        except ValueError:
            logger.warn("Could not feature: " +
                        str(toks[-1].replace(".mat", "")))

    def _skip(self, feature):
        for x in __skippable_features__:
            if feature.startswith(x):
                return True
        return False

    def _screen_name(self, f):
        ret = re.match("/.*/(.*)/(.*)/.*/.*/.+mat?$", f)
        return ret.group(1), ret.group(2)

    def _add(self, db, k, v):
        if k not in db:
            db[k] = []
        db[k].append(v)
