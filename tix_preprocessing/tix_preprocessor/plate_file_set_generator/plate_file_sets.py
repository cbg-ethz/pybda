# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 23/09/16

import logging
import os
import re

from tix_preprocessor.utility import parse_plate_info, regex
from tix_preprocessor.utility import parse_screen_details
from ._plate_file import PlateFile
from ._plate_file_set import PlateFileSet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateFileSets:
    """
    Class for keeping all the filenames of plates stored as a map.

    """
    # these are feature file names we dont use
    _skippable_features_starts = ["Batch_handles.", "Neighbors.",
                                  "Bacteria.SubObjectFlag.", "CometTails.",
                                  "DAPIFG.", "BlobBacteria.", "ExpandedNuclei."]
    _skippable_features_contains = ["SubObjectFlag"]
    # name of the file that has the sirna-entrez mapping information
    _se_map = "Image.FileName_OrigDNA.mat".lower()
    _image_ = "Image."
    _mapping_file_ = "Image.FileName_OrigDNA"
    # the pattern for screen, replicate
    _setting_pattern = "(\w+)(\d+)"
    _

    def __init__(self, folder, outfolder):
        self._setting_regex = re.compile(PlateFileSets._setting_pattern)
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
        # iterate over this array
        for basename, f in self._find_files(folder):
            self._files.append(f)
            if self._skip(basename):
                continue
            # decompose the file name
                classifier, st, pa, lib, des, scr, rep, suf, plate, feature\
                    = self._parse_plate_name(f)
            # add the (classifier-platefileset) pair to the plate map
            self._add_platefileset(clss, path, lib, scr,
                                   rep, plt, cid, self._outfolder)
            self._add_platefile(f, feat, clss)

    def _add_platefile(self, f, feature, classifier):
        # matlab file is the well mapping
        if feature.lower() == PlateFileSets._se_map:
            self._plates[classifier].mapping = PlateFile(f, feature)
        # add the current matlab file do the respective platefile
        else:
            self._plates[classifier].files.append(PlateFile(f, feature))

    def _skip(self, basename):
        if self._skip_feature(basename):
            return True
        if basename.startswith(PlateFileSets._image_) and \
                not basename.startswith(PlateFileSets._mapping_file_):
            return True
        return False

    @staticmethod
    def _find_files(folder):
        """
        Traverse the folder and return all relevant matlab files

        :param folder: the folder for which all the plates should get parsed
        :return: returns a list of matlab files
        """
        for d, s, f in os.walk(folder):
            for basename in f:
                if basename.endswith(".mat"):
                    yield basename, os.path.join(d, basename)

    @staticmethod
    def _skip_feature(basename):
        for skip in PlateFileSets._skippable_features_starts:
            if basename.startswith(skip):
                return True
        return False

    def _parse_plate_name(self, f):
        """
        Decompose a filename into several features names.

        :param f: the file name
        :return: returns a list of feature names
        """
        f = f.strip().lower()
        screen, plate = parse_plate_info(f)
        st, pa, lib, des, scr, rep, suf  = parse_screen_details(screen)
        feature = (f.split("/")[-1]).replace(".mat", "")
        if suf != regex.__NA__:
            classifier = "-".join([st, pa, lib, des, scr, rep, suf, plate])
        else:
            classifier = "-".join([st, pa, lib, des, scr, rep, plate])
        return classifier, st, pa, lib, des, scr, rep, suf, plate, feature


    def _add_platefileset(self, classifier, pathogen, library,
                          screen, replicate, plate, cid, outfolder):
        if classifier not in self._plates:
            self._plates[classifier] = \
                PlateFileSet(classifier, outfolder + '/' + classifier,
                             pathogen, library, screen,
                             replicate, plate, cid)
