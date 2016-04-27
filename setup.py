#!/usr/bin/env python

from setuptools import setup

# Version info -- read without importing
_locals = {}
with open('releases/_version.py') as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']

setup(
    name='releases',
    version=version,
    description='A Sphinx extension for changelog manipulation',
    author='Jeff Forcier',
    author_email='jeff@bitprophet.org',
    url='https://github.com/bitprophet/releases',
    packages=['releases'],
    install_requires=['semantic_version<3.0'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
