import re
import functools

def _makes_clone(f):
    """Mark a method as returning a clone."""

    @functools.wraps(f)
    def decorate(*args, **kw):
        self = args[0]._clone()
        f(self, *args[1:], **kw)
        return self

    return decorate

STDIN = 0
STDOUT = 1
STDERR = 2

NOT_SET = object()

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

    @see http://www.gnu.org/software/bash/manual/bashref.html#Single-Quotes
    """
    _find_unsafe = re.compile(r'[^\w\d@%_\-\+=:,\./]').search

    def __str__(self):
        """
        Wraps data in single quotes and escapes single quotes.

        Ex:

        don't interpolate this

        'don'\''t interpolate this
        """
        if isinstance(self.data, (int, long, float)):
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

    @see http://www.gnu.org/software/bash/manual/bashref.html#Double-Quotes
    """
    def __str__(self):
        if self.data is None:
            d = ''
        else:
            d = str(self.data)
            
        if ' ' in d:
            d = '"' + d + '"'

        return d

class Operation(object):
    def __init__(self):
        self._pipe_to = None
        self._redirects = {}
        self._env = {}
        self._background = False

    @_makes_clone
    def background(self):
        """
        Run the command in the background and don't block for output.

        @see http://www.gnu.org/software/bash/manual/bashref.html#Lists

        Ex:
        >>> clom.ls.background()
        'ls &'
        """
        self._background = True

    @_makes_clone
    def pipe_to(self, to_cmd):
        """
        Pipe this command to another.

        @see http://tldp.org/LDP/abs/html/io-redirection.html
        @see http://www.gnu.org/software/bash/manual/bashref.html#Pipelines

        Ex:
        >>> clom.ls.pipe_to(clom.grep)
        'ls | grep'
        """
        self._pipe_to = to_cmd

    @_makes_clone
    def append_to_file(self, filename, fd=STDOUT):
        """
        Append this command's output to a file.

        @see http://tldp.org/LDP/abs/html/io-redirection.html

        Ex:
        >>> clom.ls.append_to_file('list.txt')
        'ls >> list.txt'

        >>> clom.ls.append_to_file('list.txt', STDERR)
        'ls 2>> list.txt'
        """
        self._redirects[fd] = ('>>', filename)

    @_makes_clone
    def output_to_file(self, filename, fd=STDOUT):
        """
        Replace a file's contents with this command's output.

        @see http://tldp.org/LDP/abs/html/io-redirection.html

        Ex:
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

        @see http://tldp.org/LDP/abs/html/io-redirection.html

        Ex:
        >>> clom.cat.redirect(STDERR, STDOUT)
        'cat 2>&1'
        """
        self._redirects[from_fd] = ('>&', to_fd)

    @_makes_clone
    def hide_output(self, fd=STDOUT):
        """
        Redirect a command's file descriptors to /dev/null.

        @see http://tldp.org/LDP/abs/html/io-redirection.html

        Ex:
        >>> clom.cat.hide_output()
        'cat > /dev/null'

        >>> clom.cat.hide_output(STDERR)
        'cat 2> /dev/null'
        """
        self._redirects[fd] = ('>', '/dev/null')

    def __add__(self, right):
        """
        Combine Operation with a string or another Operation
        """
        if isinstance(right, basestring):
            return str(self) + right
        elif isinstance(right, Operation):
            return NotImplemented('TODO Not sure what to do here')
        else:
            raise TypeError()

    def __radd__(self, left):
        """
        Combine Operation with a string or another Operation
        """
        if isinstance(left, basestring):
            return left + str(self)
        elif isinstance(left, Operation):
            return NotImplemented('TODO Not sure what to do here')
        else:
            raise TypeError()

    def _escape_arg(self, arg):
        if isinstance(arg, Command):
            return '`%s`' % arg
        elif isinstance(arg, BaseArg):
            return str(arg)
        else:
            return str(LiteralArg(arg))

    def _build_redirects(self, s):
        """
        Adds any redirects to the command output.
        """
        for fd, (dir, output)  in self._redirects.iteritems():
            if fd == STDOUT:
                fd = ''
            if isinstance(output, (int, long)):
                s.append('%s%s%d' % (fd, dir, output))
            else:
                s.append('%s%s' % (fd, dir))
                s.append(self._escape_arg(output))

        if self._pipe_to:
            s.append('|')
            s.append(str(self._pipe_to))

    def _build_command(self, s):
        raise NotImplemented

    def __str__(self):
        """
        Build a string for the command suitable for using on the command line.
        """
        s = []

        if self._background:
            s.append('nohup')
            
        if self._env:
            s.append('/usr/bin/env')
            for k, v in self._env.iteritems():
                s.append('%s=%s' % (k, LiteralArg(v)))

        self._build_command(s)
        self._build_redirects(s)

        if self._background:
            s.append('&')

        return ' '.join(s)


    def __repr__(self):
        return '<%s `%s`>' % (self.__class__.__name__, self)


    def _clone(self):
        cls = self.__class__
        q = cls.__new__(cls)
        q.__dict__ = self.__dict__.copy()
        q._redirects = self._redirects.copy()

        return q

    def __eq__(self, other):
        if isinstance(other, basestring):
            return other == str(self)
        else:
            return other == self

    @_makes_clone
    def with_env(self, **kwargs):
        self._env.update(kwargs)

