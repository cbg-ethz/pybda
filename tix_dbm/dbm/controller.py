# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16


import logging

from ._database_headers import DatabaseHeaders
from ._database_connector import DBConnection

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)-1s/%(' \
                           'processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, user, password):
        self.__user = user
        self.__password = password

    def create(self, folder):
        self.__db_headers = DatabaseHeaders(folder)
        with DBConnection(self.__user, self.__password) as connection:
            logger.info("Creating meta table")
            self._create_meta_table(connection)
            logger.info("Creating data tables")
            self._create_data_table(connection)
            logger.info("Closing db connection")

    def query(self, query):
        pass

    def _create_meta_table(self, connection):
        create_meta_statement = \
            "CREATE TABLE IF NOT EXISTS meta " \
            "(" \
            "id int(255) not null auto_increment, " \
            "screen varchar(255) not null, " \
            "primary key (id));"
        connection.execute(create_meta_statement)

    def _create_data_table(self, connection):
        for screen, _ in self.__db_headers.screens:
            for feature_type, features in self.__db_headers.feature_types:
                tbl = screen.lower().replace("-", "_") + "_" + feature_type
                fe = (" double, ".join(features)) + " double"
                create_statement = \
                    "CREATE TABLE IF NOT EXISTS " + tbl + " " \
                                                          "(plate varchar(255), " + fe + ");"
                connection.execute(create_statement)
