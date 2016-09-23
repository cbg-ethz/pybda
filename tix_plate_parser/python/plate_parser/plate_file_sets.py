# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 23/09/16

import logging
import os
import re
from ._plate_file import PlateFile
from ._plate_file_set import PlateFileSet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateFileSets:
    def __init__(self, folder):
        self._plates = {}
        self._parse_file_names(folder)

    def __iter__(self):
        for _k, v in self._plates.items():
            yield v

    def _parse_file_names(self, folder):
        fls = self._find_files(folder)
        for f in fls:
            classifier, pathogen, library, replicate, \
            plate, cid, feature, fileprefix = self._parse_plate_name(f)
            if classifier not in self._plates:
                outfile = fileprefix + "/" + classifier + ".tsv"
                self._plates[classifier] = \
                    PlateFileSet(classifier, outfile, pathogen, library,
                                 replicate, plate, cid)
            self._plates[classifier].files.append(PlateFile(f, feature))

    @staticmethod
    def _find_files(folder):
        leave_out_image = ".+/(Image.+.mat?)$"
        for d, s, f in os.walk(folder):
            for basename in f:
                if basename.endswith(".mat"):
                    # this tests if the feature file is image related
                    nma = re.match(leave_out_image, basename)
                    # if the regex returns none, the featue does not contain
                    # image
                    if basename.startswith("Image."):
                        continue
                    if basename.startswith("Batch_handles."):
                        continue
                    if nma is not None:
                        continue
                    if nma is not None and nma.group() is None:
                        continue
                    yield os.path.join(d, basename)

    def _parse_plate_name(self, f):
        filename = f
        feature, f = self._match_and_sub(f, ".*/(.+mat?)$", 1, filename)
        cid, f = self._match_and_sub(f, ".*/(\d+.\d+?)$", 1, filename)
        _, f = self._match_and_sub(f, ".*/(.+?)$", 1, filename)
        plate, f = self._match_and_sub(f, ".*/(\w+\d+.+?)$", 1, filename)
        screen, f = self._match_and_sub(f, ".*/(.+)$", 1, filename)
        pathogen, library, replicate = screen.split("-")[0:3]
        classifier = "_".join([pathogen, library, replicate, plate, cid])
        return classifier, pathogen, library, replicate, plate, cid, feature, f

    @staticmethod
    def _match_and_sub(string, match, grp, filename):
        ret = subs = ""
        try:
            ret = re.match(match, string).group(grp)
            subs = re.sub('/' + ret, '', string)
        except AttributeError or IndexError:
            logger.warn("Could not match string %s in file %s", string,
                        filename)
        return ret, subs
