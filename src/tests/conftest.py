import doctest

import _pytest.doctest

from clom import clom, STDERR, STDIN, STDOUT, NOTSET

def monkeypatch_DoctestModule():
    """
    Ugly monkeypatch to make sure clom is available to all doctests when ran with py.test
    """
    old_runtest = _pytest.doctest.DoctestItem.runtest

    def new_runtest(self):
        self.dtest.globs.update({
            'clom': clom,
            'STDIN': STDIN,
            'STDOUT': STDOUT,
            'STDERR': STDERR,
            'NOTSET': NOTSET,
        })
        old_runtest(self)

    _pytest.doctest.DoctestItem.runtest = new_runtest

monkeypatch_DoctestModule()
