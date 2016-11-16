# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 16/11/16


import yaml
import logging

logger = logging.getLogger(__name__)


class Config:
    __BEE_PASSWORD__ = "bee_password"
    __BEE_USER__ = "bee_user_name"
    __BEE_LOADER__ = "bee_loader"
    __EXPERIMENT_FILE__ = "experiment_file"
    __LAYOUT_META_FILE__ = "layout_file"
    __OUTPUT_FOLDER__ = "output_folder"
    __DB_PASSWORD__ = "db_password"
    __DB_USER__ = "db_user_name"
    __CONFIG__ = \
        [__BEE_PASSWORD__, __BEE_USER__, __DB_PASSWORD__, __DB_USER__]

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
    def bee_username(self):
        return getattr(self, "_" + Config.__BEE_USER__)

    @property
    def bee_password(self):
        return getattr(self, "_" + Config.__BEE_PASSWORD__)

    @property
    def db_username(self):
        return getattr(self, "_" + Config.__DB_USER__)

    @property
    def db_password(self):
        return getattr(self, "_" + Config.__DB_PASSWORD__)
