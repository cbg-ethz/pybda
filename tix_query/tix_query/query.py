# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


from .meta import Meta


class Query:
    def __init__(self, file):
        self.__meta = Meta(file)