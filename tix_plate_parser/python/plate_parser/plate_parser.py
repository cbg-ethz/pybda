# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

import logging
import numpy
import scipy.io as spio
from .cell_features import CellFeature

from plate_parser.plate_file_sets import PlateFileSets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateParser:
    """
    Class for parsing a folder of plates containing matlab files for the
    features.

    """

    def __init__(self, folder, experiment_meta, layout_meta):
        """
        Constructor for PlateParser.

        :param folder: folder containing all the plate data
        :param experiment_meta: parsed experiment meta information (i.e. the
        plates you want to parse)
        :param layout_meta: parsed layout meta files (i.e. the sirna-gene
        mappings)
        """
        self._folder = folder
        # parse the folder into a map of (classifier-plate) pairs
        self._plate_file_sets = PlateFileSets(self._folder)
        # TODO: incorporate meta info to the files
        self._experiment_meta = experiment_meta
        self._layout_meta = layout_meta

    def parse(self):
        """
        Iterate over the experiments, download the files, parse them and
        store to tsv.

        """
        # TODO downloader here
        for plate in self._experiment_meta:
            print(plate)

    def _parse_plate_file_sets(self):
        """
        Parse the PlateFileSets (i.e.: all parsed folders) into tsvs.

        """
        # iterate over the file sets and create matrices
        # every platefileset represents a plate
        # so every platefileset is a single file
        for platefileset in self._plate_file_sets:
            features = self._parse_plate_file_set(platefileset)
            self._integrate_platefileset(platefileset._outfile, features)

    def _parse_plate_file_set(self, plate_file_set):
        # feature map: there is a chance that different features
        # have a different set of cells
        features = {}
        logger.info("Doing: " + str(plate_file_set.classifier))
        logger.info("\t#Features: " + str(len(plate_file_set)))
        for plate_file in plate_file_set:
            cf = self._parse_file(plate_file)
            if cf is None:
                continue
            logger.info("\tFile: " + str(plate_file) + " -> max cells:" +
                        str(cf.max_cells))
            self._add(features, cf)
        return features

    def _parse_file(self, plate_file):
        """
        Parse a matlab binary as np.array

        :param plate_file: the matlab file
        :return: returns a 2D np.array
        """
        featurename = plate_file.featurename
        file = plate_file.filename
        matrix = None
        try:
            matlab_matrix = (spio.loadmat(file))
            matrix = \
                self._alloc(
                    matlab_matrix["handles"][0][0][0][0][0][0][0][0][0][0],
                    file, featurename)
        except ValueError or TypeError or AssertionError:
            logger.warn("Could not parse: %s", file)
        return matrix

    def _alloc(self, arr, file, featurename):
        """
        Create a Cell feature object from a matlab binary.

        :param arr: the matrix object
        :param file: the filename of the matlab binary
        :param featurename: the name of the feature
        :return:
        """
        try:
            # number of images on the plate (usually 9 * 384)
            nrow = len(arr)
            # number of cells per image
            rowlens = [len(x) for x in arr]
            # maximum number of cells
            m_ncol = max(rowlens)
            # initialize empty matrix of NaNs
            mat = numpy.full(shape=(nrow, m_ncol), fill_value=numpy.nan,
                             dtype="float64")
            # fill matrix
            for i in range(len(arr)):
                row = arr[i]
                for j in range(len(row)):
                    mat[i][j] = row[j]
            return CellFeature(mat, nrow, m_ncol, file, rowlens, featurename)
        except AssertionError:
            logger.warn("Could not alloc feature %s of %s", featurename, file)
        return None

    def _add(self, features, cf):
        """
        Add a cell feature to a feature map

        :param features: the feature map
        :param cf: the cell feature object
        """
        # TODO: is this really enough?
        # maybe compare all cell numbers and not only the max cell number
        max_cells = str(cf.max_cells)
        if max_cells not in features:
            features[max_cells] = []
        features[max_cells].append(cf)

    def _integrate_platefileset(self, classifier, features):
        """
        Iterate over all matlab files and create the final matrices

        :param classifier: classifier for the current plate
        :param features: the parses feature map

        """
        logger.info("Integrating the different features to a single matrix")
        # since some features have different numbers of calls
        for k, v in features.items():
            self._integrate_feature(classifier, k, v)

    @staticmethod
    def _integrate_feature(outfile, max_ncells, features):
        filename = outfile + "_max_nit_" + max_ncells + ".tsv"
        logger.info("Writing to: " + filename)
        with open(filename, "w") as f:
            # write the feature names
            f.write("\t".join([feat.featurename for feat in features]) + "\n")
            # iterate over the different images
            # number of images per plate (should be 9 * 384)
            nimg = features[0].values.shape[0]
            for iimg in range(nimg):
                # number of cells in the iimg-th image
                cell_vals = features[0].values[iimg]
                #ncells = cell_vals.shape[0]
                ncells = features[0].ncells[iimg]
                # iterate over all the cells
                for cell in range(ncells):
                    # iterate over a single cell's feature
                    vals = [features[p].values[iimg, cell] for p in
                            range(len(features))]
                    f.write("\t".join(map(str, vals)) + "\n")
