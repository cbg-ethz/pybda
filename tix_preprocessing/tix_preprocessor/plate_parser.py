# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

import subprocess
import multiprocessing as mp
import random

from .plate_downloader import PlateDownloader
from ._plate_list import PlateList
from .plate_layout import PlateLayoutMeta
from ._plate_sirna_gene_mapping import PlateSirnaGeneMapping
from ._utility import parse_file
from .plate_file_set_parser import PlateFileSetParser

logger = mp.log_to_stderr()

lock, pool = None, None


# TODO: make nice
# TODO: better logging


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
        self._bee_loader = bee_loader
        self._username = username
        self._pw = pw
        self._output_path = output_path
        # read the expe
        self._plate_list = PlateList(
            experiment_file, ".*\/\w+\-\w[P|U]\-[G|K]\d+\/.*")
        # parse the folder into a map of (classifier-plate) pairs
        self._layout = PlateLayoutMeta(layout_file)
        # function to download data
        self._downloader = PlateDownloader(
            bee_loader, output_path, username, pw)
        self._db_writer = DatabaseWriter()

    def parse(self):
        """
        Iterate over the experiments, download the files, parse them and
        store to tsv.

        """
        # use globals vars for process pool
        global lock
        global pool
        lock = mp.Lock()
        # # number of cores we are using
        n_cores = mp.cpu_count() - 1
        logger.info("Going parallel with " + str(n_cores) + " cores!")
        # pool = mp.Pool(n_cores)
        # get only infect x data
        # TODO: remove this after testing
        # exps = list(filter(lambda x: x.startswith("/INFECT"),
        #               self._experiment_meta.plate_files))
        exps = list(self._plate_list.plate_files)
        random.shuffle(exps)
        exps = exps[:150]
        for i in exps:
            print(i)
            self._parse(i)
        # asynychronously start jobs
        # ret = pool.map_async(func=self._parse, iterable=exps)
        # pool.close()
        # pool.join()
        logger.info("All's well that ends well")

    def _parse(self, plate):
        # ret = 0
        # try:
        # plate file name
        pa = self._output_path + "/" + plate
        # download the plate files with a process lock
        down_ret_val = self._downloader.load(plate)
        # if down_ret_val != 0:
        #     return -1
        # # parse the plate file names
        # platefilesets = PlateFileSetParser(pa, self._output_path)
        # if len(platefilesets) > 1:
        #     logger.warn("Found multiple plate identifiers for: " + plate)
        # parse the files
        # ret = self._parse_plate_file_sets(platefilesets)
        # remove the matlab plate files
        # TODO
        # platefilesets.remove()
        # except Exception:
        #     logger.error("Found error parsing: " + str(plate))
        #     ret = -1
        return 1

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
                            platefileset.classifier +
                            ". Continuing to next set!")
                continue
            # load the mapping file for the wells
            mapping = self._parse_plate_mapping(platefileset)
            if mapping is None:
                logger.warn("Mapping is none for plate-fileset: " +
                            platefileset.classifier +
                            ". Continuing to next set!")
                continue
            self._integrate_platefileset(platefileset, features, mapping)
        return 0

    def _parse_plate_file_set(self, plate_file_set):
        features = {}
        logger.info("Parsing plate file set to memory: " +
                    str(plate_file_set.classifier))
        for plate_file in plate_file_set:
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
        return 0

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
            ret = self._downloader.load(plate_id)
            if ret != 0:
                logger.warn("\tdownload failed with status: " + str(0))
        finally:
            lock.release()
        return ret
