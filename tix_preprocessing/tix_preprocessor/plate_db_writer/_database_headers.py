# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16

import os
import logging

from tix_preprocessor.utility import parse_plate_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
__skippable_features__ = [x.lower() for x in
                          ["comet", "image", "dapif", "neighbors", "expanded"]]


class DatabaseHeaders:
    def __init__(self, folder):
        self.__folder = folder
        self._feature_type_name_map = {}
        self._screen_plate_map = {}
        self._get_headers()

    def _get_headers(self):
        for f in self._find_files(self.__folder):
            self._add_file(f)

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
            screen, plate = parse_plate_info(filename)
            self._add(self._feature_type_name_map, org, feature)
            self._add(self._screen_plate_map, screen, plate)
        except ValueError:
            logger.warn("Could not feature: " +
                        str(toks[-1].replace(".mat", "")))

    def _skip(self, feature):
        for x in __skippable_features__:
            if feature.startswith(x):
                return True
        return False

    def _add(self, db, k, v):
        if k not in db:
            db[k] = set()
        db[k].add(v)

    @property
    def feature_types(self):
        return self._feature_type_name_map.items()

    @property
    def screens(self):
        return self._screen_plate_map.items()
