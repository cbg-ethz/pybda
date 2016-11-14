# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16

import logging

import pymysql

logging.basicConfig(format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DBConnection:
    def __init__(self, user, password, use_cassandra):
        self.__user = user
        self.__password = password
        self.__use_cassandra=use_cassandra

    def __enter__(self):
        logger.info("Connecting to db")
        if self.__use_cassandra:
            pass
        else:
            self.__connection = pymysql.connect(
                host='localhost', user=self.__user, password=self.__password,
                db='tix',
                charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing connection to db")
        if self.__use_cassandra:
            pass
        else:
            self.__connection.close()

    def execute(self, statement):
        if self.__use_cassandra:
            pass
        else:
            with self.__connection.cursor() as cursor:
                cursor.execute(statement)
            self.__connection.commit()

