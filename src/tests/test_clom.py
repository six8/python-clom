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
    assert '( grep \'*.pyc\' test.txt || wc || cat ) | wc' == OR(clom.grep('*.pyc', 'test.txt'), clom.wc, clom.cat).pipe_to(clom.wc)

    assert 'grep >> test.txt' == clom.grep.append_to_file('test.txt')
    assert 'grep 2>> test.txt' == clom.grep.append_to_file('test.txt', STDERR)
    assert 'grep > test.txt' == clom.grep.output_to_file('test.txt')
    assert 'grep 2> test.txt' == clom.grep.output_to_file('test.txt', STDERR)
    assert 'grep > /dev/null' == clom.grep.hide_output()
    assert 'grep 2> /dev/null' == clom.grep.hide_output(STDERR)