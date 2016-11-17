# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 17/11/16


class PlateWell:
    def __init__(self, gene, sirna, well, well_type):
        self._gene = gene
        self._sirna = sirna
        self._well = well
        self._well_type = well_type

    @property
    def gene(self):
        return self._gene

    @property
    def sirna(self):
        return self._sirna

    @property
    def welltype(self):
        return self._well_type
