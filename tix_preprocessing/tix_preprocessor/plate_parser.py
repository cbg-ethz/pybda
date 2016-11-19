# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 17/11/16


import logging

import numpy

from .plate_file_set_generator import PlateFileSet
from .utility import load_matlab
from ._plate_sirna_gene_mapping import PlateSirnaGeneMapping
from ._plate_cell_features import PlateCellFeature

logger = logging.getLogger(__name__)


class PlateParser:
    # meta information header for a single cell
    _meta_ = ["pathogen", "library_vendor", "library_type", "screen",
              "replicate", "plate", "sirna", "gene",
              "well", "welltype", "image", "cell_number"]

    def parse(self, platefileset):
        """
        Parse the PlateFileSets (i.e.: all parsed folders) into tsvs.

        Iterate over the file sets and create matrices every platefileset
        represents a plate so every platefileset is a single file

        """

        if not isinstance(platefileset, PlateFileSet):
            logger.error("Please provide a PlateFileSets object.")
            return
        # parse the feates to np arrays
        features = self._parse_plate_file_set(platefileset)
        if len(features) == 0:
            return
        for k, v in features.items():
            for l in v:
                print(k, v, l)
        exit(1)
        # load the mapping file for the wells
        mapping = self._parse_plate_mapping(platefileset)
        if len(mapping) == 0:
            logger.warn("Mapping is none for plate-fileset: " +
                        platefileset.classifier + ". Continuing to next set!")
            return
        self._integrate_platefileset(platefileset, features, mapping)
        # todo
        # platefilesets.remove()
        return 0

    def _parse_plate_file_set(self, plate_file_set):
        features = {}
        logger.info("Parsing plate file set to memory: " +
                    str(plate_file_set.classifier))
        for plate_file in plate_file_set:
            cf = self._parse_file(plate_file)
            if cf is None:
                continue
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
        if file is None:
            logger.warn("Could not parse: %s", file)
            return None
        matrix = None
        try:
            matrix = self._alloc(load_matlab(file), file, featurename)
        except ValueError or TypeError or AssertionError:
            logger.warn("Could not parse: %s", file)
        return matrix

    def _alloc(self, arr, file, featurename):
        """
        Create a Cell feature object from a matlab binary.

        :param arr: the matrix object
        :param file: the filename of the matlab binary
        :param featurename: the name of the feature
        :return: return a plate cell feature
        """
        featurename = str(featurename)
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
            logger.warn("Could not alloc feature %s of %s", featurename, file)
        return None

    def _add(self, features, cf):
        """
        Add a cell feature to a feature map

        :param features: the feature map
        :param cf: the cell feature object
        """
        # TODO: is this really enough?
        # this has to be changed for FEATURE TYPES
        # maybe compare all cell numbers and not only the max cell number
        max_cells = str(cf.max_cells)
        if max_cells not in features:
            features[max_cells] = []
        features[max_cells].append(cf)

    def _parse_plate_mapping(self, plate_file_set):
        logger.info("Loading meta for plate file set: " + str(
            plate_file_set.classifier))
        mapp = PlateSirnaGeneMapping(plate_file_set)
        return mapp

    def _integrate_platefileset(self, platefileset, features, mapping):
        """
        Iterate over all matlab files and create the final matrices

        :param platefileset: the platefile set
        :param features: the parses feature map

        """
        logger.info("Integrating the different feature sets to matrices for "
                    "plate file set: " + str(platefileset.classifier))
        # since some features have different numbers of calls
        for k, v in features.items():
            self._integrate_feature(platefileset, k, v, mapping)
            return 0

    def _integrate_feature(self, platefileset, max_ncells, features, mapping):
        features = sorted(features, key=lambda x: x.featurename.lower())
        filename = platefileset.outfile + "_max_nit_" + max_ncells + ".tsv"
        pathogen = platefileset.pathogen
        library = platefileset.library
        replicate = platefileset.replicate
        screen = platefileset.screen
        plate = platefileset.plate
        library_vendor, library_type = list(library)
        layout = self._layout.get(pathogen, library, screen,
                                  replicate, plate)
        if layout is None:
            logger.warn("Could not load layout for: " + platefileset.classifier)
            return
        logger.info("Writing to: " + filename)
        with open(filename, "w") as f:
            header = PlateParser._meta_ + \
                     [feat.featurename.lower() for feat in features]
            f.write("\t".join(header) + "\n")
            nimg = features[0].values.shape[0]
            assert nimg == len(mapping)
            for iimg in range(nimg):
                well = mapping[iimg]
                for cell in range(features[0].ncells[iimg]):
                    vals = [features[p].values[iimg, cell] for p in
                            range(len(features))]
                    meta = [pathogen, library_vendor, library_type, screen,
                            replicate, plate, layout.sirna(well),
                            layout.gene(well), well, layout.welltype(well),
                            iimg + 1, cell + 1]
                    f.write("\t".join(list(map(str, meta)) +
                                      list(map(str, vals))).lower() + "\n")
        return 0
