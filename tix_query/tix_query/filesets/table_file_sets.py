# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 28.04.17


from tix_query.tix_query.dbms.database import DBMS


class TableFileSets:
    def __init__(self):
        # map of maps that hold file pointers
        # map - (1:n) -> [_gene_map , ...] - (1:m) -> filename
        self._file_set = set()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "TODO"

    def filter(self, **kwargs):
        """
        Get a set of files that meets some criteria. Kwargs is a names list, 
        that can have the following form:
         
         {
                study="infectx",
                pathogen="salmonella",
                well="a01",
                gene="tp53",
                sirna="blub",
                replicate=1,
                library="d"
         }
        
        :return: returns a set of TableFile
         :rtype: set(TableFile)
        """

        with DBMS() as d:
            res = d.query(**kwargs)


