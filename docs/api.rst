Clom API
========

clom
----

The main interface to clom is the clom object::

    >>> from clom import clom
    >>> clom.cat
    'cat'

Each attribute of the clom object is a ``clom.command.Command``.

.. automodule:: clom
    :members: AND, OR

    .. attribute:: clom

        Manager for generating commands.

    .. attribute:: NOTSET

        Represents an argument that is not set as opposed to ``None`` which is a valid value

    .. attribute:: STDIN

        Standard In file descriptor

    .. attribute:: STDOUT

        Standard Out file descriptor

    .. attribute:: STDERR

        Standard Error file descriptor

Commands
--------

.. autoclass:: clom.command.Command
    :members:
    :inherited-members:

.. autoclass:: clom.command.Operation
    :members:
   

Arguments
---------

.. autoclass:: clom.arg.RawArg
.. autoclass:: clom.arg.LiteralArg
