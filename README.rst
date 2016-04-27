.. image:: https://secure.travis-ci.org/bitprophet/releases.png?branch=master
        :target: https://travis-ci.org/bitprophet/releases

What is Releases?
=================

Releases is a Python 2+3 compatible `Sphinx <http://sphinx-doc.org>`_ extension
designed to help you keep a source control friendly, merge friendly changelog
file & turn it into useful, human readable HTML output.

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

For more documentation, please see http://releases.readthedocs.io.

.. note::
    You can install the `development version
    <https://github.com/bitprophet/releases/tarball/master#egg=releases-dev>`_
    via ``pip install releases==dev``.
