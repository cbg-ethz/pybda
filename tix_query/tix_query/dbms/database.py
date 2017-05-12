# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


import logging
import psycopg2

from tix_query.tix_query.dbms._db_query import DatabaseQuery
from tix_query.tix_query.dbms._db_setup import DatabaseInserter

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DBMS:
    def __init__(self):
        pass

    def __enter__(self):
        logger.info("Connecting to db")
        try:
            self.__connection = psycopg2.connect(database="tix")
        except Exception as e:
            logger.error("Could not connect" + e)
            exit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing connection to db")
        self.__connection.close()

    def query(self, **kwargs):
        q = DatabaseQuery(self.__connection)
        return q.query(**kwargs)

    def insert(self, path):
        d = DatabaseInserter(self.__connection)
        d.insert(path)


if __name__ == "__main__":
    import sys

    with DBMS() as d:
        d.insert(sys.argv[1])
