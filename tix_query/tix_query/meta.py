# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


from pathlib import Path
import os.path
import yaml
import pandas
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s'
)

logger = logging.getLogger(__name__)


class Meta:
    _pattern_ = re.compile("(\w+)-(\w+)-(\w+)-(\w+)-(\w+)-(\d+)-(.*)_(\w+)")

    def __init__(self, path):
        if not Path(path).is_dir():
            raise ValueError(str(path) + "does not exist.")
        self._path = path
        self._table = None
        self._read_meta_files()

    def _read_meta_files(self):
        self._files = list(filter(
            lambda x: x.endswith("_meta.tsv"),
            [f for f in os.listdir(self._path)]
        ))
        for f in self._files:
            self._read_meta_file(f)
            exit(0)

    def _read_meta_file(self, file):
        print(file)
        full_file = os.path.join(self._path, file)
        try:
            study, bacteria, screen, design, ome, replicate, plate, feature = \
                Meta._pattern_.match(file.replace("_meta.tsv", "")).groups()
            with open(full_file, "r") as fh:
                meta = yaml.load(fh)
                self._add_to_meta(study,
                                  bacteria,
                                  screen,
                                  design,
                                  ome,
                                  replicate,
                                  plate,
                                  feature,
                                  meta)
        except ValueError as e:
            logger.error(
                "Could not match meta file {}, with error {}".format(file, e)
            )

    def _add_to_meta(self,
                     study, bacteria, screen,
                     design, ome, replicate,
                     plate, feature, meta):
        pass
