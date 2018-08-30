# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 30.08.18


from abc import ABC, abstractmethod

class DimensionReduction(ABC):
    def __init__(self, spark, threshold, max_iter):
        self.__spark = spark
        self.__threshold = threshold
        self.__max_iter = max_iter

    @abstractmethod
    def fit(self):
        pass
