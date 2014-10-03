from clom import clom
from fabric.api import local, task, abort, settings, puts
from fabric.colors import green
from fabric.contrib.console import confirm

@task
def release(version=None):
    """
    Release with git flow then release current version to pypi
    """
    with settings(warn_only=True):
        r = local(clom.git['diff-files']('--quiet', '--ignore-submodules', '--'))
        branch = str(local("git for-each-ref --format='%(refname:short)' `git symbolic-ref HEAD`", capture=True)).strip()

    if branch != 'develop':
        abort('You must be on the develop branch to start a release.')
    elif r.return_code != 0:
        abort('There are uncommitted changes, commit or stash them before releasing')

    if confirm('Must pull from origin to continue, pull now?'):     
        local(clom.git.pull('origin', 'develop'))
    else:
        abort('Aborted by user.')

    if not version:
        version = open('VERSION.txt').read().strip()
        if not confirm('Do you want to release as version `{version}`?'.format(version=version), default=False):
            abort('Aborted by user.')

    puts(green('Releasing %s...' % version))
    local(clom.git.flow.release.start(version))

    # Can't use spaces in git flow release messages, see https://github.com/nvie/gitflow/issues/98
    local(clom.git.flow.release.finish(version, m='Release-%s' % version))
    local(clom.git.push('origin', 'master', 'develop', tags=True))
    local(clom.python('setup.py', 'sdist', 'upload'))
