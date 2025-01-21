from pickle import load, dump
from pathlib import Path


class DepGraph():
    '''
    Dependency graph using pickle to cache
    '''


    def __init__(self, cache_file):
        self.cache_file = cache_file

        try:
            with open(self.cache_file, 'rb') as f:
                self.deps = load(f)
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


    def save(self):
        try:
            with open(self.cache_file, 'wb') as f:
                dump(self.deps, f)
        except FileNotFoundError:
            p = Path(self.cache_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                dump(self.deps, f)
