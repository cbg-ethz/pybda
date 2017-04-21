# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16


import multiprocessing as mp
import logging

from .config import Config
from .plate_parser import PlateParser
from .plate_writer import PlateWriter
from .plate_file_set_generator.plate_file_sets import PlateFileSets
from .plate_layout import MetaLayout
from ._plate_list import PlateList

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = mp.log_to_stderr()


class Controller:
    """
    Class for parsing a folder of plates containing matlab files for the
    features.

    """

    def __init__(self, config):
        """
        Constructor for PlateParser.

        :param config: a configuration for file parsing
        :type config: Config
        """
        if not isinstance(config, Config):
            raise ValueError("Please provide a config object")
        self._config = config
        self._output_path = config.output_path
        self._multi_processing = config.multi_processing
        # read the plate list files
        # oly take files with regex pooled/unpooled genome/kinome
        self._plate_list = PlateList(
            config.plate_id_file,
            ".*\/\w+\-\w[P|U]\-[G|K]\d+\/.*"
        )
        # parse the folder into a map of (classifier-plate) pairs
        self._layout = MetaLayout(config.layout_file)
        self._parser = PlateParser()
        self._writer = PlateWriter(self._layout)

    def parse(self):
        """
        Iterate over the experiments, download the files, parse them and
        store to data-base.

        """
        exps = list(self._plate_list.plate_files)
        # use globals vars for process pool
        if self._multi_processing:
            # number of cores we are using
            n_cores = mp.cpu_count() - 1
            logger.info("Going parallel with " + str(n_cores) + " cores!")
            pool = mp.Pool(processes=n_cores)
            _ = pool.map(func=self._parse, iterable=exps)
            pool.close()
            pool.join()
        else:
            for x in exps:
                self._parse(x)
        logger.info("All's well that ends well")

    def _parse(self, plate):
        try:
            platefilesets = self.filesets(
                self._output_path + "/" + plate,
                self._output_path
            )
            if len(platefilesets) > 1:
                logger.warn("Found multiple plate identifiers for: " + plate)
            ret = self.parse_plate_file_sets(platefilesets)
        except Exception as e:
            logger.error("Found error parsing: " + str(plate) + ". " +
                         "Error:" + str(e))
            ret = -1
        return ret

    @staticmethod
    def filesets(folder, output_path):
        """
        Create a list of platefile sets contained in a folder. Recursively go
        through all the folders and add the found matlab files into the
        respective platefile set.

        :param folder: the folder that is recursively went through
        :param output_path: the output path where the platefile set is stored to
        :return: returns a platefilesets object
        """
        return PlateFileSets(folder, output_path)

    def parse_plate_file_sets(self, platefilesets):
        if not isinstance(platefilesets, PlateFileSets):
            raise TypeError("no PlateFileSets object given")
        try:
            for platefileset in platefilesets:
                logger.info("Doing: " + " ".join(platefileset.meta))
                pfs, features, mapping = self._parser.parse(platefileset)
                if pfs is not None:
                    self._writer.write(pfs, features, mapping)
        except Exception as e:
            logger.error("Some error idk anythin can happen here: " + str(e))
        return 0
