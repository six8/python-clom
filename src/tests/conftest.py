import pytest
import sys
import py

from _pytest import doctest
from clom import clom, STDERR, STDIN, STDOUT, NOTSET

def monkeypatch_DoctestModule():
    """
    Ugly monkeypath to make sure clom is available to all doctests when ran with py.test
    """
    old_runtest = doctest.DoctestModule.runtest

    def runtest(self):
        doctest = py.std.doctest
        if self.fspath.basename == "conftest.py":
            module = self.config._conftest.importconftest(self.fspath)
        else:
            module = self.fspath.pyimport()
        failed, tot = doctest.testmod(
            module, raise_on_error=True, verbose=0,
            optionflags=doctest.ELLIPSIS, extraglobs={
                'clom' : clom,
                'STDIN' : STDIN,
                'STDOUT' : STDOUT,
                'STDERR' : STDERR,
                'NOTSET' : NOTSET,
            })

    doctest.DoctestModule.runtest = runtest

monkeypatch_DoctestModule()