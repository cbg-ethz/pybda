# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 23/09/16

import logging
import os
import re
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileSets:
    def __init__(self, folder):
        self._plates = {}
        self.parse_file_names(folder)
        for k, v in self._plates.items():
            print(k, " ", v, len(v.files), v.sample(5))

    def parse_file_names(self, folder):
        fls = self.find_files(folder)
        for f in fls:
            classifier, pathogen, library, replicate, \
            plate, cid, feature, fileprefix = self.parse_plate_name(f)
            if classifier not in self._plates:
                outfile = fileprefix + "/" + classifier + ".tsv"
                self._plates[classifier] = \
                    PlateFileSet(classifier, outfile, pathogen, library,
                                 replicate, plate, cid)
            self._plates[classifier].files.append(PlateFile(f, feature))

    @staticmethod
    def find_files(folder):
        for d, s, f in os.walk(folder):
            for basename in f:
                if basename.endswith(".mat"):
                    yield os.path.join(d, basename)

    def parse_plate_name(self, f):
        filename = f
        feature, f = self.match_and_sub(f, ".*/(.+mat?)$", 1, filename)
        cid, f = self.match_and_sub(f, ".*/(\d+.\d+?)$", 1, filename)
        _, f = self.match_and_sub(f, ".*/(.+?)$", 1, filename)
        plate, f = self.match_and_sub(f, ".*/(\w+\d+.+?)$", 1, filename)
        screen, f = self.match_and_sub(f, ".*/(.+)$", 1, filename)
        pathogen, library, replicate = screen.split("-")[0:3]
        classifier = "_".join([pathogen, library, replicate, plate, cid])
        return classifier, pathogen, library, replicate, plate, cid, feature, f

    @staticmethod
    def match_and_sub(string, match, grp, filename):
        ret = subs = ""
        try:
            ret = re.match(match, string).group(grp)
            subs = re.sub('/' + ret, '', string)
        except AttributeError or IndexError:
            logger.warn("Could not match string %s in file %s", string,
                        filename)
        return ret, subs


class PlateFileSet:
    def __init__(self, classifier, outfile, pathogen,
                 library, replicate, plate, cid):
        self._classifier = classifier
        self._outfile = outfile
        self._pathogen = pathogen
        self._library = library
        self._replicate = replicate
        self._plate = plate
        self._cid = cid
        self._files = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "\t".join([self._pathogen, self._library, self._replicate,
                          self._plate, self._cid])

    def sample(self, cnt):
        return random.sample(self._files, cnt)

    @property
    def files(self):
        return self._files


class PlateFile:
    """
    Class that stores the feature name and the absolute filename.

    """

    def __init__(self, filename, feature):
        self._filename = filename
        self._feature = feature

    @property
    def filename(self):
        return self._filename

    @property
    def featurename(self):
        return self._feature

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self._feature
