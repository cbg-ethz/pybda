# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16

import logging

import pymysql

logging.basicConfig(format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DBConnection:
    def __init__(self, user, password):
        self.__user = user
        self.__password = password

    def __enter__(self):
        logger.info("Connecting to db")
        self.__connection = pymysql.connect(
            host='localhost', user=self.__user, password=self.__password,
            db='tix',
            charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing connection to db")
        self.__connection.close()

    def execute(self, statement):
        with self.__connection.cursor() as cursor:
            cursor.execute(statement)
        self.__connection.commit()

    def close(self):
        self.__connection.close()
