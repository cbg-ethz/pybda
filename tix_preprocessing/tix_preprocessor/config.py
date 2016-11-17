# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 16/11/16


import yaml
import logging

logger = logging.getLogger(__name__)


class Config:
    __BEE_PASSWORD__ = "bee_password"
    __BEE_USER__ = "bee_username"
    __BEE_LOADER__ = "bee_loader"
    __DB_PASSWORD__ = "db_password"
    __DB_USER__ = "db_username"
    __DB__ = "db_name"
    __PLATE_ID_FILE__ = "plate_id_file"
    __LAYOUT_FILE__ = "layout_file"
    __PLATE_FOLDER__ = "plate_folder"
    __OUTPUT_PATH__ = "output_path"
    __MULTI_PROCESSING__ = "multiprocessing"
    __CONFIG__ = \
        [__BEE_PASSWORD__, __BEE_USER__, __BEE_LOADER__,
         __DB__, __DB_PASSWORD__, __DB_USER__,
         __PLATE_FOLDER__, __PLATE_ID_FILE__, __LAYOUT_FILE__,
         __MULTI_PROCESSING__, __OUTPUT_PATH__
         ]

    def __init__(self, credentials):
        with open(credentials, 'r') as f:
            doc = yaml.load(f)
            for credential in Config.__CONFIG__:
                if credential not in doc:
                    logger.error("Could not find credential: " + str(credential))
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
    def bee_username(self):
        return getattr(self, "_" + Config.__BEE_USER__)

    @property
    def bee_password(self):
        return getattr(self, "_" + Config.__BEE_PASSWORD__)

    @property
    def bee_loader(self):
        return getattr(self, "_" + Config.__BEE_LOADER__)

    @property
    def db_username(self):
        return getattr(self, "_" + Config.__DB_USER__)

    @property
    def db_password(self):
        return getattr(self, "_" + Config.__DB_PASSWORD__)

    @property
    def db_name(self):
        return getattr(self, "_" + Config.__DB__)