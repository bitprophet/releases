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
    long_description=open("README.rst").read(),
    author='Jeff Forcier',
    author_email='jeff@bitprophet.org',
    url='https://github.com/bitprophet/releases',
    packages=['releases'],
    install_requires=[
        'semantic_version<2.7',
        'sphinx>=1.3',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Documentation',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
    ],
)
