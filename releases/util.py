"""
Utility functions, such as helpers for standalone changelog parsing.
"""

from os import rmdir
from tempfile import mkdtemp

import sphinx
from sphinx.application import Sphinx # not exposed at top level

from . import generate_changelog, setup


def parse_changelog(path):
    """
    Load and parse changelog file from ``path``, returning data structures.

    This function does not alter any files on disk; it is solely for
    introspecting a Releases ``changelog.rst`` and programmatically answering
    questions like "are there any unreleased bugfixes for the 2.3 line?" or
    "what was included in release 1.2.1?".

    :param str path: A relative or absolute file path string.

    :returns: Stuff.
    """


def get_doctree(path):
    """
    Obtain a Sphinx doctree from the file at ``path``.

    Performs no Releases-specific processing; this code would, ideally, be in
    Sphinx itself, but things there are pretty tightly coupled. So we wrote
    this.

    :param str path: A relative or absolute file path string.

    :returns: Stuff.
    """
    import os
    root, filename = os.path.split(path)
    docname, _ = os.path.splitext(filename)
    # TODO: this only works for top level changelog files (i.e. ones where
    # their dirname is the project/doc root)
    app = make_app(srcdir=root)
    # Create a BuildEnvironment. Mm, tasty side effects.
    app._init_env(freshenv=True)
    build_env = app.env
    # Pretend our doc has been updated so BuildEnvironment.update() triggers a
    # .read_doc() of it (while the app is set; otherwise actual extensions like
    # Releases may not work, as they may reference it or its config).
    # TODO: how to actually fake the fact that a given doc needs updating?
    # TODO: may be worth actually just re-ripping out that chunk of
    # env.read_doc again now that we have a sorta-working env instance
    build_env.update(config=app.config, srcdir=root, doctreedir=app.doctreedir, app=app)

    # Code taken from sphinx.environment.read_doc; easier to manually call
    # it with a working Environment object, instead of doing more random crap
    # to trick the higher up build system into thinking our single changelog
    # document was "updated".
    build_env.temp_data['docname'] = docname
    build_env.app = app
    from sphinx.io import SphinxStandaloneReader, SphinxFileInput, SphinxDummyWriter
    from docutils.core import Publisher
    from docutils.io import NullOutput
    self = build_env # TODO: make explicit
    reader = SphinxStandaloneReader(self.app, parsers=self.config.source_parsers)
    pub = Publisher(reader=reader,
                    writer=SphinxDummyWriter(),
                    destination_class=NullOutput)
    pub.set_components(None, 'restructuredtext', None)
    pub.process_programmatic_settings(None, self.settings, None)
    # NOTE: docname derived higher up, from our given path
    src_path = self.doc2path(docname)
    source = SphinxFileInput(app, self, source=None, source_path=src_path,
                             encoding=self.config.source_encoding)
    pub.source = source
    pub.settings._source = src_path
    pub.set_destination(None, None)
    pub.publish()
    return pub.document


def make_app(**kwargs):
    """
    Create a dummy Sphinx app, filling in various hardcoded assumptions.

    For example, Sphinx assumes the existence of various source/dest
    directories, even if you're only calling internals that never generate (or
    sometimes, even read!) on-disk files. This function creates safe temp
    directories for these instances.

    It also neuters Sphinx's internal logging, which otherwise causes verbosity
    in one's own test output and/or debug logs.

    All args are stored in a single ``**kwargs``. Aside from the params listed
    below (all of which are optional), all kwargs given are turned into
    'releases_xxx' config settings; e.g. ``make_app(foo='bar')`` is like
    setting ``releases_foo = 'bar'`` in ``conf.py``.

    :param str docname:
        Override the document name used (mostly for internal testing).

    :param str srcdir:
        Sphinx source directory path.

    :param str dstdir:
        Sphinx dest directory path.

    :param str doctreedir:
        Sphinx doctree directory path.

    :returns: A Sphinx ``Application`` instance.
    """
    srcdir = kwargs.pop('srcdir', mkdtemp())
    dstdir = kwargs.pop('dstdir', mkdtemp())
    doctreedir = kwargs.pop('doctreedir', mkdtemp())
    try:
        Sphinx._log = lambda self, message, wfile, nonl=False: None
        app = Sphinx(
            srcdir=srcdir,
            confdir=None,
            outdir=dstdir,
            doctreedir=doctreedir,
            buildername='html',
        )
    finally:
        for d in (srcdir, dstdir, doctreedir):
            # Only remove empty dirs; non-empty dirs are implicitly something
            # that existed before we ran, and should not be touched.
            try:
                rmdir(d)
            except OSError:
                pass
    setup(app)
    # Mock out the config within. More assumptions by Sphinx :(
    config = {
        'releases_release_uri': 'foo_%s',
        'releases_issue_uri': 'bar_%s',
        'releases_debug': False,
        'master_doc': 'index',
    }
    # Allow tinkering with document filename
    if 'docname' in kwargs:
        app.env.temp_data['docname'] = kwargs.pop('docname')
    # Allow config overrides via kwargs
    for name in kwargs:
        config['releases_{0}'.format(name)] = kwargs[name]
    # Stitch together as the sphinx app init() usually does w/ real conf files
    app.config._raw_config = config
    # init_values() requires a 'warn' runner on Sphinx 1.3+, give it no-op.
    init_args = []
    if sphinx.version_info[:2] > (1, 2):
        init_args = [lambda x: x]
    app.config.init_values(*init_args)
    return app
