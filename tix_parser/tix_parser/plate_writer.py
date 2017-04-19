# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 18.04.17

import re
import logging
import numpy

from .utility import check_feature_group

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

__NA__ = "NA"


class PlateWriter:
    def __init__(self, layout):
        self._layout = layout

    _meta_ = ["well", "gene", "sirna", "well_type", "image_idx", "object_idx"]
    _well_regex = re.compile("(\w)(\d+)")

    def write(self, pfs, feature_groups, mapping):
        logger.info("Integrating the different feature sets to matrices for "
                    "plate file set: " + str(pfs.classifier))
        for k, v in feature_groups.items():
            self._write(pfs, k, v, mapping)
        return 0

    def _write(self, pfs, feature_group, features, mapping):
        features = sorted(features, key=lambda x: x.short_name)
        pathogen = pfs.pathogen
        library = pfs.library
        replicate = pfs.replicate
        screen = pfs.screen
        design = pfs.design
        plate = pfs.plate
        layout = self._layout.get(pathogen, library, design, screen,
                                  replicate, plate)
        if layout is None:
            logger.warning("Could not load layout for: " + pfs.classifier)
            return
        filename = pfs.outfile + "_" + feature_group
        try:
            self._write_file(filename, features, mapping, layout)
        except Exception as e:
            logger.error("Could not integrate: " + filename)
            logger.error(str(e))

    @staticmethod
    def _write_file(filename, features, mapping, layout):
        check_feature_group(features)
        meta = [None] * len(PlateWriter._meta_)
        logger.info("Writing to: " + filename)
        with open(filename, "w") as f:
            header = PlateWriter._meta_ + \
                     [feat.featurename.lower() for feat in features]
            f.write("\t".join(header) + "\n")
            nimg = features[0].values.shape[0]
            assert nimg == len(mapping)
            for iimg in range(nimg):
                well = mapping[iimg]
                meta[0] = well
                meta[1] = layout.gene(well)
                meta[2] = layout.sirna(well)
                meta[3] = layout.welltype(well)
                meta[4] = iimg + 1
                for cell in range(features[0].ncells[iimg]):
                    vals = [__NA__] * len(features)
                    for p in range(len(features)):
                        try:
                            vals[p] = features[p].values[iimg, cell]
                        except IndexError:
                            vals[p] = __NA__
                    meta[5] = cell + 1
                    f.write("\t".join(list(map(str, meta)) +
                                      list(map(str, vals))).lower() + "\n")
        return 0
