from contextlib import contextmanager
from errors import CompilerError


class Scraps(object):
    def __init__(self, view):
        self._data = {}
        self._grabbed = set()
        self._active_fname = None
        self._view = view
        self._extra_consulted = []

    @contextmanager
    def move_to(self, fname: str):
        assert self._active_fname is None
        assert isinstance(fname, str)
        self._active_fname = fname
        try:
            self._view.add_to_scraps(self, fname)
            self._extra_consulted.append(fname)
            yield
        finally:
            self._active_fname = None

    def key(self, fkey):
        if self._active_fname is None:
            raise CompilerError(
                "trying to populate or consume scraps while not moved to anywhere"
            )
        return self._active_fname, fkey

    def list_all(self, include_grabbed=True):
        return [
            (fname, fkey, data)
            for (fname, fkey), data in self._data.items()
            if include_grabbed or ((fname, fkey) not in self._grabbed)
        ]

    def list_extra_consulted(self):
        return list(self._extra_consulted)

    def add(self, fkey, data):
        key = self.key(fkey)
        existing = self._data.get(key)

        if data.strip() == "":
            data = None

        if existing is not None and existing != data:
            raise CompilerError(
                "scrap already exists (is defined as {0}): cannot add contradictory definition as {1}".format(
                    existing, data
                )
            )

        if data is None:
            if key in self._data:
                del self._data[key]
        else:
            self._data[key] = data

    def grab(self, fkey):
        key = self.key(fkey)

        self._grabbed.add(key)
        return self._data.get(key, "")
