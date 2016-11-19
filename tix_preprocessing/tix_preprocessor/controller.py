# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

import multiprocessing as mp
import logging

from .config import Config
from .plate_parser import PlateParser
from .plate_file_set_generator.plate_file_sets import PlateFileSets
from .plate_list import PlateList
from .plate_db_writer import DatabaseWriter
from .plate_downloader import PlateDownloader
from .plate_layout import MetaLayout

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = mp.log_to_stderr()

lock, pool = None, None

startstr = "/GROUP_COSSART/LISTERIA_TEAM/LISTERIA-DP-G1/DZ44-1K"


class Controller:
    """
    Class for parsing a folder of plates containing matlab files for the
    features.

    """

    def __init__(self, config):
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
        if not isinstance(config, Config):
            logger.error("Please provide a config object")
            exit(-1)
        self._config = config
        self._output_path = config.output_path
        self._multi_processing = config.multi_processing
        # read the plate list files
        self._plate_list = PlateList(
            config.plate_id_file, ".*\/\w+\-\w[P|U]\-[G|K]\d+\/.*")
        # parse the folder into a map of (classifier-plate) pairs
        self._layout = MetaLayout(config.layout_file)
        # function to download data
        self._downloader = PlateDownloader(
            config.bee_loader, self._output_path,
            config.bee_username, config.bee_password)
        # the connection to the database
        self._db_writer = DatabaseWriter(
            user=config.db_username, password=config.db_password,
            db=config.db_name, folder=config.plate_folder)
        self._parser = PlateParser()

    def parse(self):
        """
        Iterate over the experiments, download the files, parse them and
        store to data-base.

        """
        exps = list(filter(lambda x: x.startswith(startstr),
                           self._plate_list.plate_files))
        self._db_writer.create_meta_table()
        # use globals vars for process pool
        if self._multi_processing:
            global lock
            global pool
            lock = mp.Lock()
            # # number of cores we are using
            n_cores = mp.cpu_count() - 1
            logger.info("Going parallel with " + str(n_cores) + " cores!")
            pool = mp.Pool(n_cores)
            ret = pool.map_async(func=self._parse, iterable=exps)
            pool.close()
            pool.join()
        else:
            for x in exps:
                self._parse(x)
        logger.info("All's well that ends well")

    def _parse(self, plate):
        try:
            # download the plate files with a process lock
            down_ret_val = self.download_plate(plate)
            if down_ret_val != 0:
                return -1
            # parse the plate file name into a list of file sets
            platefilesets = self.filesets(self._output_path + "/" + plate,
                                          self._output_path)
            if len(platefilesets) > 1:
                logger.warn("Found multiple plate identifiers for: " + plate)
            # parse the files
            ret = self.parse_plate_file_sets(platefilesets)
        except Exception as e:
            logger.error("Found error parsing: " + str(plate) +
                         ". Error:" + str(e))
            ret = -1
        return ret

    def download_plate(self, plate_id):
        """
        Download a plate using the bee-data downloader.

        :param plate_id: the full qualifier id of a plate
        :return:
        """
        logger.info("Downloading: " + plate_id)
        if self._multi_processing:
            global lock
            try:
                lock.acquire()
                ret = self._downloader.load(plate_id)
            finally:
                lock.release()
        else:
            ret = self._downloader.load(plate_id)
        if ret != 0:
            logger.warn("\tdownload failed with status: " + str(0))
        return ret

    def filesets(self, folder, output_path):
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
        try:
            self._db_writer.create_meta_table()
            for platefileset in platefilesets:
                meta = platefileset.meta
                self._db_writer.insert_meta(meta[0], meta[1], meta[2], meta[3],
                                            meta[4], meta[5], meta[6])
                self._db_writer.create_data_tables(meta[0], meta[1], meta[2],
                                                   meta[3], meta[4], meta[5],
                                                   meta[6])
                self._parser.parse(platefileset)
            # TODO
            # platefilesets.remove()
        except Exception as e:
            logger.error("Error: " + str(e))
        return 0
