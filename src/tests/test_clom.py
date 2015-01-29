from clom import clom, AND, OR, STDERR

def test_clom():
    assert 'vagrant' == clom.vagrant
    assert 'vagrant --list ssh_config --help' == clom.vagrant.with_opts('--list').ssh_config.with_opts('--help')
    assert 'vagrant ssh_config extra' == clom.vagrant.ssh_config.extra

    assert 'fab --list' == clom.fab.with_opts(list=True)
    assert 'fab --list' == clom.fab.with_opts('--list')

    assert 'fab -i keyfile' == clom.fab(i='keyfile')
    assert 'fab -i keyfile' == clom.fab.with_opts('-i', 'keyfile')


    assert 'grep --file myfile.txt -m 2 \'*.pyc\' test.txt' == clom.grep.with_opts('--file', 'myfile.txt', m=2).with_args('*.pyc', 'test.txt')


    assert '( grep \'*.pyc\' test.txt && wc && cat )' == AND(clom.grep('*.pyc', 'test.txt'), clom.wc, clom.cat)

    bigcmd = OR(clom.grep('*.pyc', 'test.txt'), clom.wc, clom.cat).pipe_to(clom.wc)
    assert (
            '( grep \'*.pyc\' test.txt || wc || cat ) | wc' ==
            bigcmd ==
            OR(clom.grep('*.pyc', 'test.txt'), clom.wc, clom.cat) | clom.wc
    )

    assert 'grep >> test.txt' == clom.grep.append_to_file('test.txt')
    assert 'grep 2>> test.txt' == clom.grep.append_to_file('test.txt', STDERR)
    assert 'grep > test.txt' == clom.grep.output_to_file('test.txt')
    assert 'grep 2> test.txt' == clom.grep.output_to_file('test.txt', STDERR)
    assert 'grep > /dev/null' == clom.grep.hide_output()
    assert 'grep 2> /dev/null' == clom.grep.hide_output(STDERR)
    assert 'env foo=true ls' == clom.ls.with_env(foo='true')

def test_shell():
    assert 'foo' == clom.echo.shell('foo')
    assert 'foo' == clom.echo.shell.first('foo')

    r = clom.echo.shell('')
    assert 0 == r.return_code
    assert r.return_code == r.code    
    assert str(r) == ''
    assert r == ''
    assert r == r
    assert r == clom.echo.shell('')
    assert r.stdout == '\n'

    for i, line in enumerate(clom.echo.shell('a\nb\nc')):
        if i == 0:
            assert line == 'a'
        elif i == 1:
            assert line == 'b'
        elif i == 2:
            assert line == 'c'    
        else:
            raise AssertionError('Did not expect line %i: %r' % (i, line))

def test_piping():
    """
    Verify that piping several commands together behaves as expected.
    """
    cmd_ls = clom.ls.with_opts('-lah')
    cmd_ls._env = {}
    cmd_echo = clom.echo.with_opts("monkey", "gorilla")
    cmd_grep = clom.grep.with_opts('monkey')

    ls_pipe_echo = cmd_ls.pipe_to(cmd_echo)
    ls_pipe_echo_expected = 'ls -lah | echo monkey gorilla' 
    assert ls_pipe_echo_expected == str(ls_pipe_echo)

    ls_pipe_echo = cmd_ls | cmd_echo
    assert ls_pipe_echo_expected == str(ls_pipe_echo)

    ls_pipe_echo_pipe_grep = ls_pipe_echo.pipe_to(cmd_grep)
    ls_pipe_echo_pipe_grep_expected = ls_pipe_echo_expected + ' | grep monkey'
    assert ls_pipe_echo_pipe_grep_expected == str(ls_pipe_echo_pipe_grep)

    ls_pipe_echo_pipe_grep = ls_pipe_echo | cmd_grep
    assert ls_pipe_echo_pipe_grep_expected == str(ls_pipe_echo_pipe_grep)

def test_new_commands():
    """
    Verify that you can manually re-create a command instead of cloning it.
    """
    ls_cmd_a = clom.ls.with_opts('-r')
    ls_cmd_b = clom.ls.with_opts('-lah')
    assert str(ls_cmd_a) != str(ls_cmd_b)

    ls_cmd_x = clom.ls.with_env(foo='monkey')
    ls_cmd_y = clom.ls
    assert str(ls_cmd_x) != str(ls_cmd_y)

def test_sub_command():
    shell_stuff = r""" $`'" \ """
    echo = clom.echo(shell_stuff)
    assert str(echo) == r"""echo ' $`'\''" \ '"""
    assert echo.shell() == shell_stuff

    echo_twice = clom.echo(echo, shell_stuff)
    assert str(echo_twice) == r"""echo "$(echo ' $`'\''" \ ')" ' $`'\''" \ '"""

    assert str(echo_twice.shell()) == shell_stuff + ' ' + shell_stuff
