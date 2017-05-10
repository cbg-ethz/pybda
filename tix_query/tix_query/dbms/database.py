# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


import logging
import os
import re
import psycopg2
import yaml

from tix_query.tix_query._global import GENE, SIRNA, WELL, LIBRARY, DESIGN
from tix_query.tix_query._global import REPLICATE, PLATE, STUDY, PATHOGEN
from tix_query.tix_query._global import FILE_FEATURES_PATTERNS

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DBMS:
    _gsw_ = [
        x for x in [GENE, SIRNA, WELL]
    ]
    _descr = [
        x for x in
        [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE]
    ]

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

    def insert(self, path):
        self.create_dbs()
        fls = filter(
          lambda x: x.endswith("_meta.tsv"),
          [os.path.join(path, f) for f in os.listdir(path)]
        )
        # for file in fls:
        #     self._insert(file)

    def _insert(self, file):
        try:
            # parse file name meta information
            study, bacteria, library, design, \
            ome, replicate, plate, feature = \
                FILE_FEATURES_PATTERNS \
                    .match(file.replace("_meta.tsv", "")) \
                    .groups()
            #
            # # read the meta file
            # with open(file, "r") as fh:
            #     meta = yaml.load(fh)


        except ValueError as e:
            logger.error("Could not match meta file {} and value {}"
                         .format(file, e, file))

    def create_dbs(self):
        tbs = [GENE, SIRNA, WELL, LIBRARY, DESIGN,
               REPLICATE, PLATE, STUDY, PATHOGEN]
        with self.__connection.cursor() as cursor:
            for t in tbs:
                cursor.execute(self._create_table_name(t))
        self.__connection.commit()

    def _create_table_name(self, t):
        return "CREATE TABLE IF NOT EXISTS " + t + \
               "(" \
               "id integer NOT NULL, " + \
               t + " varchar(40) NOT NULL, " + \
               "filename varchar(100) NOT NULL, " + \
               "PRIMARY KEY(id)" + \
               ")"


if __name__ == "__main__":
    path = "/Users/simondi/PROJECTS/target_infect_x_project/data/target_infect_x/screening_data"
    with DBMS() as d:
        d.insert(path)
