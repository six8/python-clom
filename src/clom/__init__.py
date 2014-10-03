from clom.arg import NOTSET, STDIN, STDOUT, STDERR
from clom.command import Command, AND, OR
from clom.fabric import FabCommand

__all__ = [
    'clom',
    'STDIN',
    'STDOUT',
    'STDERR',
    'NOTSET',
    'AND',
    'OR',
]

class Clom(object):
    """
    Manager for generating commands.
    """
    NOTSET = NOTSET

    def __init__(self):
        self._commands = {
            'fab' : FabCommand(self, 'fab')
        }

    def __getattr__(self, name):
        """
        Get a command.

        ::

            >>> clom.cat
            'cat'

        """
        if name not in self._commands:
            self._commands[name] = Command(self, name)
        return self._commands[name]._clone()

    def __getitem__(self, name):
        """
        Get a command by dictionary-like key.

        Useful if the command has spaces or other special characters.

        ::

            >>> clom['cat']
            'cat'

        """
        return self.__getattr__(name)

clom = Clom()
