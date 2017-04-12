# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 17/11/16


import re
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

__screen_regex__ = re.compile("^(\S+-?\S+)-(\w+)-(\w)(\w)-(\w+)(\d+)(-(.*))?$")
__screen_plate_regex__ = re.compile(".*/(.*)/.*/(.*)/(.*)/.*/.*/.+mat?$")
__NA__ = "NA"


def parse_screen_details(screen):
    """
    Parse a screen into an array of substrings, each being a detail of the
    screen:
    study, pathogen,
    library,
    design, screen, replicate, suffix

    :param screen: a screen string, such as "GROUP_COSSART-LISTERIA-DP-G1" or "GROUP_COSSART-LISTERIA-DP-G1-SUFFIX"
    :return: returns an array of details
    """
    try:
        pat = __screen_regex__.match(screen.lower())
        if pat is None:
            return [None] * 7
        return pat.group(1), pat.group(2), pat.group(3), pat.group(4), \
               pat.group(5), pat.group(6), \
               pat.group(8) if pat.group(8) is not None else __NA__
    except AttributeError:
        logger.warn("Could not parse: " + str(screen))
        return None


def parse_plate_info(mat_file):
    """
    Takes the absolut path of a matlab file and parses the screen name and

    the plate name from it
    :param mat_file: the absolute filename of a matlab file
    :return: returns an array of screenname and plate name
    """
    ret = __screen_plate_regex__.match(mat_file)
    return ret.group(1) + "-" + ret.group(2), ret.group(3)
