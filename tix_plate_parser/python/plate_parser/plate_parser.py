# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

import logging
import subprocess
import multiprocessing as mp

from .plate_experiment_meta import PlateExperimentMeta
from .plate_layout import PlateLayoutMeta
from ._plate_sirna_gene_mapping import PlateSirnaGeneMapping
from ._utility import parse_file
from .plate_file_set_parser import PlateFileSetParser

logger = mp.log_to_stderr()
logger.setLevel(logging.INFO)

lock, pool = None, None


class PlateParser:
    """
    Class for parsing a folder of plates containing matlab files for the
    features.

    """

    # meta information header for a single cell
    _meta = ["pathogen", "library_vendor", "library_type", "screen",
             "replicate",
             "plate", "sirna", "gene",
             "well", "welltype", "image", "cell_number"]

    def __init__(self, experiment_file, layout_file,
                 bee_loader, output_path, username, pw):
        """
        Constructor for PlateParser.

        :param experiment_meta: parsed experiment meta files
        :param layout_meta: parsed layout meta
        :param bee_loader: the full path with the script name that downloads
         the data (e.g. /bla/..../BeeDataSetDownloader.sh)
        :param output_path: the folder where all the plates get stored and
        parsed to
        :param username: the user name of the open bis instance
        :param pw: the password of the open bis instance
        """
        self._experiment_file = experiment_file
        self._layout_file = layout_file
        # parse the folder into a map of (classifier-plate) pairs
        self._experiment_meta = PlateExperimentMeta(experiment_file,
                                              ".*\/\w+\-\w[P|U]\-[G|K]\d+\/.*")
        self._layout_meta = PlateLayoutMeta(layout_file)
        self._bee_loader = bee_loader
        self._username = username
        self._pw = pw
        self._output_path = output_path
        self._downloader = PlateLoader(bee_loader, output_path, username, pw)

    def parse(self):
        """
        Iterate over the experiments, download the files, parse them and
        store to tsv.

        """
        global lock
        global pool
        lock = mp.Lock()
        pool = mp.Pool(mp.cpu_count() - 1)
        cnt = 0
        logger.info("Going parallel ...")
        for plate in self._experiment_meta:
            cnt += 1
            if cnt == 20:
                break
            pool.apply_async(func=self._parse, args=(plate,))
        pool.close()
        pool.join()

    def _parse(self, plate):
        # plate file name
        pa = self._output_path + "/" + plate
        # download the plate files with a process lock
        self._downloader.load(plate)
        # parse the plate file names
        platefilesets = PlateFileSetParser(pa, self._output_path)
        if len(platefilesets) > 1:
            logger.warn("Found multiple plate identifiers for: " + plate)
        # parse the files
        self._parse_plate_file_sets(platefilesets)
        # remove the matlab plate files
        # TODO
        # platefilesets.remove()

    def _parse_plate_file_sets(self, platefilesets):
        """
        Parse the PlateFileSets (i.e.: all parsed folders) into tsvs.

        Iterate over the file sets and create matrices every platefileset
        represents a plate so every platefileset is a single file

        """
        for platefileset in platefilesets:
            # parse the feates to np arrays
            features = self._parse_plate_file_set(platefileset)
            if len(features) == 0:
                logger.warn("Didnt find features for: " +
                            platefileset.classifier + ". Continuing to next "
                                                      "set!")
                continue
            # load the mapping file for the wells
            mapping = self._parse_plate_mapping(platefileset)
            if mapping is None:
                logger.warn("Mapping is none for plate-fileset: " +
                            platefileset.classifier + ". Continuing to next "
                                                      "set!")
                continue
            self._integrate_platefileset(platefileset, features, mapping)

    def _parse_plate_file_set(self, plate_file_set):
        features = {}
        logger.info("Doing: " + str(plate_file_set.classifier))
        cnt = 0
        for plate_file in plate_file_set:
            cnt += 1
            # TODO
            if cnt == 2:
                break
            cf = parse_file(plate_file)
            if cf is None:
                continue
            self._add(features, cf)
        return features

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

    def _parse_plate_mapping(self, plate_file_set):
        logger.info("#Loading meta: " + str(plate_file_set.classifier))
        mapp = PlateSirnaGeneMapping(plate_file_set)
        return mapp

    def _integrate_platefileset(self, platefileset, features, mapping):
        """
        Iterate over all matlab files and create the final matrices

        :param platefileset: the platefile set
        :param features: the parses feature map

        """
        logger.info("Integrating the different features to a single matrix")
        # since some features have different numbers of calls
        for k, v in features.items():
            self._integrate_feature(platefileset, k, v, mapping)

    def _integrate_feature(self, platefileset, max_ncells, features, mapping):
        filename = platefileset.outfile + "_max_nit_" + max_ncells + ".tsv"
        logger.info("Writing to: " + filename)
        pathogen = platefileset.pathogen
        library = platefileset.library
        replicate = platefileset.replicate
        screen = platefileset.screen
        plate = platefileset.plate
        library_vendor, library_type = list(library)
        layout = self._layout_meta.get(pathogen, library, screen,
                                       replicate, plate)
        if layout is None:
            logger.warn("Could not load layout for: " + platefileset.classifier)
            return
        with open(filename, "w") as f:
            header = PlateParser._meta + \
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


class PlateLoader:
    """
    Class for plate downloading.

    """

    def __init__(self, bee_loader, output_path, username, pw):
        """
        Constructor for the plate downloader.

        :param bee_loader: the full path with the script name that downloads
        the data (e.g. /bla/..../BeeDataSetDownloader.sh)
        :param output_path: the folder where all the plates get stored and
        parsed to
        :param username: the user name of the open bis instance
        :param pw: the password of the open bis instance
        """
        self._bee_loader = bee_loader
        self._output_path = output_path
        self._username = username
        self._pw = pw

    def load(self, plate_id):
        """
        Download a plate using the bee-data downloader.

        :param plate_id: the full qualifier id of a plate
        :return:
        """
        global lock
        try:
            lock.acquire()
            logger.info("Downloading: " + plate_id)
            sc = [self._bee_loader,
                  "--user", self._username,
                  "--password", self._pw,
                  "--outputdir", self._output_path,
                  "--plateid", plate_id,
                  "--type", "HCS_ANALYSIS_CELL_FEATURES_CC_MAT",
                  "--newest",
                  "--files", ".*.mat"]
            ret = subprocess.call(sc)
            if ret != 0:
                logger.warn("\tdownload failed with status: " + str(0))
        finally:
            lock.release()
        return ret
