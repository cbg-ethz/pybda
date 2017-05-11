# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 08.05.17

import re

GENE = "gene"
SIRNA = "sirna"
WELL = "well"

STUDY = "study"
PATHOGEN = "pathogen"
LIBRARY = "library"
DESIGN = "design"
REPLICATE = "replicate"
PLATE = "plate"

FILE_FEATURES_PATTERNS = re.compile(
      "(\w+)-(\w+)-(\w+)-(\w+)-(\w+)-(\d+)-(.*)_(\w+)")