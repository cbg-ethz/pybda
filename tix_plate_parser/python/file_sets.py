# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 23/09/16

import logging
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileSets:
    def __init__(self, folder):
        self._folder = folder
        self._plates = {}
        self.parse_file_names()

    def parse_file_names(self):
        fls = self.find_files(self._folder)
        for f in fls:
            classifier, pathogen, library, replicate, plate, cid, feature = \
                self.parse_plate_name(f)
            if classifier not in self._plates:
                self._plates[classifier] = PlateFileSet(classifier)

    def parse_plate_name(self, f):
        feature, f = self.match_and_sub(f, ".*/(.+mat?)$", 1)
        cid, f = self.match_and_sub(f, ".*/(\d+.\d+?)$", 1)
        _, f = self.match_and_sub(f, ".*/(.+?)$", 1)
        plate, f = self.match_and_sub(f, ".*/(\w+\d+.+?)$", 1)
        screen, _ = self.match_and_sub(f, ".*/(.+)$", 1)
        pathogen, library, replicate = screen.split("\t")
        classifier = "_".join([pathogen, library, replicate, plate, cid, feature])
        return classifier, pathogen, library, replicate, plate, cid, feature

    @staticmethod
    def find_files(folder):
        for d, s, f in os.walk(folder):
            for basename in f:
                if basename.endswith(".mat"):
                    yield os.path.join(d, basename)

    @staticmethod
    def match_and_sub(string, match, grp):
        ret = subs = ""
        try:
            ret = re.match(match, string).group(grp)
            subs = re.sub('/' + ret, '', string)
        except AttributeError or IndexError:
            logger.warn("Could not match string: %s", string)
        return ret, subs


class PlateFileSet:
    def __init__(self, classifier):
        self._classifier = classifier
        self._outfile = self._folder + "/matrix.tsv"
        self._files = self.find_files(self._folder)

class PlateFile: