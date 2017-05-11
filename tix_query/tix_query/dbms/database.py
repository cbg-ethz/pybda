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
    _features_ = "features"
    _elements_ = "elements"
    _sample_ = "sample"
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
        fls = list(filter(
          lambda x: x.endswith("_meta.tsv"), [f for f in os.listdir(path)]
        ))
        le = len(fls)
        for i, file in enumerate(fls):
            if i % 100 == 0:
                logger.info("Doing file {} of {}".format(i, le))
            self._insert(path, file)
        self.create_indexes()

    def _do(self, f):
        with self.__connection.cursor() as cursor:
            cursor.execute(f)
        self.__connection.commit()

    def create_dbs(self):
        self._do(self._create_meta_table())
        for col in [GENE, SIRNA, WELL]:
            tb = self._create_table_name(col)
            self._do(tb)

    @staticmethod
    def _create_meta_table():
        s = "CREATE TABLE IF NOT EXISTS meta " + \
            "(" + \
            "id serial, "
        for col in [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE]:
            s += "{} varchar(100) NOT NULL, ".format(col)
        s += "filename varchar(1000) NOT NULL, " + \
             "PRIMARY KEY(id)" + \
             ");"
        logger.info(s)
        return s

    @staticmethod
    def _create_table_name(t):
        s = "CREATE TABLE IF NOT EXISTS {} ".format(t) + \
            "(" + \
            "id serial, " + \
            "{} varchar(100) NOT NULL, ".format(t) + \
            "filename varchar(1000) NOT NULL, " + \
            "PRIMARY KEY(id)" + \
            ");"
        logger.info(s)
        return s

    def create_indexes(self):
        self._do(self._create_meta_index())
        for col in [GENE, SIRNA, WELL]:
            tb = self._create_table_index(col)
            self._do(tb)

    def _create_meta_index(self):
        s = "CREATE INDEX meta_index ON meta (" + \
            ", ".join([STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE]) + \
            ")"
        logger.info(s)
        return s

    def _create_table_index(self, t):
        s = "CREATE INDEX {}_index ON {} ({});".format(t, t, t)
        logger.info(s)
        return s

    def _insert(self, path, file):
        filename = os.path.join(path, file)
        try:
            # parse file name meta information
            study, bacteria, library, design, \
            ome, replicate, plate, feature = \
                FILE_FEATURES_PATTERNS \
                    .match(file.replace("_meta.tsv", "")) \
                    .groups()
            self._insert_file_suffixes(filename,
                                       study,
                                       bacteria,
                                       library,
                                       design,
                                       replicate,
                                       plate)
            # read the meta file
            with open(filename, "r") as fh:
                meta = yaml.load(fh)
            self._insert_meta(filename, meta[DBMS._elements_])
        except ValueError as e:
            logger.error("Could not match meta file {} and value {}"
                         .format(file, e, file))

    def _insert_file_suffixes(self,
                              file,
                              study,
                              bacteria,
                              library,
                              design,
                              replicate,
                              plate):
        with self.__connection.cursor() as cursor:
            ins = self._insert_meta_into_statement(file,
                                                   study,
                                                   bacteria,
                                                   library,
                                                   design,
                                                   replicate,
                                                   plate)
            cursor.execute(ins)
        self.__connection.commit()

    @staticmethod
    def _insert_meta_into_statement(file,
                                    study,
                                    bacteria,
                                    library,
                                    design,
                                    replicate,
                                    plate):
        return "INSERT INTO meta " \
               "({}, {}, {}, {}, {}, {}, {}) ".format(STUDY,
                                                      PATHOGEN,
                                                      LIBRARY,
                                                      DESIGN,
                                                      REPLICATE,
                                                      PLATE,
                                                      "filename") + \
               "VALUES (" + \
               "'{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(study,
                                                                   bacteria,
                                                                   library,
                                                                   design,
                                                                   replicate,
                                                                   plate, file)

    def _insert_meta(self, file, meta):
        with self.__connection.cursor() as cursor:
            for element in meta:
                try:
                    well, gene, sirna = element.split(";")[:3]
                    for k, v in {WELL: well, GENE: gene, SIRNA: sirna}.items():
                        ins = self._insert_into_statement(k, v, file)
                        cursor.execute(ins)
                except ValueError as e:
                    logger.error("Could not match element {} and error {}"
                                 .format(element, e))
        self.__connection.commit()

    @staticmethod
    def _insert_into_statement(k, v, file):
        s = "INSERT INTO {} ({}, filename) VALUES('{}', '{}')" \
            .format(k, k, v, file)
        return s


if __name__ == "__main__":
    path = "/Users/simondi/PROJECTS/target_infect_x_project/data/target_infect_x/screening_data"
    with DBMS() as d:
        d.insert(path)
