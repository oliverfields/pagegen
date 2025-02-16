from os.path import join
from pagegen.Common import Common
from pathlib import Path
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class DepGraph(Common):
    '''
    Dependency graph using pickle to cache
    '''


    def __init__(self, cache_dir, cache_file):
        self.cache_dir = cache_dir
        self.cache_file = cache_file
        self.cache_path = join(cache_dir, cache_file)

        try:
            logger.debug('Loading dependency graph from file: ' + self.cache_path)
            self.deps = self.load_pickle(self.cache_path)
        except FileNotFoundError:
            self.deps = {}


    def add(self, dep_path, deps_to_path):
        '''
        Add dependencies to the graph
        '''

        if isinstance(deps_to_path, str):
            deps_to_path = [ deps_to_path ]

        if not dep_path in self.deps.keys():
            self.deps[dep_path] = []

        for dep in deps_to_path:
            if not dep in self.deps[dep_path]:
                self.deps[dep_path].append(dep)


    def write_cache(self):
        self.pickle_object(self.cache_dir, self.cache_file, self.deps)
