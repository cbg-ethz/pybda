# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 12.05.17


import logging

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DatabaseQuery:
    def __init__(self, connection):
        self.__connection = connection

    def query(self, **kwargs):
        q = self._build_meta_query(**kwargs)
        logger.info(q)
        res = self._query(q)
        for x in res:
            print(x)
        print(len(res))

    def _query(self, q):
        with self.__connection.cursor() as cursor:
            cursor.execute(q)
            res = cursor.fetchall()
        self.__connection.commit()
        fls = set()
        for x in res:
            # TODO
            # path, filename =
            # /fls.add(TableFile())
            pass
        return res

    def _build_meta_query(self, **kwargs):
        s = "SELECT filename FROM meta WHERE "
        ar = []
        for k, v in kwargs.items():
            if v is not None:
                if k in DBMS._descr:
                    ar.append("{}='{}'".format(k, v))
        s += " and ".join(ar) + ";"
        return s
