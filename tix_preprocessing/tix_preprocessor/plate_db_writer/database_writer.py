# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16


import logging
import re

from tix_preprocessor.utility import parse_screen_details
from ._database_connector import DBConnection
from ._database_headers import DatabaseHeaders

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

__NA__ = "NA"


class DatabaseWriter:
    __meta_table_create_statement__ = "CREATE TABLE IF NOT EXISTS meta" \
                                      "(" \
                                      "study varchar(40) NOT NULL, " \
                                      "pathogen varchar(40) NOT NULL, " \
                                      "library varchar(40) NOT NULL, " \
                                      "design varchar(40) NOT NULL, " \
                                      "screen varchar(40) NOT NULL, " \
                                      "replicate integer NOT NULL, " \
                                      "suffix varchar(40), " \
                                      "feature_group varchar(40) NOT NULL, " \
                                      "table_name varchar(300) NOT NULL, " \
                                      "PRIMARY KEY(table_name)" \
                                      ")"
    __data_table_colname_statement__ = " (plate varchar(40) NOT NULL, " \
                                       "gene varchar(40), " \
                                       "sirna varchar(40), " \
                                       "row char(1), " \
                                       "col integer, " \
                                       "well_type varchar(40), " \
                                       "image_idx integer, " \
                                       "object_idx integer, "
    __data_table_end_statement__ = ");"

    def __init__(self, folder, user=None, password=None, db=None):
        self.__screen_regex = re.compile(
            "^(\S+-?\S+)-(\w+)-(\w)(\w)-(\w+)(\d+)(-(.*))?$")
        self.__user = user
        self.__meta = []
        self.__db = db
        self.__pw = password
        self.__db_headers = DatabaseHeaders(folder)

    def print(self):
        """
        Parse a folder of plates and feature files and print the statements
        for the tables creations using postgreSQL.

        :param folder: a folder containing plates and matlab files
        """
        self._run(do_create=False)

    def create(self):
        """
        Parse a folder of plates and feature files and create the respective
        tables in a postgreSQL database.

        :param folder: a folder containing plates and matlab files
        """
        self._run(do_create=True)

    def create_meta_table(self):
        """
        Create a meta data table.
        """
        meta_data_st = self._create_meta_table_statement()
        with DBConnection(self.__user, self.__pw, self.__db) as connection:
            logger.info("Creating meta table")
            self._execute(connection, meta_data_st)

    def create_data_tables(self, study, pathogen, library, design, screen,
                           replicate, suffix):
        """
        Create the respective tables given the full set of informations for
        an experiment

        :param study: the name of the study, e.g. infectx
        :param pathogen: the name of the pathogen, e.g. bartonella
        :param library: the name of the library, e.g. ambion
        :param design: the kind of the library design, e.g. 'p' for pooled
        :param screen: the level on which the experiment was performed on,
        e.g. 'k' for kinome
        :param replicate: the replicate number, e.g. 1
        :param suffix: a random suffix, e.g. 1-pmol
        """
        try:
            with DBConnection(self.__user, self.__pw, self.__db) as connection:
                for feature_group, feature_type in self.__db_headers.feature_types:
                    st = self._create_data_table_statement(feature_group,
                                                           feature_type, study,
                                                           pathogen, library,
                                                           design,
                                                           screen, replicate,
                                                           suffix)
                    self._execute(connection, st)
        except Exception as e:
            logger.error(str(e))

    def insert_batch(self, statement, data):
        with DBConnection(self.__user, self.__pw, self.__db) as connection:
            connection.insert_batch(statement, data)

    def insert_meta(self, study, pathogen, library, design,
                    screen, replicate, suffix):
        """
        Insert meta information into the meta table

        :param study: the name of the study, e.g. infectx
        :param pathogen: the name of the pathogen, e.g. bartonella
        :param library: the name of the library, e.g. ambion
        :param design: the kind of the library design, e.g. 'p' for pooled
        :param screen: the level on which the experiment was performed on,
        e.g. 'k' for kinome
        :param replicate: the replicate number, e.g. 1
        :param suffix: a random suffix, e.g. 1-pmol
        """

        try:
            with DBConnection(self.__user, self.__pw, self.__db) as connection:
                for feature_group, feature_type_ in self.__db_headers.feature_types:
                    table_name = self.table_name(study, pathogen, library, design,
                                                 screen, replicate, suffix,
                                                 feature_group)
                    connection.insert_meta(study, pathogen, library,
                                           design, screen,
                                           replicate, suffix, feature_group,
                                           table_name)
        except Exception as e:
            logger.error(str(e))

    def _run(self, do_create):
        meta_data_st = self._create_meta_table_statement()
        data_tab_statements = self._create_data_table_statements()
        if do_create:
            with DBConnection(self.__user, self.__pw, self.__db) as connection:
                logger.info("Creating meta table")
                self._execute(connection, meta_data_st)
                logger.info("Creating data tables")
                for x in data_tab_statements:
                    self._execute(connection, x)
        else:
            print(meta_data_st)
            for x in data_tab_statements:
                print(x)

    def _create_meta_table_statement(self):
        return DatabaseWriter.__meta_table_create_statement__

    def _execute(self, connection, job):
        connection.execute(job)

    def _create_data_table_statements(self):
        for screen, _ in self.__db_headers.screens:
            # study/pathogen/library/design/screen/replicate/suffix
            st, pa, lib, des, scr, rep, suf = parse_screen_details(screen)
            if None in [st, pa, lib, des, scr, rep, suf]:
                continue
            self.__meta.append([st, pa, lib, des, scr, rep, suf])
            for ftype, features in self.__db_headers.feature_types:
                yield self._create_data_table_statement(
                    ftype, features, st, pa, lib, des, scr, rep, suf)

    def _create_data_table_statement(self, feature_group, features, study,
                                     pathogen, library, design, screen,
                                     replicate, suffix):
        """
        Create the 'create table statement' for an experiment and feature group.

        :param feature_group: the feature group, such as 'cell'
        :param features: a list of features (with double values)
        :param study: the name of the study, e.g. infectx
        :param pathogen: the name of the pathogen, e.g. bartonella
        :param library: the name of the library, e.g. ambion
        :param design: the kind of the library design, e.g. 'p' for pooled
        :param screen: the level on which the experiment was performed on,
        e.g. 'k' for kinome
        :param replicate: the replicate number, e.g. 1
        :param suffix: a random suffix, e.g. 1-pmol
        :return: returns the 'create data table statement'
        """
        tbl = self.table_name(study, pathogen, library, design, screen,
                              replicate, suffix, feature_group)
        fe = (" double precision, ".join(features)) + " double precision"
        create_statement = "CREATE TABLE IF NOT EXISTS " + tbl
        create_statement += DatabaseWriter.__data_table_colname_statement__
        create_statement += fe + DatabaseWriter.__data_table_end_statement__
        return create_statement

    def table_name(self, study, pathogen, library, design, screen, replicate,
                   suffix, feature_group):
        if suffix == __NA__:
            tbl = "_".join(
                [study, pathogen, library, design, screen, replicate])
        else:
            tbl = "_".join(
                [study, pathogen, library, design, screen, replicate, suffix])
        tbl += "_" + feature_group
        return tbl
