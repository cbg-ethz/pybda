# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 18.04.17


import logging
import numpy

from .utility import check_feature_group

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

__NA__ = "NA"


class PlateWriter:
    def _integrate_platefileset(self, platefileset, features, mapping):
        """
        Iterate over all matlab files and create the final matrices

        :param platefileset: the platefile set
        :param features: the parsed feature map

        """
        logger.info("Integrating the different feature sets to matrices for "
                    "plate file set: " + str(platefileset.classifier))
        # since some features have different numbers of objects
        for k, v in features.items():
            self._integrate_feature(platefileset, k, v, mapping)
        return 0

    def _integrate_feature(self, pfs, feature_group, features,
                           mapping):
        features = sorted(features, key=lambda x: x.short_name)
        pathogen = pfs.pathogen
        library = pfs.library
        replicate = pfs.replicate
        screen = pfs.screen
        design = pfs.design
        plate = pfs.plate
        layout = self._layout.get(pathogen, library, design,
                                  screen, replicate, plate)
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
        meta = [None] * len(PlateParser._meta_)
        logger.info("Writing to: " + filename)
        with open(filename, "w") as f:
            header = PlateParser._meta_ + \
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
                    # this is critical
                    # prolly source of errors
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