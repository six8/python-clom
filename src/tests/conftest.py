import doctest

import _pytest.doctest

from clom import clom, STDERR, STDIN, STDOUT, NOTSET

def monkeypatch_DoctestModule():
    """
    Ugly monkeypatch to make sure clom is available to all doctests when ran with py.test
    """
    def runtest(self):
        module = self.fspath.pyimport()
        doctest.testmod(
            module, raise_on_error=True, verbose=0,
            optionflags=doctest.ELLIPSIS, extraglobs={
                'clom': clom,
                'STDIN': STDIN,
                'STDOUT': STDOUT,
                'STDERR': STDERR,
                'NOTSET': NOTSET,
            })

    _pytest.doctest.DoctestItem.runtest = runtest

monkeypatch_DoctestModule()
