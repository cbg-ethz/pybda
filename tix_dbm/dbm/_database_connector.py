# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# add this for db creation
__CASSANDRA_KEYSPACE__ = \
    "CREATE KEYSPACE IF NOT EXISTS tix WITH replication = { " \
    "'class':'SimpleStrategy', 'replication_factor':1};"
__SQL_DATA_BASE__ = "CREATE DATABASE IF NOT EXISTS tix;"


class DBConnection:
    def __init__(self, user, password, use_cassandra):
        self._id  = 0
        self.__user = user
        self.__password = password
        self.__use_cassandra = use_cassandra

    def __enter__(self):
        logger.info("Connecting to db")
        if self.__use_cassandra:
            import cassandra.cluster as clust
            import cassandra.auth as auth
            auth_provider = auth.PlainTextAuthProvider(
                username=self.__user, password=self.__password)
            self.__cluster = clust.Cluster(auth_provider=auth_provider)
            self.__connection = self.__cluster.connect()
            self.__connection.default_timeout = 10
            self.execute(__CASSANDRA_KEYSPACE__)
            self.__connection.set_keyspace('tix')
        else:
            import pymysql
            self.__connection = pymysql.connect(
                host='localhost', user=self.__user, password=self.__password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            self.execute(__SQL_DATA_BASE__)
            self.__connection.select_db("tix")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing connection to db")
        if self.__use_cassandra:
            self.__connection.shutdown()
            self.__cluster.shutdown()
        else:
            self.__connection.close()

    def execute(self, statement):
        if self.__use_cassandra:
            self.__connection.execute(statement)
        else:
            with self.__connection.cursor() as cursor:
                cursor.execute(statement)
            self.__connection.commit()

    def add_batch_meta(self, array):
        if self.__use_cassandra:
            import cassandra.query as q
            insert_meta = self.__connection.prepare(
                "INSERT INTO meta (id, study, pathogen, library, design, "
                "screen, replicate, suffix) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
            batch = q.BatchStatement()
            for (study, pathogen, library, design, screen, replicate,
                 suffix) \
                    in array:
                batch.add(insert_meta, (int(self.next_id()),
                                        study, pathogen, library, design,
                                        screen, int(replicate), suffix))
            self.__connection.execute(batch)
        else:
            logger.error("NOT YET MPLEMENTED")

    def next_id(self):
        self._id += 1
        return self._id
