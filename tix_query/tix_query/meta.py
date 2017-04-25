# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


from pathlib import Path


class Meta:
    def __init__(self, path):
        if not Path(path).is_dir():
            raise ValueError(str(path) + "does not exist.")
