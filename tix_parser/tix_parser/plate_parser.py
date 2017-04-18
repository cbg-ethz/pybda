# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 17/11/16


import re
import logging
import numpy

from .plate_file_set_generator import PlateFileSet
from .utility import load_matlab
from ._plate_sirna_gene_mapping import PlateSirnaGeneMapping
from ._plate_cell_features import PlateCellFeature

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

__NA__ = "NA"


class PlateParser:
    def parse(self, pfs):
        """
        Parse the PlateFileSets (i.e.: all parsed folders) into tsvs.

        Iterate over the file sets and create matrices every platefileset
        represents a plate so every platefileset is a single file.
        """

        if not isinstance(pfs, PlateFileSet):
            logger.error("Please provide a PlateFileSets object.")
            return None, None, None
        features = self._parse_plate_file_set(pfs)
        if len(features) == 0:
            return None, None, None
        mapping = self._parse_plate_mapping(pfs)
        if len(mapping) == 0:
            logger.warning("Mapping is none for plate-fileset: " +
                           pfs.classifier + ". Continuing to next set!")
            return None, None, None
        return pfs, features, mapping

    def _parse_plate_file_set(self, plate_file_set):
        features = {}
        logger.info("Parsing plate file set to memory: " +
                    str(plate_file_set.classifier))
        for plate_file in plate_file_set:
            cf = self._parse_file(plate_file)
            if cf is None:
                continue
            self._add(features, cf, cf.feature_group)
        return features

    def _parse_file(self, plate_file):
        """
        Parse a matlab binary as np.array

        :param plate_file: the matlab file
        :return: returns a 2D np.array
        """
        featurename = plate_file.featurename
        file = plate_file.filename
        if file is None:
            logger.warning("Could not parse: %s", file)
            return None
        matrix = None
        try:
            matrix = self._alloc(load_matlab(file), file, featurename)
        except ValueError or TypeError or AssertionError:
            logger.warning("Could not parse: %s", file)
        return matrix

    @staticmethod
    def _alloc(arr, file, featurename):
        featurename = str(featurename).lower()
        if featurename.endswith(".mat"):
            featurename = featurename.replace(".mat", "")
        try:
            # number of images on the plate (usually 9 * 384)
            nrow = len(arr)
            # number of cells per image
            rowlens = [len(x) for x in arr]
            # maximum number of cells
            m_ncol = max(rowlens)
            # initialize empty matrix of NaNs
            mat = numpy.full(shape=(nrow, m_ncol),
                             fill_value=numpy.Infinity,
                             dtype="float64")
            # fill matrix
            for i in range(len(arr)):
                row = arr[i]
                for j in range(len(row)):
                    mat[i][j] = row[j]
            return PlateCellFeature(mat, nrow, m_ncol, file, rowlens,
                                    featurename)
        except AssertionError:
            logger.warning("Could not alloc feature %s of %s",
                           featurename, file)
        return None

    @staticmethod
    def _add(features, cf, feature_group):
        # TODO: is this really enough?
        if feature_group not in features:
            features[feature_group] = []
        features[feature_group].append(cf)

    @staticmethod
    def _parse_plate_mapping(pfs):
        logger.info("Loading meta for plate file set: " + str(pfs.classifier))
        return PlateSirnaGeneMapping(pfs)

