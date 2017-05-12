# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 12.05.17


import logging
import os

import psycopg2
import yaml

from tix_query.tix_query.globals import FEATURECLASS, FEATURES, ELEMENTS
from tix_query.tix_query.globals import FILE_FEATURES_PATTERNS
from tix_query.tix_query.globals import GENE, SIRNA, WELL, LIBRARY, DESIGN
from tix_query.tix_query.globals import REPLICATE, PLATE, STUDY, PATHOGEN

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DatabaseInserter:
    _gsw_ = [GENE, SIRNA, WELL]
    _descr_ = [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE, FEATURECLASS]

    def __init__(self, connection):
        self.__connection = connection

    def insert(self, path):
        self._create_dbs()
        fls = list(
          filter(
            lambda x: x.endswith("_meta.tsv"), [f for f in os.listdir(path)]
          )
        )
        le = len(fls)
        for i, file in enumerate(fls):
            if i % 100 == 0:
                logger.info("Doing file {} of {}".format(i, le))
            self._insert(path, file)
        self._create_indexes()

    def _insert_file_suffixes(self, file, study, bacteria, library,
                              design, replicate, plate, featureclass):
        with self.__connection.cursor() as cursor:
            ins = self._insert_meta_into_statement(
              file, study, bacteria, library, design,
              replicate, plate, featureclass
            )
            cursor.execute(ins)
        self.__connection.commit()

    def _insert(self, path, file):
        filename = os.path.join(path, file)
        try:
            # parse file name meta information
            ma = FILE_FEATURES_PATTERNS.match(file.replace("_meta.tsv", ""))
            stu, pat, lib, des, ome, rep, pl, feature = ma.groups()
            self._insert_file_suffixes(
              filename, stu, pat, lib,
              des, rep, pl, feature
            )

            # read the meta file
            with open(filename, "r") as fh:
                meta = yaml.load(fh)
            self._insert_meta(filename, meta)

        except ValueError as e:
            logger.error("Could not match meta file {} and value {}"
                         .format(file, e, file))

    @staticmethod
    def _insert_meta_into_statement(
      file, study, bacteria, library,
      design, replicate, plate, featureclass):
        return "INSERT INTO meta " \
               "({}, {}, {}, {}, {}, {}, {}, {}) ".format(STUDY,
                                                          PATHOGEN,
                                                          LIBRARY,
                                                          DESIGN,
                                                          REPLICATE,
                                                          PLATE,
                                                          FEATURECLASS,
                                                          "filename") + \
               "VALUES (" + \
               "'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(study,
                                                                         bacteria,
                                                                         library,
                                                                         design,
                                                                         replicate,
                                                                         plate,
                                                                         featureclass,
                                                                         file)

    def _insert_meta(self, file, meta):
        self._insert_elements(file, meta[ELEMENTS])
        self._insert_features(file, meta[FEATURES])

    def _insert_elements(self, file, meta):
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

    def _insert_features(self, file, meta):
        tab = file.replace("_meta.tsv", "").split("/")[-1].replace("-", "_")
        if not self._exists(tab):
            self._create_file_feature_table(tab)
            with self.__connection.cursor() as c:
                for x in meta:
                    c.execute("INSERT INTO {} VALUES ('{}')".format(tab, x))
            self.__connection.commit()

    @staticmethod
    def _insert_into_statement(k, v, file):
        s = "INSERT INTO {} ({}, filename) VALUES('{}', '{}')" \
            .format(k, k, v, file)
        return s

    def _do(self, f):
        with self.__connection.cursor() as cursor:
            cursor.execute(f)
        self.__connection.commit()

    def _create_dbs(self):
        self._do(self._create_meta_table())
        for col in [GENE, SIRNA, WELL]:
            tb = self._create_table_name(col)
            self._do(tb)

    @staticmethod
    def _create_meta_table():
        s = "CREATE TABLE IF NOT EXISTS meta " + \
            "(" + \
            "id serial, "
        for col in DatabaseInserter._descr_:
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

    def _create_indexes(self):
        self._do(self._create_meta_index())
        for col in [GENE, SIRNA, WELL]:
            tb = self._create_table_index(col)
            self._do(tb)

    def _create_meta_index(self):
        s = "CREATE INDEX meta_index ON meta ({});"\
            .format(", ".join(DatabaseInserter._descr_))
        logger.info(s)
        return s

    def _create_table_index(self, t):
        s = "CREATE INDEX {}_index ON {} ({});".format(t, t, t)
        logger.info(s)
        return s

    def _create_file_feature_table(self, tab):
        s = "CREATE TABLE IF NOT EXISTS {}".format(tab) + \
            " (feature varchar(1000) NOT NULL, " + \
            "PRIMARY KEY(feature));"
        self._do(s)

    def _exists(self, tab):
        s = "SELECT EXISTS(SELECT * FROM information_schema.tables" \
            " WHERE table_name = '{}');".format(tab)
        with self.__connection.cursor() as c:
            c.execute(s)
            bol = c.fetchall()
        self.__connection.commit()
        return bol[0][0]
