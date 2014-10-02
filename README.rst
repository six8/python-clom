Clom is a Python Command Line Object Mapper. It's intended to make generating generating commands and escaping arguments
easier for command line interaction. It's particularly useful when used with `Fabric <http://fabfile.org>`_ or ``subprocess``.

- `Documentation <http://clom.rtfd.org>`_
- `Clom on GitHub <http://github.com/six8/python-clom>`_
- `Clom on Pypi <http://pypi.python.org/pypi/clom>`_

Installation
------------

Install with ``pip`` or ``easy_install``.

::

    pip install clom

Usage Examples
--------------

Import::

	>>> from clom import clom

Build a command::


	>>> clom.echo("Don't test me")
	'echo 'Don'\''t test me''

Augment with arguments::

	>>> clom.ls.with_opts('-a', '-t', l=True).with_args('~/')
	'ls -a -t -l '~/''
	>>> clom.curl('http://dev.host', X='POST', data='message=hello')
	'curl -X POST --data message=hello http://dev.host'


Use sub commands::

	>>> clom.git.checkout('mybranch')
	'git checkout mybranch'

Execute with ease::

	>>> clom.seq(5).shell.all()
	['1', '2', '3', '4', '5']

	>>> clom.seq.shell('5').first()
	'1'

Iterate over results::

	>>> for i in clom.seq(3).shell():
	...	print(i)
	... 
	1
	2
	3

Handle errors::

	>>> clom.touch('/not/a/thing').shell()      # doctest:+IGNORE_EXCEPTION_DETAIL
	Traceback (most recent call last):
          ...
        CommandError: Error while executing "touch /not/a/thing" (1):
	touch: cannot touch ‘/not/a/thing’: No such file or directory

Group commands::

	>>> from clom import AND, OR
	>>> OR(clom.vagrant.up, clom.echo('Vagrant up failed'))
	'( vagrant up || echo 'Vagrant up failed' )'
	>>> OR(clom.vagrant.up, clom.echo('Vagrant up failed')).shell()
	<CommandResult return_code=0, stdout=17 bytes, stderr=... bytes>
	>>> print(OR(clom.false, clom.echo('Vagrant up failed')).shell())
	Vagrant up failed

Re-use commands::

	>>> echo = clom.echo
	>>> echo.one.two
	'echo one two'
	>>> echo.three.four.shell.all()
	['three four']
	>>> echo.foo.bar.shell.all()
	['foo bar']

Background tasks::

	>>> clom.VBoxHeadless.with_opts(startvm="Windows Base").background()
	'nohup VBoxHeadless --startvm 'Windows Base' &> /dev/null &'
	>>> clom.VBoxHeadless.with_opts(startvm="Windows Base").background().shell()
	<CommandResult return_code=0, stdout=0 bytes, stderr=0 bytes>

Works great with fabric::

	>>> from fabric.api import run, local   	# doctest: +SKIP
	>>> local(clom.ls)				# doctest: +SKIP
	[localhost] local: ls
	clom		clom.egg-info	docs		nohup.out	tests
	''

Can even create fab commands::

	>>> clom.fab.test('doctest', 'unit').deploy('dev')
	'fab test:doctest,unit deploy:dev'
	>>> clom.fab.with_opts('-a', hosts='dev.host').deploy.with_args('dev','test')
	'fab -a --hosts dev.host deploy:dev,test'


See more examples and the API in the `Clom Documentation <http://clom.rtfd.org>`_

Running Tests
-------------

Test are run using pytest::

	pip install pytest fabfile

::

	python tests/runtests.py -v
