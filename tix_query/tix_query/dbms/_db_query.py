# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 12.05.17


import logging

from tix_query.tix_query.filesets.table_file import TableFile
from tix_query.tix_query.globals import FEATURECLASS
from tix_query.tix_query.globals import GENE, SIRNA, LIBRARY, DESIGN
from tix_query.tix_query.globals import REPLICATE, PLATE, STUDY, PATHOGEN

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DatabaseQuery:
    _gsw_ = [GENE, SIRNA]
    _descr_ = [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE, FEATURECLASS]

    def __init__(self, connection):
        self.__connection = connection

    def query(self, **kwargs):
        q = self._build_query(**kwargs)
        logger.info(q)
        res = self._query(q, **kwargs)
        return res

    def _query(self, q, **kwargs):
        with self.__connection.cursor() as cursor:
            cursor.execute(q)
            res = cursor.fetchall()
        self.__connection.commit()
        fls = { TableFile(x[0], **kwargs) for x in res }
        return fls

    def _build_query(self, **kwargs):
        mq = self._build_meta_query(**kwargs)
        gq = self._build_plate_query(GENE, **kwargs)
        sq = self._build_plate_query(SIRNA, **kwargs)
        su = None
        if gq is not None and sq is not None:
            su = "JOIN (SELECT a1.filename \n" + \
                "\t\tFROM ({}) a1 \n".format(gq) + \
                "\t\tJOIN ({}) a2 \n".format(sq) + \
                "\t\tON (a1.filename = a2.filename) \n" + \
            "\t) a2"
        elif gq:
            su = "JOIN ({}) a2".format(gq)
        elif sq:
            su = "JOIN ({}) a2".format(sq)
        if su:
            q = "\nSELECT a1.filename \n" \
                "\tFROM ({}) a1 \n".format(mq) + \
                "\t" + su + " \n" \
                "\tON (a1.filename = a2.filename);"
        else:
            q = mq + ";"
        return q

    def _build_meta_query(self, **kwargs):
        s = "SELECT filename FROM meta"
        ar = []
        for k, v in kwargs.items():
            if v is not None:
                if k in DatabaseQuery._descr_:
                    ar.append("{}='{}'".format(k, v))
        if len(ar) > 0:
            s += " WHERE " + " and ".join(ar)
        return s

    def _build_plate_query(self, el, **kwargs):
        s = None
        if el in kwargs.keys():
            if kwargs[el] is not None:
                s = "SELECT filename FROM {} WHERE {}='{}'" \
                    .format(el, el, kwargs[el])
        return s
