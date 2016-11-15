# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16


import logging
import re

from ._database_headers import DatabaseHeaders
from ._database_connector import DBConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__NA__ = "NA"


class Controller:
    def __init__(self, user, password, use_cassandra):
        self.__screen_regex = re.compile(
            "^(\S+-?\S+)-(\w+)-(\w)(\w)-(\w+)(\d+)(-(.*))?$")
        self.__user = user
        self.__meta = []
        self.__password = password
        self.__use_cassandra = use_cassandra

    def create(self, folder):
        self.__db_headers = DatabaseHeaders(folder)
        with DBConnection(self.__user, self.__password,
                          self.__use_cassandra) as connection:
            logger.info("Creating meta table")
            self._create_meta_table(connection)
            logger.info("Creating data tables")
            self._create_data_tables(connection)
            self._add_to_meta(connection)

    def query(self, query):
        pass

    def _create_meta_table(self, connection):
        if self.__use_cassandra:
            create_meta_statement = \
                "CREATE TABLE IF NOT EXISTS meta" \
                "(" \
                "id int, " \
                "study varchar, " \
                "pathogen varchar, " \
                "library varchar, " \
                "design varchar, " \
                "screen varchar, " \
                "replicate int, " \
                "suffix varchar, " \
                "primary key(id));"
        else:
            create_meta_statement = \
                "CREATE TABLE IF NOT EXISTS meta " \
                "(" \
                "id int(255) not null auto_increment, " \
                "study varchar(255) not null, " \
                "pathogen varchar(255) not null, " \
                "library varchar(255) not null, " \
                "design varchar(255) not null, " \
                "screen varchar(255) not null, " \
                "replicate int(255) not null, " \
                "suffix varchar(255), " \
                "primary key (id));"
        connection.execute(create_meta_statement)

    def _create_data_tables(self, con):
        for screen, _ in self.__db_headers.screens:
            st, pa, lib, des, scr, rep, suf = self._parse_screen(screen)
            self.__meta.append([st, pa, lib, des, scr, rep, suf])
            for ftype, features in self.__db_headers.feature_types:
                if any([st, pa, lib, des, scr, rep, suf]) is None:
                    continue
                self._create_data_table(con, ftype, features,
                                        st, pa, lib, des, scr, rep, suf)

    def _create_data_table(self, connection, ftype, features, st, pa, lib, des,
                           scr,
                           rep, suf):
        tbl = self._table_name(st, pa, lib, des, scr, rep, suf, ftype)
        fe = (" double, ".join(features)) + " double"
        create_statement = self._create_data_table_statement(tbl, fe)
        connection.execute(create_statement)

    def _create_data_table_statement(self, tbl, fe):
        create_statement = "CREATE TABLE IF NOT EXISTS " + tbl
        if self.__use_cassandra:
            create_statement += " (id int, plate varchar, "
        else:
            create_statement += " (id int(255), plate varchar(255), "
        create_statement += fe + ", primary key(id));"
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
            return pat.group(1), pat.group(2), pat.group(3), pat.group(4), \
                   pat.group(5), pat.group(6), \
                   pat.group(8) if pat.group(8) is not None else __NA__
        except AttributeError:
            logger.warn("Could not parse: " + str(screen))
            return None

    def _add_to_meta(self, conn):
        conn.add_batch_meta(self.__meta)
