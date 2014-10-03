import subprocess
import time
import logging

from clom._compat import string_types

log = logging.getLogger(__name__)

__all__ = [
    'Shell',
    'CommandError',
    'CommandResult',
]

class CommandError(Exception):
    """
    An error returned from a shell command.
    """
    def __init__(self, return_code, stdout, stderr, message):
        super(CommandError, self).__init__(message)

        self.stdout = stdout
        self.stderr = stderr
        self.code = return_code
        self.return_code = return_code

class _AttributeString(str):
    """
    A string that you assign attributes to.
    """    

class CommandResult(object):
    """
    The result of a command execution.
    """
    def __init__(self, return_code, stdout='', stderr=''):
        self._stdout = stdout
        self._return_code = return_code
        self._stderr = stderr

    def __str__(self):
        return str(self._stdout)

    def __repr__(self):
        return '<CommandResult return_code=%s, stdout=%s bytes, stderr=%s bytes>' % (
            self._return_code, 
            len(self._stdout) if self._stdout else '0', 
            len(self._stderr) if self._stderr else '0'
        )

    @property
    def return_code(self):
        """
        Returns the status code returned from the command.
        """
        return self._return_code

    @property
    def code(self):
        """
        Alias to `return_code`
        """
        return self._return_code

    @property
    def stdout(self):
        """
        Returns the command's stdout as a string.
        """
        return str(self)
        
    @property
    def stderr(self):
        """
        Returns the command's stderr as a string.
        """        
        return self._stderr                

    def __iter__(self):
        """
        Iterate over the command results split by lines with whitespace
        stripped.
        """
        return self.iter(strip=True)

    def iter(self, strip=True):
        """
        Iterate over the command results split by lines with whitespace
        optionally stripped.

        :param strip: bool - Strip whitespace for each line
        """
        return (
            r.strip() for r in str(self).split('\n')
        )

    def first(self, strip=True):
        """
        Get the first line of the results.

        You can also get the return code::

            >>> r = CommandResult(2)
            >>> r.first().return_code
            2
               
        """
        s = _AttributeString(next(self.iter(strip=strip)))
        s.return_code = s.code = self.return_code
        return s

    def last(self, strip=True):
        """
        Get the last line of the results.

        You can also get the return code::

            >>> r = CommandResult(2)
            >>> r.last().return_code
            2

        """
        line = ''
        for line in self.iter(strip=strip):
            pass
        s = _AttributeString(line)
        s.return_code = s.code = self.return_code
        return s


    def all(self, strip=True):
        """
        Get all lines of the results as a list.
        """
        return list(self.iter(strip=strip))

    def __eq__(self, other):
        if isinstance(other, string_types):
            return other == str(self)
        else:
            return super(self.__class__, self).__eq__(other)

class Shell(object):
    """
    Easily run `Command`s on the system's shell.
    """
    def __init__(self, cmd):
        self._command = cmd

    def __call__(self, *args, **kwargs):
        """
        Execute the command on the shell and capture the results.

        :raises: CommandError
        :returns: CommandResult
                
        ::
        
            >>> str(clom.echo.shell('foo'))
            'foo'

        """

        if self._command.is_background:
            # Force command to not capture since it's backgrounding
            return self.execute(*args, **kwargs)

        cmd = self._command.as_string(*args, **kwargs)
        log.info('Executing command: %s' % cmd)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if self._command._encoding:
            stdout = stdout.decode(self._command._encoding)
            stderr = stderr.decode(self._command._encoding)
        status = p.returncode

        stdout = stdout.strip() if stdout else ''
        stderr = stderr.strip() if stderr else ''

        if status == 0:
            return CommandResult(status, stdout, stderr)
        else:
            raise CommandError(status, stdout, stderr, 'Error while executing "%s" (%s):\n%s' % (cmd, status, stderr or stdout))

    def first(self, *args, **kwargs):
        """
        Executes the command and returns the first line.

        Alias for `shell(...).first()`

        ::
        
            >>> str(clom.echo.shell.first('foo\\nfoobar'))
            'foo'
                    
        """
        return self(*args, **kwargs).first()

    def last(self, *args, **kwargs):
        """
        Executes the command and returns the last line.

        Alias for `shell(...).last()`

        ::
        
            >>> str(clom.echo.shell.last('foo\\nfoobar'))
            'foobar'

        """
        return self(*args, **kwargs).last()

    def all(self, *args, **kwargs):
        """
        Executes the command and returns a list of the lines of the result.

        Alias for `shell(...).all()`

        ::
        
            >>> str(clom.echo.shell.all('foo\\nfoobar'))
            "['foo', 'foobar']"
                    
        """
        return self(*args, **kwargs).all()

    def iter(self, *args, **kwargs):
        """
        Executes the command and returns an iterator of the results.

        Alias for `shell(...).iter()`
        """
        return self(*args, **kwargs).iter()

    def execute(self, *args, **kwargs):
        """
        Execute the command on the shell without capturing output.

        Use this if the result is very large or you do not care about the results.

        :raises: CommandError
        :returns: CommandResult
        """
        cmd = self._command.as_string(*args, **kwargs)
        log.info('Executing command (capture off): %s' % cmd)

        p = subprocess.Popen(cmd, shell=True, stdout=None, stderr=None)
        p.communicate()
        status = p.returncode

        if status == 0:
            return CommandResult(status, '', '')
        else:
            raise CommandError(status, '', '', 'Error while executing "%s" (%s): Error not captured, see console.' % (cmd, status))
