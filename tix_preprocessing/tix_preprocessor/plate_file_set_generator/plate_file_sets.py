# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 23/09/16

import logging
import os
import re

from tix_preprocessor.utility import parse_plate_info, regex
from tix_preprocessor.utility import parse_screen_details
from ._plate_file import PlateFile
from .plate_file_set import PlateFileSet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateFileSets:
    """
    Class for keeping all the filenames of plates stored as a map.

    """
    _feature_names_ = ["Batch_handles.", "Neighbors.", "Bacteria.SubObjectFlag.",
                       "CometTails.", "DAPIFG.", "BlobBacteria.", "ExpandedNuclei."]
    # these are feature file names we dont use
    _skippable_features_starts = [x.lower() for x in _feature_names_]
    # skip the features that contain on of those strings
    _skippable_features_contains = ["SubObjectFlag".lower()]
    # name of the file that has the sirna-entrez mapping information
    _image_ = "Image.".lower()
    # name of the well index mappings
    _mapping_file_ = "Image.FileName_OrigDNA".lower()
    # the pattern for screen, replicate
    _setting_pattern_ = "(\w+)(\d+)"

    def __init__(self, folder, outfolder):
        self._setting_regex = re.compile(PlateFileSets._setting_pattern_)
        self._folder = folder
        self._plates = {}
        self._files = []
        self._outfolder = outfolder
        self._parse_file_names(folder)

    def __iter__(self):
        """
        Iterate over all the single plates.

        """
        for _, v in self._plates.items():
            yield v

    def __len__(self):
        return len(self._plates)

    def remove(self):
        """
        Remove the plate file set from the disc.

        """
        logger.info("Removing plate-file sets")
        from subprocess import call
        for f in self._files:
            if f.endswith(".mat"):
                call(["rm", f])

    def _parse_file_names(self, folder):
        """
        Traverse the given folder structure and save every
        (classifier-folder) pair in a plate map.

        :param folder: the folder for which all the plates should get parsed
        """
        # iterate over the array of files
        for basename, filename in self._find_files(folder):
            self._files.append(filename)
            if self._skip(basename):
                continue
                # decompose the file name
            self._parse_file_name(filename)

    def _parse_file_name(self, filename):
        clss, st, pa, lib, des, scr, rep, suf, plate, feature \
            = self._parse_plate_name(filename)
        self._add_platefileset(clss, st, pa, lib, des, scr,
                               rep, suf, plate, self._outfolder)
        self._add_platefile(filename, feature, clss)

    def _skip(self, basename):
        b = basename.lower()
        if self._skip_feature(b):
            return True
        if b.startswith(PlateFileSets._image_) and \
                not b.startswith(PlateFileSets._mapping_file_):
            return True
        return False

    def _add_platefile(self, f, feature, classifier):
        # matlab file is the well mapping
        if feature.lower() == PlateFileSets._mapping_file_:
            self._plates[classifier].mapping = PlateFile(f, feature)
        # add the current matlab file do the respective platefile
        else:
            self._plates[classifier].files.append(PlateFile(f, feature))

    @staticmethod
    def _find_files(folder):
        """
        Traverse the folder and return all relevant matlab files

        :param folder: the folder for which all the plates should get parsed
        :return: returns a list of matlab files
        """
        for d, _, f in os.walk(folder):
            for basename in f:
                if basename.endswith(".mat"):
                    yield basename, os.path.join(d, basename)

    @staticmethod
    def _skip_feature(basename):
        b = basename.lower()
        for skip in PlateFileSets._skippable_features_starts:
            if b.startswith(skip):
                return True
        return False

    def _parse_plate_name(self, f):
        """
        Decompose a filename into several features names.

        :param f: the file name
        :return: returns a list of feature names
        """
        screen, plate = parse_plate_info(f.strip().lower())
        st, pa, lib, des, scr, rep, suf = parse_screen_details(screen)
        feature = (f.split("/")[-1]).replace(".mat", "")
        if suf != regex.__NA__:
            classifier = "-".join([st, pa, lib, des, scr, rep, suf, plate])
        else:
            classifier = "-".join([st, pa, lib, des, scr, rep, plate])
        return classifier, st, pa, lib, des, scr, rep, suf, plate, feature

    def _add_platefileset(self, classifier, study, pathogen, library, design,
                          screen, replicate, suffix, plate, outfolder):
        if classifier not in self._plates:
            self._plates[classifier] = \
                PlateFileSet(classifier, outfolder + '/' + classifier,
                             study, pathogen, library, design,
                             screen, replicate, suffix, plate)
