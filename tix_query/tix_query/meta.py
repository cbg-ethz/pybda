# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


from pathlib import Path
import os.path
import yaml
import pandas
import re


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
        # study, bacteria, screen, design, ome, replicate, plate, feature =

        s = Meta._pattern_.match(file.replace("_meta.tsv", ""))
        print(s.groups())

        k = 2
        print (s)
        # with open(full_file, "r") as fh:
        #     meta = yaml.load(fh)
        #     print(meta["features"])
