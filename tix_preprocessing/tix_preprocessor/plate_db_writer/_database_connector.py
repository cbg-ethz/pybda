# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16

import logging

import psycopg2

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

__insert_meta_statement__ = "INSERT INTO meta " \
                            "(study, pathogen, library, design, screen, replicate, suffix, feature_group, table_name) " \
                            "VALUES " \
                            "(%s, %s, %s, %s, %s, %s, %s, %s, %s);"


class DBConnection:
    def __init__(self, user, password, db):
        self._id = 0
        self.__user = user
        self.__password = password
        self.__db = db

    def __enter__(self):
        logger.info("Connecting to db")
        self.__connection = psycopg2.connect(
            database=self.__db, user=self.__user, password=self.__password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing connection to db")
        self.__connection.close()

    def execute(self, statement):
        with self.__connection.cursor() as cursor:
            cursor.execute(statement)
        self.__connection.commit()

    def add_batch_meta(self, array):
        logger.error('to do')
        pass

    def insert_meta(self, study, pathogen, library, design, screen,
                    replicate, suffix, feature_group, table_name):
        with self.__connection.cursor() as cursor:
            cursor.execute(__insert_meta_statement__,
                           (study, pathogen, library, design, screen, replicate,
                            suffix, feature_group, table_name))
        self.__connection.commit()
