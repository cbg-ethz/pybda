# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


from pathlib import Path
import os.path
import yaml
import re
import logging

from tix_query.tix_query.result_set import ResultSet
from tix_query.tix_query.filesets import table_file_sets
from tix_query.tix_query.filesets.table_file import TableFile

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

logger = logging.getLogger(__name__)


class Meta:
    _file_features_pattern_ = re.compile(
      "(\w+)-(\w+)-(\w+)-(\w+)-(\w+)-(\d+)-(.*)_(\w+)")
    _features_ = "features"
    _elements_ = "elements"
    _sample_ =  "sample"

    def __init__(self, path):
        if not Path(path).is_dir():
            raise ValueError(str(path) + "does not exist.")
        # path containing meta files
        self._path = path
        # filesets of meta files
        self._table = table_file_sets.TableFileSets()
        self._read_meta_files()

    def get(self, sample=None, **kwargs):
        """
        Get a lazy file result set from some filtering criteria and a fixed 
        sample size.
        
        :param sample: the number of objects to sample 
         (i.e. bacteria/cells/nuclei/...)
        :param kwargs: the filtering criteria. 
        :return: 
        """
        fls = self._table.filter(**kwargs)
        return ResultSet(fls, sample, **kwargs)

    def _read_meta_files(self):
        """
        Read the meta files from self._path and parse them into meta files
         
        """

        # get files ending with meta suffix
        self._files = \
            list(
              filter(
                lambda x: x.endswith("_meta.tsv"),
                [f for f in os.listdir(self._path)]
              )
            )
        # add every file to the meta map
        for f in self._files:
            self._read_meta_file(f)

    def _read_meta_file(self, file):
        """
        Read a single meta file and add to meta
        
        :param file: a meta file
        """

        # paste file name with paste
        full_file = os.path.join(self._path, file)
        try:
            # parse file name meta information
            study, bacteria, library, design,\
            ome, replicate, plate, feature = \
                Meta._file_features_pattern_ \
                    .match(file.replace("_meta.tsv", "")) \
                    .groups()

            # read the meta file
            with open(full_file, "r") as fh:
                meta = yaml.load(fh)
                # create a meta file TableFile
                tablefile = TableFile(
                  self._path,
                  file,
                  feature,
                  meta[Meta._features_])

            # add the filesets file to the meta map
            self._add_to_meta(study, bacteria, library,
                              design, replicate,
                              plate, meta, tablefile)
        except ValueError as e:
            logger.error("Could not match meta file {} and value {}"
                         .format(file, e, file))

    def _add_to_meta(self, study, pathogen, library, design,
                     replicate, plate, meta, file):

        # add the file to fileset
        self._table.add_to_fileset(file)

        # add file-name meta information to the meta map
        # this is taken from the file names
        self._table.add_file_descriptor(
          study, pathogen,
          library, design,
          replicate, plate, file
        )

        # add the elements 'gene'/'sirna'/'welltype' to maps
        # this is from the file contents
        for element in meta[Meta._elements_]:
            try:
                well, gene, sirna = element.split(";")[:3]
                self._table.add_element(gene, sirna, well, file)
            except Exception as e:
                logger.error("Could not match element {} and error {}"
                             .format(element, e))

