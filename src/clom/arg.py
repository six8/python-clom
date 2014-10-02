import re

from clom._compat import number_types

__all__ = [
    'NOTSET',
    'STDIN',
    'STDOUT',
    'STDERR',
    'RawArg',
    'LiteralArg',
]

#: Represents an argument that is not set as opposed to `None` which is a valid value
NOTSET = object()

#: Standard In file descriptor
STDIN = 0

#: Standard Out file descriptor
STDOUT = 1

#: Standard Error file descriptor
STDERR = 2


class BaseArg(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        raise NotImplemented

class RawArg(BaseArg):
    """
    A command line argument that is not escaped at all.
    """
    def __str__(self):
        return str(self.data)

class LiteralArg(BaseArg):
    """
    A command line argument that is fully escaped.

    Use this if you want the value to be maintained and not interpolated.

    Chars like * and $ are escaped and the value is wrapped in quotes.

    .. seealso:: http://www.gnu.org/software/bash/manual/bashref.html#Single-Quotes
    """
    _find_unsafe = re.compile(r'[^\w\d@%_\-\+=:,\./]').search

    def __str__(self):
        """
        Wraps data in single quotes and escapes single quotes.

        ::

            don't interpolate this

            'don'\''t interpolate this
            
        """
        if isinstance(self.data, number_types):
            return str(self.data)
        elif self.data is None or self.data == '':
            return "''"
        elif self._find_unsafe(self.data) is None:
            return self.data

        d = str(self.data)

        d = "'" + d.replace("'", "'\\''") + "'"
        return d

class Arg(BaseArg):
    """
    A command line argument that is minimally escaped.

    .. seealso:: http://www.gnu.org/software/bash/manual/bashref.html#Double-Quotes
    """
    def __str__(self):
        if self.data is None:
            d = ''
        else:
            d = str(self.data)

        if ' ' in d:
            d = '"' + d + '"'

        return d
  
