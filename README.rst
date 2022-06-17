|version| |python| |license| |ci| |coverage|

.. |version| image:: https://img.shields.io/pypi/v/releases
    :target: https://pypi.org/project/releases/
    :alt: PyPI - Package Version
.. |python| image:: https://img.shields.io/pypi/pyversions/releases
    :target: https://pypi.org/project/releases/
    :alt: PyPI - Python Version
.. |license| image:: https://img.shields.io/pypi/l/releases
    :target: https://github.com/bitprophet/releases/blob/main/LICENSE
    :alt: PyPI - License
.. |ci| image:: https://img.shields.io/circleci/build/github/bitprophet/releases/main
    :target: https://app.circleci.com/pipelines/github/bitprophet/releases
    :alt: CircleCI
.. |coverage| image:: https://img.shields.io/codecov/c/gh/bitprophet/releases
    :target: https://app.codecov.io/gh/bitprophet/releases
    :alt: Codecov


What is Releases?
=================

Releases is a `Sphinx <http://sphinx-doc.org>`_ extension designed to help you
keep a source control friendly, merge friendly changelog file & turn it into
useful, human readable HTML output. It's compatible with Python 3.6+, and may
work on Sphinx versions as far back as 1.8.x, though 4.x and up are
recommended and generally all we will support.

Specifically:

* The source format (kept in your Sphinx tree as ``changelog.rst``) is a
  stream-like timeline that plays well with source control & only requires one
  entry per change (even for changes that exist in multiple release lines).
* The output (when you have the extension installed and run your Sphinx build
  command) is a traditional looking changelog page with a section for every
  release; multi-release issues are copied automatically into each release.
* By default, feature and support issues are only displayed under feature
  releases, and bugs are only displayed under bugfix releases. This can be
  overridden on a per-issue basis.

Some background on why this tool was created can be found in `this blog post
<http://bitprophet.org/blog/2013/09/14/a-better-changelog/>`_.

For more documentation, please see http://releases.readthedocs.io. For a
roadmap, see the maintainer's `roadmap page
<http://bitprophet.org/projects#roadmap>`_.

.. note::
    You can install the development version via ``pip install -e
    git+https://github.com/bitprophet/releases/#egg=releases``.
