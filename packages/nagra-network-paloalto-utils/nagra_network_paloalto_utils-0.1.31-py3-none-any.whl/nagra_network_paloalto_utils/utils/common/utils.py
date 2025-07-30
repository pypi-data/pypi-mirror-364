import os

from nagra_panorama_api.restapi import PanoramaClient


# =================================================================
def iterflattenlist(data):
    if not isinstance(data, list):
        yield data
        return
    for x in data:
        yield from flattenlist(x)


def flattenlist(data):
    return list(iterflattenlist(data))


# =================================================================
def expanded(string):
    """
    WARNING: do pass untrusted string in a sensitive environment to this function

    Expand a string using environment variables
    e.g. if your current user is 'debian' then
        expanded("Hello $USER")
    should expand to "Hello debian"

    This can be used with click:
    @click.option(..., type=expanded)
    """
    return os.path.expandvars(string)


# =================================================================


class BaseRegistry:
    KEY = "@name"

    def __init__(self, url, api_key, verbose=False):
        self.client = PanoramaClient(url, api_key, verbose=verbose)
        self.refresh()

    def _find_by_name(self, name):
        return self._data.get(name)

    def find_by_name(self, name):
        if not isinstance(name, str):
            return self.find_by_names(name)
        return self._find_by_name(name)

    def find_by_names(self, names):
        return {n: self.find_by_name(n) for n in names}

    def find_missing(self, names):
        return [n for n in names if not self.find_by_name(n)]

    def refresh(self):
        self._data = {d[self.KEY]: d for d in self.get_data()}

    def get_data(self):
        raise Exception("get_data must be overrided")
        # return []


# =================================================================


def is_sorted(data, /, key=None):
    return data == sorted(data, key=key)


def is_unique(data, /, key=None):
    if key:
        return len(data) == len({key(d) for d in data})
    return len(data) == len(set(data))
