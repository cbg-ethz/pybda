# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


from tix_query.tix_query.controller import Controller


class Query:
    def __init__(self):
        self.__ctrl = Controller()

    def query(self,
              study=None,
              pathogen=None,
              library=None,
              design=None,
              replicate=None,
              plate=None,
              gene=None,
              sirna=None,
              well=None,
              featureclass=None,
              sample=100):
        return self.__ctrl.query(sample=sample,
                                 study=study,
                                 pathogen=pathogen,
                                 library=library,
                                 design=design,
                                 replicate=replicate,
                                 plate=plate,
                                 gene=gene,
                                 sirna=sirna,
                                 well=well,
                                 featureclass=featureclass)


if __name__ == "__main__":
    q = Query()
    res = q.query(study="infectx", well="a01", library="d", replicate=1)
    res.dump()
