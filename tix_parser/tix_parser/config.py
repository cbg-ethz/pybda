# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 16/11/16


import yaml
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class Config:
    __PLATE_ID_FILE__ = "plate_id_file"
    __LAYOUT_FILE__ = "layout_file"
    __PLATE_FOLDER__ = "plate_folder"
    __OUTPUT_PATH__ = "output_path"
    __MULTI_PROCESSING__ = "multiprocessing"
    __CONFIG__ = \
        [
            __PLATE_FOLDER__, __PLATE_ID_FILE__, __LAYOUT_FILE__,
            __MULTI_PROCESSING__, __OUTPUT_PATH__
        ]

    def __init__(self, credentials):
        with open(credentials, 'r') as f:
            doc = yaml.load(f)
            for credential in Config.__CONFIG__:
                if credential not in doc:
                    logger.error(
                        "Could not find credential: " + str(credential))
                    exit(-1)
                setattr(self, "_" + credential, doc[credential])

    @property
    def plate_id_file(self):
        return getattr(self, "_" + Config.__PLATE_ID_FILE__)

    @property
    def layout_file(self):
        return getattr(self, "_" + Config.__LAYOUT_FILE__)

    @property
    def multi_processing(self):
        return bool(getattr(self, "_" + Config.__MULTI_PROCESSING__))

    @property
    def output_path(self):
        return getattr(self, "_" + Config.__OUTPUT_PATH__) + "/"

    @property
    def plate_folder(self):
        return getattr(self, "_" + Config.__PLATE_FOLDER__)
