===========
Python Clom
===========

About
=====

Clom is a Python Command Line Object Mapper. It's intended to make generating generating commands and escaping arguments
easier for command line interaction. It's particularly useful when used with `Fabric <http://fabfile.org>`_ or ``subprocess``.

- `Clom on GitHub <http://github.com/six8/python-clom>`_
- `Clom on Pypi <http://pypi.python.org/pypi/clom>`_

Installation
============

Install with ``pip`` or ``easy_install``.

::

    pip install clom

Usage Examples
==============

Import::

	>>> from clom import clom

Build a command::


	>>> clom.echo("Don't test me")
	"echo 'Don'\\''t test me'"

Augment with arguments::

	>>> clom.ls.with_opts('-a', '-t', l=True).with_args('~/')
	'ls -a -t -l '~/''
	>>> clom.curl('http://dev.host', X='POST', data='message=hello')
	'curl -X POST --data message=hello http://dev.host'


Use sub commands::

	>>> clom.git.checkout('mybranch')
	'git checkout mybranch'

Execute with ease::

	>>> clom.ls.shell.all()
	['clom', 'clom.egg-info', 'docs', 'tests']

	>>> clom.git.status.shell('.').first()
	'# On branch master'

Iterate over results::

	>>> for path in clom.ls.shell():
	...     print path
	... 
	clom
	clom.egg-info
	docs
	tests

Handle errors::

	>>> clom.vagrant.up.shell()
	Traceback (most recent call last):
	  File "<console>", line 1, in <module>
	  File "/Users/mthornton/Dropbox/Projects/python-clom/src/clom/shell.py", line 164, in __call__
	    raise CommandError(status, stdout, stderr, 'Error while executing "%s" (%s):\n%s' % (cmd, status, stderr or stdout))
	CommandError: Error while executing "vagrant up" (3):
	No Vagrant environment detected. Run `vagrant init` to set one up.

Group commands::

	>>> from clom import AND, OR
	>>> OR(clom.vagrant.up, clom.echo('Vagrant up failed'))
	'( vagrant up || echo 'Vagrant up failed' )'
	>>> OR(clom.vagrant.up, clom.echo('Vagrant up failed')).shell()
	<clom.shell.CommandResult object at 0x10c4a85d0>
	>>> print OR(clom.vagrant.up, clom.echo('Vagrant up failed')).shell()
	No Vagrant environment detected. Run `vagrant init` to set one up.
	Vagrant up failed

Re-use commands::

	>>> vbox = clom.VBoxManage
	>>> vbox.list.runningvms
	'VBoxManage list runningvms'
	>>> vbox.list.runningvms.shell.all()
	['']
	>>> vbox.list.vms.shell.all()
	['"Windows Base" {949ec0af-92d0-4140-8a6c-36301ca6f695}']

Background tasks::

	>>> clom.VBoxHeadless.with_opts(startvm="Windows Base").background()
	'nohup VBoxHeadless --startvm 'Windows Base' &> /dev/null &'
	>>> clom.VBoxHeadless.with_opts(startvm="Windows Base").background().shell()
	<CommandResult return_code=0, stdout=0 bytes, stderr=0 bytes>

	>>> vbox.list.runningvms.shell.all()
	['"Windows Base" {949ec0af-92d0-4140-8a6c-36301ca6f695}']

Works great with fabric::

	>>> from fabric.api import run, local
	>>> local(clom.ls)
	[localhost] local: ls
	clom		clom.egg-info	docs		nohup.out	tests
	''

Can even create fab commands::

	>>> clom.fab.test('doctest', 'unit').deploy('dev')
	'fab test:doctest,unit deploy:dev'
	>>> clom.fab.with_opts('-a', hosts='dev.host').deploy.with_args('dev','test')
	'fab -a --hosts dev.host deploy:dev,test'


API Documentation
=================

.. toctree::
   :maxdepth: 2

   api


