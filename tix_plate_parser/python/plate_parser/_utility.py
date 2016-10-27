# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 27/10/16

import scipy.io as spio


def load_matlab(file):
    matlab_matrix = spio.loadmat(file)
    return matlab_matrix["handles"][0][0][0][0][0][0][0][0][0][0]
