# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24.04.17


from tix_query.tix_query.meta import Meta


class Query:
    def __init__(self, path):
        self.__meta = Meta(path)


if __name__ == "__main__":
    path = "/Users/simondi/PROJECTS/target_infect_x_project/data/target_infect_x/screening_data"
    q = Query(path)