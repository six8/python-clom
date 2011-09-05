from distutils.core import setup

def main():
    setup(
        name = 'clom',
        packages=['clom'],
        package_dir = {'':'src'},
        version = '0.7',
        author='Mike Thornton',
        author_email='six8@devdetails.com',
        url='http://clom.readthedocs.org/',
        download_url='http://github.com/six8/python-clom',
        keywords=['command line', 'fabric'],
        license='MIT',
        description='Command Line Object Mapper. A library for building POSIX command line arguments, commands, and parameters. Very useful for Fabric tasks.',
        classifiers = [
            "Programming Language :: Python",
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Operating System :: POSIX",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: System :: System Shells",
            "Topic :: System :: Systems Administration",
        ],
        long_description=open('README.rst').read(),
    )

if __name__ == '__main__':
    main()