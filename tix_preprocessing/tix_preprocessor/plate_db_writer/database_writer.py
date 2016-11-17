# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16


import logging
import re

from ._database_connector import DBConnection
from ._database_headers import DatabaseHeaders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__NA__ = "NA"


class DatabaseWriter:
    meta_table_create_statement = "CREATE TABLE IF NOT EXISTS meta" \
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

    def __init__(self, user=None, password=None, db=None):
        self.__screen_regex = re.compile(
            "^(\S+-?\S+)-(\w+)-(\w)(\w)-(\w+)(\d+)(-(.*))?$")
        self.__user = user
        self.__meta = []
        self.__db = db
        self.__pw = password

    def print(self, folder):
        self._run(folder=folder, do_create=False)

    def create(self, folder):
        self._run(folder=folder, do_create=True)

    def _run(self, folder, do_create):
        self.__db_headers = DatabaseHeaders(folder)
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
        return DatabaseWriter.meta_table_create_statement

    def _execute(self, connection, job):
        connection.execute(job)

    def _create_data_table_statements(self):
        for screen, _ in self.__db_headers.screens:
            # study/pathogen/library/design/screen/replicate/suffix
            st, pa, lib, des, scr, rep, suf = self._parse_screen(screen)
            if None in [st, pa, lib, des, scr, rep, suf]:
                continue
            self.__meta.append([st, pa, lib, des, scr, rep, suf])
            for ftype, features in self.__db_headers.feature_types:
                yield self._create_data_table_statement(
                    ftype, features, st, pa, lib, des, scr, rep, suf)

    def _create_data_table_statement(
            self, ftype, features, st, pa, lib, des, scr, rep, suf):
        tbl = self._table_name(st, pa, lib, des, scr, rep, suf, ftype)
        fe = (" double precision, ".join(features)) + " double precision"
        create_statement = "CREATE TABLE IF NOT EXISTS " + tbl
        create_statement += " (plate varchar(40) NOT NULL, " \
                            "gene varchar(40), " \
                            "sirna varchar(40), " \
                            "well_idx integer, " \
                            "well_type varchar(40), " \
                            "image_idx integer, " \
                            "object_idx integer, "
        create_statement += fe + ", primary key(plate, gene, sirna, well_idx, " \
                                 " image_idx, object_idx));"
        return create_statement

    def _table_name(self, st, pa, lib, des, scr, rep, suf, f):
        if suf == __NA__:
            tbl = "_".join([st, pa, lib, des, scr, rep])
        else:
            tbl = "_".join([st, pa, lib, des, scr, rep, suf])
        tbl += "_" + f
        return tbl

    def _parse_screen(self, screen):
        try:
            pat = self.__screen_regex.match(screen.lower())
            if pat is None:
                return [None] * 7
            return pat.group(1), pat.group(2), pat.group(3), pat.group(4), \
                   pat.group(5), pat.group(6), \
                   pat.group(8) if pat.group(8) is not None else __NA__
        except AttributeError:
            logger.warn("Could not parse: " + str(screen))
            return None

    def _add_to_meta(self, conn):
        conn.add_batch_meta(self.__meta)
