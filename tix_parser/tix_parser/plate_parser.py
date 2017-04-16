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
    # meta information header for a single cell
    _meta_ = ["well", "gene", "sirna",
              "well_type", "image_idx", "object_idx"]
    _well_regex = re.compile("(\w)(\d+)")

    def __init__(self, layout):
        self._layout = layout

    def parse(self, platefileset):
        """
        Parse the PlateFileSets (i.e.: all parsed folders) into tsvs.

        Iterate over the file sets and create matrices every platefileset
        represents a plate so every platefileset is a single file

        """

        if not isinstance(platefileset, PlateFileSet):
            logger.error("Please provide a PlateFileSets object.")
            return
        features = self._parse_plate_file_set(platefileset)
        if len(features) == 0:
            return
        mapping = self._parse_plate_mapping(platefileset)
        if len(mapping) == 0:
            logger.warning("Mapping is none for plate-fileset: " +
                           platefileset.classifier + ". Continuing to next set!")
            return
        self._integrate_platefileset(platefileset, features, mapping)
        return 0

    def _parse_plate_file_set(self, plate_file_set):
        features = {}
        logger.info("Parsing plate file set to memory: " +
                    str(plate_file_set.classifier))
        k = 0
        for plate_file in plate_file_set:
            # TODO
            if k == 10:
                break
            k += 1
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
        """
        Create a Cell feature object from a matlab binary.

        :param arr: the matrix object
        :param file: the filename of the matlab binary
        :param featurename: the name of the feature
        :return: return a plate cell feature
        """
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
                             fill_value=numpy.nan,
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
                           featurename,
                           file)
        return None

    @staticmethod
    def _add(features, cf, feature_group):
        """
        Add a cell feature to a feature map

        :param features: the feature map
        :param cf: the cell feature object
        """
        # TODO: is this really enough?
        # this has to be changed for FEATURE TYPES
        # maybe compare all cell numbers and not only the max cell number
        if feature_group not in features:
            features[feature_group] = []
        features[feature_group].append(cf)

    @staticmethod
    def _parse_plate_mapping(plate_file_set):
        logger.info("Loading meta for plate file set: " +
                    str(plate_file_set.classifier))
        mapp = PlateSirnaGeneMapping(plate_file_set)
        return mapp

    def _integrate_platefileset(self, platefileset, features, mapping):
        """
        Iterate over all matlab files and create the final matrices

        :param platefileset: the platefile set
        :param features: the parsed feature map

        """
        logger.info("Integrating the different feature sets to matrices for "
                    "plate file set: " + str(platefileset.classifier))
        # since some features have different numbers of objects
        for k, v in features.items():
            self._integrate_feature(platefileset, k, v, mapping)
        return 0

    def _integrate_feature(self, pfs, feature_group, features,
                           mapping):
        features = sorted(features, key=lambda x: x.short_name)
        pathogen = pfs.pathogen
        library = pfs.library
        replicate = pfs.replicate
        screen = pfs.screen
        design = pfs.design
        study = pfs.study
        plate = pfs.plate
        suffix = pfs.suffix
        layout = self._layout.get(pathogen, library, design,
                                  screen, replicate, plate)
        if layout is None:
            logger.warning("Could not load layout for: " + pfs.classifier)
            return
        filename = pfs.outfile + "_" + feature_group
        self._write_file(filename, features, mapping, layout)

    @staticmethod
    def _write_file(filename, features, mapping, layout):
        meta = [None] * len(PlateParser._meta_)
        logger.info("Writing to: " + filename)
        with open(filename, "w") as f:
            header = PlateParser._meta_ + \
                     [feat.featurename.lower() for feat in features]
            f.write("\t".join(header) + "\n")
            nimg = features[0].values.shape[0]
            assert nimg == len(mapping)
            for iimg in range(nimg):
                well = mapping[iimg]
                meta[0] = well
                meta[1] = layout.gene(well)
                meta[2] = layout.sirna(well)
                meta[3] = layout.welltype(well)
                meta[4] = iimg + 1
                for cell in range(features[0].ncells[iimg]):
                    vals = [features[p].values[iimg, cell] for p in
                            range(len(features))]
                    meta[5] = cell + 1
                    f.write("\t".join(list(map(str, meta)) +
                                      list(map(str, vals))).lower() + "\n")
        return 0
