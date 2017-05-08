# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16


import logging
import re

import psycopg2

from tix_parser.utility import parse_screen_details
from .database_headers import DatabaseHeaders

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
    __insert_meta_statement__ = "INSERT INTO meta " \
                                "(study, pathogen, library, design, screen, replicate, suffix, feature_group, table_name) " \
                                "VALUES " \
                                "(%s, %s, %s, %s, %s, %s, %s, %s, %s);"

    def __init__(self, folder, user=None, password=None, db=None):
        self.__screen_regex = re.compile(
            "^(\S+-?\S+)-(\w+)-(\w)(\w)-(\w+)(\d+)(-(.*))?$")
        self.__user = user
        self.__meta = []
        self.__db = db
        self.__pw = password
        self.__db_headers = DatabaseHeaders(folder)

    def __enter__(self):
        logger.info("Connecting to db")
        self.__connection = psycopg2.connect(
            database=self.__db, user=self.__user, password=self.__pw)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing connection to db")
        self.__connection.close()

    def execute(self, statement):
        with self.__connection.cursor() as cursor:
            cursor.execute(statement)
        self.__connection.commit()

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
        Create a meta data filesets.
        """
        meta_data_st = self._create_meta_table_statement()
        logger.info("Creating meta filesets")
        with self.__connection.cursor as cursor:
            cursor.execute(meta_data_st)
        self.__connection.commit()

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
            with self.__connection.cursor() as cursor:
                for feature_group, feature_type in self.__db_headers.feature_types:
                    st = self._create_data_table_statement(
                        feature_group, feature_type, study, pathogen, library,
                        design, screen, replicate, suffix)
                    cursor.execute(st)
            self.__connection.commit()
        except Exception as e:
            logger.error(str(e))

    def insert_batch(self, statemet, batch):
        with self.__connection.cursor() as cursor:
            try:
                cursor.executemany(statemet, batch)
            except Exception as e:
                logger.error(str(e))
        self.__connection.commit()

    def insert_meta(self, study, pathogen, library, design,
                    screen, replicate, suffix):
        """
        Insert meta information into the meta filesets

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
            with self.__connection.cursor() as cursor:
                for feature_group, feature_type_ in self.__db_headers.feature_types:
                    table_name = self.table_name(study, pathogen, library,
                                                 design, screen, replicate,
                                                 suffix, feature_group)
                    cursor.execute(DatabaseWriter.__insert_meta_statement__,
                                   (study, pathogen, library, design, screen,
                                    replicate,
                                    suffix, feature_group, table_name))
        except Exception as e:
            logger.error(str(e))

    def _run(self, do_create):
        meta_data_st = self._create_meta_table_statement()
        data_tab_statements = self._create_data_table_statements()
        if do_create:
            with self.__connection.cursor() as cursor:
                logger.info("Creating meta filesets")
                cursor.execute(meta_data_st)
                logger.info("Creating data tables")
                for x in data_tab_statements:
                    cursor.execute(x)
            self.__connection.commit()
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
        Create the 'create filesets statement' for an experiment and feature group.

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
        :return: returns the 'create data filesets statement'
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

    def _write_db(self, tablename, features, mapping, plate, layout):
        nimg = features[0].values.shape[0]
        assert nimg == len(mapping)
        state = "INSERT INTO " + tablename + \
                " ( " + \
                ", ".join(PlateParser._meta_) + ', ' + \
                ", ".join([x.short_name for x in features]) + ") " + \
                "VALUES (" + ', '.join(
            ["%s"] * (len(PlateParser._meta_) + len(features))) + ");"
        dat = []
        for iimg in range(nimg):
            well = mapping[iimg]
            pat = PlateParser._well_regex.match(well.lower())
            row, col = pat.group(1), int(pat.group(2))
            for cell in range(features[0].ncells[iimg]):
                vals = [features[p].values[iimg, cell] for p in
                        range(len(features))]
                meta = [plate, layout.gene(well), layout.sirna(well), row,
                        int(col), layout.welltype(well), iimg + 1, cell + 1]
                dat.append(list(map(str, meta + vals)))
                if len(dat) == 10000:
                    self._db.insert_batch(state, dat)
                    dat = []
        self._db.insert_batch(state, dat)
        return 0
