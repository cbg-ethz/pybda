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


class PlateFileSetParser:
    """
    Class for keeping all the filenames of plates stored as a map.

    """
    # these are feature file names we dont use
    _skippable_features = ["Batch_handles.", "Neighbors.",
                           "Bacteria.SubObjectFlag.", "CometTails.",
                           "DAPIFG.", "BlobBacteria.", "ExpandedNuclei."]
    # name of the file that has the sirna-entrez mapping information
    _se_map = "Image.FileName_OrigDNA.mat".lower()
    # the pattern for screen, replicate
    _setting_pattern = "(\w+)(\d+)"

    def __init__(self, folder, outfile):
        self._setting_regex = re.compile(PlateFileSetParser._setting_pattern)
        self._folder = folder
        self._plates = {}
        self._outfile = outfile
        self._files = []
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
            if self._skip_feature(basename):
                continue
            if basename.startswith("Image.") and \
                    not basename.startswith(
                        "Image.FileName_OrigDNA"):
                continue
            # decompose the file name
            classifier, pathogen, library, screen, replicate, \
            plate, cid, feature, fileprefix = self._parse_plate_name(f)
            # add the (classifier-platefileset) pair to the plate map
            self._add(classifier, pathogen, library, screen,
                      replicate, plate, cid, self._outfile)
            # add the current matlab file do the respective platefile
            if feature.lower() == PlateFileSetParser._se_map:
                self._plates[classifier].mapping = PlateFile(f, feature)
            else:
                self._plates[classifier].files.append(PlateFile(f, feature))

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
        for skip in PlateFileSetParser._skippable_features:
            if basename.startswith(skip):
                return True
        return False

    def _parse_plate_name(self, f):
        """
        Decompose a filename into several features names.

        :param f: the file name
        :return: returns a list of feature names
        """

        filename = f
        feature, f = self._match_and_sub(f, ".*/(.+mat?)$", 1, filename)
        cid, f = self._match_and_sub(f, ".*/(\d+.\d+?)$", 1, filename)
        # remove HCS_ANALYSIS_CELL_FEATURES_CC_MAT string
        _, f = self._match_and_sub(f, ".*/(.+?)$", 1, filename)
        plate, f = self._match_and_sub(f, ".*/(.+)$", 1, filename)
        exper, f = self._match_and_sub(f, ".*/(.+)$", 1, filename)
        pathogen, library, sett = exper.split("-")[0:3]
        mat = self._setting_regex.match(sett)
        screen, replicate = mat.group(1), mat.group(2)
        team, f = self._match_and_sub(f, ".*/(.+)$", 1, filename)
        src, f = self._match_and_sub(f, ".*/(.+)$", 1, filename)
        classifier = "_".join([src, team, pathogen, library, sett,
                               plate,
                               cid])
        return classifier, pathogen, library, screen, replicate, plate, cid, \
               feature, f

    @staticmethod
    def _match_and_sub(string, match, grp, filename):
        ret = subs = ""
        try:
            ret = re.match(match, string).group(grp)
            subs = re.sub('/' + ret, '', string)
        except AttributeError or IndexError:
            logger.warn("Could not match string %s in file %s against %s",
                        string, filename, match)
        return ret, subs

    def _add(self, classifier, pathogen, library, screen,
             replicate, plate, cid, outfile):
        if classifier not in self._plates:
            self._plates[classifier] = \
                PlateFileSet(classifier, outfile + '/' + classifier,
                             pathogen, library, screen,
                             replicate, plate, cid)
