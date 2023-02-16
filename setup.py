#!/usr/bin/env python

from setuptools import setup

# Version info -- read without importing
_locals = {}
with open("releases/_version.py") as fp:
    exec(fp.read(), None, _locals)
version = _locals["__version__"]

setup(
    name="releases",
    version=version,
    description="A Sphinx extension for changelog manipulation",
    long_description=open("README.rst").read(),
    author="Jeff Forcier",
    author_email="jeff@bitprophet.org",
    url="https://github.com/bitprophet/releases",
    project_urls={
        "Docs": "https://releases.readthedocs.io",
        "Source": "https://github.com/bitprophet/releases",
        "Changelog": "https://releases.readthedocs.io/en/latest/changelog.html",  # noqa
        "CI": "https://app.circleci.com/pipelines/github/bitprophet/releases",
    },
    packages=["releases"],
    install_requires=[
        # We mostly still work on Sphinx>=1.8, but a number of transitive
        # dependencies do not, and trying to square that circle is definitely
        # not worth the effort at this time. PRs that can pass the entire test
        # matrix are welcome, if you disagree!
        "sphinx>=4",
        # Continuing to pin an old semantic_version until I have time to update
        # and finish the branch I made for
        # https://github.com/bitprophet/releases/pull/86#issuecomment-580037996
        "semantic_version<2.7",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development",
        "Topic :: Software Development :: Documentation",
        "Topic :: Documentation",
        "Topic :: Documentation :: Sphinx",
    ],
)
