# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperimentMetaLoader:
    """
    Class that loads the experiment meta files from an open-bis instance

    """

    def __init__(self, uri, user, pw):
        """
        Constructor for the meta file loader from an open-bis instance.

        :param uri: the open-bis instance
        """
        self._uri = uri
        self._pw = pw
        self._user = user
        self._experiments = self._load()

    def _load(self):
        import jsonrpclib
        server = jsonrpclib.Server(self._uri)
        session_token = server.tryToAuthenticateForAllServices(self._user,
                                                               self._pw)
        projects = server.listProjects(session_token)
        experiment_type = 'HCS_ANALYSIS_CELL_FEATURES_CC_MAT'

        experiments = server.listExperiments(session_token,
                                             projects,
                                             experiment_type)
        for experiment in experiments:
            print(experiment['code'])
        return None
