try:
    # Try to use decorator module as it gives better introspection of
    # decorated me
    from decorator import decorator
except ImportError:
    # No decorator package available. Create a no-op "decorator".
    def decorator(f):
        def decorate(_func):
            def inner(*args, **kwargs):
                return f(_func, *args, **kwargs)
            return inner
        return decorate

from clom import arg
from clom.shell import Shell
from clom._compat import string_types, integer_types, PY3

__all__ = [
    'Command',
    'Operation',
    'AND',
    'OR',
]

@decorator
def _makes_clone(_func, *args, **kw):
    """
    A decorator that returns a clone of the current clom object.
    """
    self = args[0]._clone()
    _func(self, *args[1:], **kw)
    return self

class Operation(object):
    """
    Base class for all command line operations, functions, commands, etc.
    """

    def __init__(self):
        self._pipe_to = []
        self._redirects = {}
        self._env = {}
        self._background = False
        self._shell = None
        if PY3:
            self._encoding = 'UTF-8'
        else:
            self._encoding = None

    @_makes_clone
    def background(self):
        """
        Run the command in the background and don't block for output.

        .. seealso:: http://www.gnu.org/software/bash/manual/bashref.html#Lists

        ::

            >>> clom.ls.background()
            'nohup ls &> /dev/null &'

        """
        self._background = True

    @property
    def is_background(self):
        return self._background

    @_makes_clone
    def pipe_to(self, to_cmd):
        """
        Pipe this command to another.

        :param to_cmd: Operation or Command to pipe to
        :returns: Operation

        .. seealso:: http://tldp.org/LDP/abs/html/io-redirection.html
        .. seealso:: http://www.gnu.org/software/bash/manual/bashref.html#Pipelines

        ::

            >>> clom.ls.pipe_to(clom.grep)
            'ls | grep'

        """
        self._pipe_to.append(to_cmd)

    @_makes_clone
    def append_to_file(self, filename, fd=arg.STDOUT):
        """
        Append this command's output to a file.

        :param filename: Filename to append to
        :param fd: File descriptor to redirect to file
        :returns: Operation

        .. seealso:: http://tldp.org/LDP/abs/html/io-redirection.html

        ::

            >>> clom.ls.append_to_file('list.txt')
            'ls >> list.txt'

            >>> clom.ls.append_to_file('list.txt', arg.STDERR)
            'ls 2>> list.txt'

        """
        self._redirects[fd] = ('>>', filename)

    @_makes_clone
    def output_to_file(self, filename, fd=arg.STDOUT):
        """
        Replace a file's contents with this command's output.

        :param filename: Filename to append to
        :param fd: File descriptor to redirect to file
        :returns: Operation

        .. seealso:: http://tldp.org/LDP/abs/html/io-redirection.html

        ::

            >>> clom.ls.output_to_file('list.txt')
            'ls > list.txt'

            >>> clom.ls.output_to_file('list.txt', STDERR)
            'ls 2> list.txt'

        """
        self._redirects[fd] = ('>', filename)


    @_makes_clone
    def redirect(self, from_fd, to_fd):
        """
        Redirect a command's file descriptors.

        :param from_fd: File descriptor to redirect from
        :param to_fd: File descriptor to redirect to
        :returns: Operation

        .. seealso:: http://tldp.org/LDP/abs/html/io-redirection.html

        ::

            >>> clom.cat.redirect(STDERR, STDOUT)
            'cat 2>&1'

        """
        self._redirects[from_fd] = ('>&', to_fd)

    @_makes_clone
    def hide_output(self, fd=arg.STDOUT):
        """
        Redirect a command's file descriptors to /dev/null.

        :param fd: File descriptor to redirect to /dev/null
        :returns: Operation

        .. seealso:: http://tldp.org/LDP/abs/html/io-redirection.html

        ::

            >>> clom.cat.hide_output()
            'cat > /dev/null'

            >>> clom.cat.hide_output(STDERR)
            'cat 2> /dev/null'

        """
        self._redirects[fd] = ('>', '/dev/null')

    def __add__(self, right):
        """
        Combine Operation with a string or another Operation

        ::

            >>> clom.echo('test') + ' > test.txt'
            'echo test > test.txt'

        """
        if isinstance(right, string_types):
            return str(self) + right
        elif isinstance(right, Operation):
            # TODO
            return NotImplemented('TODO Not sure what to do here yet')
        else:
            raise TypeError('Can not add Operation and %r' % right)

    def __radd__(self, left):
        """
        Combine Operation with a string or another Operation

        ::

            >>> 'cat test.txt | ' + clom.echo
            'cat test.txt | echo'

        """
        if isinstance(left, string_types):
            return left + str(self)
        elif isinstance(left, Operation):
            # TODO
            return NotImplemented('TODO Not sure what to do here yet')
        else:
            raise TypeError('Can not add Operation and %r' % left)

    def _escape_arg(self, val):
        if isinstance(val, Command):
            return '`%s`' % arg
        elif isinstance(val, arg.BaseArg):
            return str(val)
        else:
            return str(arg.LiteralArg(val))

    def _build_redirects(self, s):
        """
        Adds any redirects to the command output.
        """
        for fd, (dir, output)  in self._redirects.items():
            if dir in ('>', '>>') and fd == arg.STDOUT:
                fd = ''
            elif dir in ('<', '<<') and fd == arg.STDIN:
                fd = ''

            if isinstance(output, integer_types):
                s.append('%s%s%d' % (fd, dir, output))
            else:
                s.append('%s%s' % (fd, dir))
                s.append(self._escape_arg(output))

        for c in self._pipe_to:
            s.append('|')
            s.append(str(c))

    def _build_command(self, s):
        raise NotImplemented('Must implement _build_command in base class')

    def __str__(self):
        """
        Build a string for the command suitable for using on the command line.
        """
        s = []

        if self._background:
            s.append('nohup')
            
        if self._env:
            s.append('env')
            for k, v in self._env.items():
                s.append('%s=%s' % (k, arg.LiteralArg(v)))

        self._build_command(s)
        self._build_redirects(s)

        if self._background:
            s.append('&> /dev/null &')

        return ' '.join(s)


    def __repr__(self):
        return "'%s'" % self


    def _clone(self):
        """
        Clones the state of the current operation.

        The state is cloned so that you can freeze the state at a certain point for re-use.

        ::

            >>> cat = clom.cat
            >>> cat.with_args('test.txt')
            'cat test.txt'
            >>> o = cat.with_opts(n=1)
            >>> o('test.txt')
            'cat -n 1 test.txt'
            >>> o('test2.txt')
            'cat -n 1 test2.txt'

        """
        cls = self.__class__
        q = cls.__new__(cls)
        q.__dict__ = self.__dict__.copy()
        q._redirects = self._redirects.copy()
        q._env = self._env.copy()

        return q

    def __eq__(self, other):
        if isinstance(other, string_types):
            return other == str(self)
        else:
            return super(self.__class__, self).__eq__(other)

    @_makes_clone
    def with_env(self, **kwargs):
        """
        Run the operation with environmental variables.

        :param kwargs: dict - Environmental variables to run command with
        """
        self._env.update(kwargs)

    @property
    def shell(self):
        """
        Returns a `Shell` that will allow you to execute commands on the
        shell.
        """
        if not self._shell:
            self._shell = Shell(self)
        return self._shell

    def as_string(self):
        """
        :returns: str - Command suitable to pass to the command line
        """
        return str(self)


