from setuptools import setup, find_packages, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'tests/runtests.py'])
        raise SystemExit(errno)

def main():
    setup(
        name = 'clom',
        version = '0.7',
        packages=find_packages('src'),
        zip_safe=False,
        install_requires = [],
        tests_require = ['pytest'],
        package_dir = {'':'src'},
        cmdclass = {'test': PyTest},
    )

if __name__ == '__main__':
    main()