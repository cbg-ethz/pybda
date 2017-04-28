# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


from pathlib import Path
import os.path
import yaml
import re
import logging
from tix_query.tix_query.table import table
from tix_query.tix_query.table._table_file import TableFile

logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

logger = logging.getLogger(__name__)


class Meta:
    _file_features_pattern_ = re.compile(
            "(\w+)-(\w+)-(\w+)-(\w+)-(\w+)-(\d+)-(.*)_(\w+)")
    _features_ = "features"
    _elements_ = "elements"

    def __init__(self, path):
        if not Path(path).is_dir():
            raise ValueError(str(path) + "does not exist.")
        self._path = path
        self._table = table.Table()
        self._read_meta_files()

    def _read_meta_files(self):
        self._files = list(filter(
                lambda x: x.endswith("_meta.tsv"),
                [f for f in os.listdir(self._path)]
        ))
        for f in self._files:
            self._read_meta_file(f)

    def _read_meta_file(self, file):
        full_file = os.path.join(self._path, file)
        try:
            study, bacteria, library, design, ome, replicate, plate, feature = \
                Meta._file_features_pattern_.match(
                        file.replace("_meta.tsv", "")).groups()
            with open(full_file, "r") as fh:
                meta = yaml.load(fh)
            tablefile = TableFile(self._path, file, feature, meta[Meta._features_])
            self._add_to_meta(study, bacteria, library, design, replicate,
                              plate, meta, tablefile)
        except ValueError as e:
            logger.error("Could not match meta file {} and value {}"
                         .format(file, e, file))

    def _add_to_meta(self, study, pathogen, library, design,
                     replicate, plate, meta, file):
        self._table.add_file_descriptor(study, pathogen, library, design,
                                        replicate, plate, file)

        # add the elements 'gene'/'sirna'/'welltype' to maps
        for element in meta[Meta._elements_]:
            try:
                well, gene, sirna = element.split(";")[:3]
                self._table.add_element(gene, sirna, well, file)
            except Exception as e:
                logger.error("Could not match element {} and error {}"
                             .format(element, e))

    def get(self, **kwargs):
        return self._table.get(**kwargs)
