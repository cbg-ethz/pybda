# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 23/09/16


import random


class PlateFileSet:
    def __init__(self, classifier, outfile, study, pathogen, library, design,
                 screen, replicate, suffix, plate):
        self._classifier = classifier
        self._outfile = outfile
        self._study = study
        self._pathogen = pathogen
        self._library = library
        self._design = design
        self._screen = screen
        self._replicate = replicate
        self._suffix = suffix
        self._plate = plate
        self._files = []
        # sirna-entrez mapping
        self._mapping = None

    def __iter__(self):
        for f in self._files:
            yield f

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "\t".join([self._study, self._pathogen, self._library,
                          self._design, self._screen, self._replicate,
                          self._plate, self._suffix])

    def __len__(self):
        return len(self._files)

    @property
    def meta(self):
        return [self._study, self._pathogen, self._library, self._design,
                self._screen, self._replicate, self._suffix, self.plate]

    @property
    def pathogen(self):
        return self._pathogen

    @property
    def library(self):
        return self._library

    @property
    def design(self):
        return self._design

    @property
    def replicate(self):
        return self._replicate

    @property
    def screen(self):
        return self._screen

    @property
    def plate(self):
        return self._plate

    def sample(self, cnt):
        return random.sample(self._files, cnt)

    @property
    def classifier(self):
        return self._classifier

    @property
    def files(self):
        return self._files

    @property
    def outfile(self):
        return self._outfile

    @property
    def study(self):
        return self._study

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, value):
        self._mapping = value

    @property
    def suffix(self):
        return self._suffix