class Command(Operation):
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

        kwargs are computed as --name value or -n value

        args are passed in as is
        """
        self._listopts.extend(args)
        self._kwopts.update(kwargs)
        return self

    @_makes_clone
    def with_args(self, *args):
        """
        Arguments to call the command with.
        """
        self._args.extend(args)
        return self

    def __getattr__(self, name):
        """
        Get a sub command.

        Ex:
        >>> clom.fab.push
        'fab push'
        """
        parent = self._clone()
        return Command(self._clom, name, parent=parent)

    def __getitem__(self, name):
        return self.__getattr__(name)

    def _build_command(self, s):
        """
        Builds the raw command parts without any redirects, pipes, etc.
        """
        e = self._escape_arg

        if self._parent:
            s.append(str(self._parent))

        s.append(self.name)

        for opt in self._listopts:
            if opt is not NOT_SET:
                s.append(e(opt))

        for name, opt in self._kwopts.iteritems():
            if opt is not NOT_SET:
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

        for arg in self._args:
            if arg is not NOT_SET:
                s.append(e(arg))

    @_makes_clone
    def __call__(self, *args, **kwargs):
        """
        Shortcut for `command.with_opts(**kwargs).with_args(*args)`
        """
        self._kwopts.update(kwargs)
        self._args.extend(args)
        return self

    @_makes_clone
    def from_file(self, filename):
        """
        Read a file's contents with this command's stdin.

        @see http://tldp.org/LDP/abs/html/io-redirection.html

        Ex:
        >>> clom.cat.from_file('list.txt')
        'cat < list.txt'
        """
        self._redirects.append((STDIN, '<', filename))

    def _clone(self):
        q = super(Command, self)._clone()
        q._args = self._args[:]
        q._listopts = self._listopts[:]
        q._kwopts = self._kwopts.copy()

        return q

class BaseConjunction(Operation):
    operator = None

    def __init__(self, *commands):
        Operation.__init__(self)
        self.commands = commands

    def _build_command(self, s):
        s.append('(')
        s.append((' %s ' % self.operator).join((str(c) for c in self.commands)))
        s.append(')')

class AND(BaseConjunction):
    """
    Combine commands together that must execute together.

    Ex:

    >>> And(clom.echo('foo'), clom.echo('bar'))
    (echo 'foo' && echo 'bar')
    """
    operator = '&&'

class OR(BaseConjunction):
    """
    Combine commands together that must not execute together.

    Ex:

    >>> Or(clom.echo('foo'), clom.echo('bar'))
    (echo 'foo' || echo 'bar')
    """
    operator = '||'

class Clom(object):
    NOT_SET = NOT_SET
    
    def __init__(self):
        self._commands = {}

    def __getattr__(self, name):
        if name not in self._commands:
            self._commands[name] = Command(self, name)
        return self._commands[name]._clone()

    def __getitem__(self, name):
        return self.__getattr__(name)

clom = Clom()