class Command(Operation):
    """
    A command line command.

    Don't use directly, instead use a clom object.

    ::

        >>> from clom import clom
        >>> type(clom.cat)
        <class 'clom.command.Command'>

    """
    def __init__(self, clom, name, parent=None):
        Operation.__init__(self)

        self.name = name

        self._clom = clom        

        # Parent command
        self._parent = parent

        # Keyword options
        self._kwopts = {}

        # List options
        self._listopts = []

        # Arguments to pass to the command line
        self._args = []

    @_makes_clone
    def with_opts(self, *args, **kwargs):
        """
        Options to call the command with.

        :param kwargs: A dictionary of options to pass to the command.
                       Keys are generated as `--name value` or `-n value` depending on the length.
        :param args: A list of options to pass to the command.
                     Args are only escaped, no other special processing is done.
        :returns: Command


        ::

            >>> clom.curl.with_opts('--basic', f=True, header='X-Test: 1')
            'curl --basic --header \'X-Test: 1\' -f'

        """
        self._listopts.extend(args)
        self._kwopts.update(kwargs)
        return self

    @_makes_clone
    def with_args(self, *args):
        """
        Arguments to call the command with.

        :param args: A list of arguments to pass to the command.
                     Arguments are by automatically escaped as a `clom.arg.LiteralArg` unless you
                     pass in a `clom.arg.RawArg`.
        :returns: Command

        ::

            >>> clom.echo("don't test me")
            'echo \'don\'\\\'\'t test me\''

        """
        self._args.extend(args)
        return self

    def __getattr__(self, name):
        """
        Get a sub command.

        ::

            >>> clom.git.status
            'git status'

        """
        parent = self._clone()
        return Command(self._clom, name, parent=parent)

    def __getitem__(self, name):
        """
        Get a sub command by dictionary-like key.

        Useful if the command has spaces or other special characters.

        ::

            >>> clom.git['status']
            'git status'

        """
        return self.__getattr__(name)

    def _build_command(self, s):
        """
        Builds the raw command parts without any redirects, pipes, etc.
        """
        e = self._escape_arg

        if self._parent:
            s.append(str(self._parent))

        self._build_action(s)

        for opt in self._listopts:
            if opt is not arg.NOTSET:
                s.append(e(opt))

        for name, opt in sorted(self._kwopts.items()):
            if opt is not arg.NOTSET:
                if not name.startswith('-'):
                    if len(name) == 1:
                        name = '-%s' % name
                    else:
                        name = '--%s' % name

                s.append(str(name))

                if opt is True:
                    # Do nothing, assume they just wanted `--name`
                    pass
                elif opt is False:
                    raise ValueError('Keyword options such as %r can not have False values' % name)
                else:
                    s.append(e(opt))

        self._build_args(s)

    def _build_action(self, s):
        s.append(self._escape_arg(self.name))

    def _build_args(self, s):
        for val in self._args:
            if val is not arg.NOTSET:
                s.append(self._escape_arg(val))

    @_makes_clone
    def __call__(self, *args, **kwargs):
        """
        Shortcut for `command.with_opts(**kwargs).with_args(*args)`

        :returns: str - Command suitable to pass to the command line
        """
        self._kwopts.update(kwargs)
        self._args.extend(args)
        return self

    def as_string(self, *args, **kwargs):
        """
        Shortcut for `command.with_opts(**kwargs).with_args(*args)`

        :returns: str - Command suitable to pass to the command line
        """
        c = self._clone()
        c._kwopts.update(kwargs)
        c._args.extend(args)
        return str(c)

    @_makes_clone
    def from_file(self, filename):
        """
        Read a file's contents with this command's stdin.

        :param filename: The filename to read input from
        :returns: Command
        
        .. seealso:: http://tldp.org/LDP/abs/html/io-redirection.html

        ::

            >>> clom.cat.from_file('list.txt')
            'cat < list.txt'

        """
        self._redirects[arg.STDIN] = ('<', filename)

    def _clone(self):
        q = super(Command, self)._clone()
        q._args = self._args[:]
        q._listopts = self._listopts[:]
        q._kwopts = self._kwopts.copy()
        q._pipe_to = self._pipe_to[:]

        return q

class BaseConjunction(Operation):
    operator = None

    def __init__(self, *commands):
        """
        :param commands: List of Commands or Operations to combine
        """
        Operation.__init__(self)
        self.commands = commands

    def _build_command(self, s):
        s.append('(')
        s.append((' %s ' % self.operator).join((str(c) for c in self.commands)))
        s.append(')')

class AND(BaseConjunction):
    """
    Combine commands together that must execute together.

    :param commands: List of Commands or Operations to combine

    ::
    
        >>> from clom import clom
        >>> AND(clom.echo('foo'), clom.echo('bar'))
        '( echo foo && echo bar )'

    """
    operator = '&&'

class OR(BaseConjunction):
    """
    Combine commands together that must not execute together.

    :param commands: List of Commands or Operations to combine

    ::

        >>> from clom import clom
        >>> OR(clom.echo('foo'), clom.echo('bar'))
        '( echo foo || echo bar )'

    """
    operator = '||'

if __name__ == '__main__':
    import doctest
    from clom import clom
    doctest.testmod(extraglobs={'clom' : clom})
