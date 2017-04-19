# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 18.04.17


import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


def check_feature_group(fg):
    if not isinstance(fg, list):
        raise ("provide a list, yo")
    f1_cells = fg[0].ncells
    for j, f in enumerate(fg):
        fj_cells = f.ncells
        for i, fj_cells_i in enumerate(fj_cells):
            try:
                if f1_cells[i] != fj_cells_i:
                    logger.warning("Cell numbers between feature {} and feature {} differ: {} vs. {}".format(fg[0].featurename, f.featurename, f1_cells[i], fj_cells_i))
            except IndexError:
                logger.warning("Cell array sizes differ: {} vs. {}".format(fg[0].featurename, f.featurename))
