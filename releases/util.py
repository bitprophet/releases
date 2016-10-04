"""
Utility functions, such as helpers for standalone changelog parsing.
"""

from shutil import rmtree
from tempfile import mkdtemp

import sphinx
from sphinx.application import Sphinx

from releases import setup as releases_setup # avoid unittest crap


def make_app(**kwargs):
    """
    Create a dummy Sphinx app, filling in various hardcoded assumptions.

    For example, Sphinx assumes the existence of various source/dest
    directories, even if you're only calling internals that never generate (or
    read!) on-disk files. This function creates safe temp directories for these
    instances.

    It also neuters Sphinx's internal logging, which otherwise causes verbosity
    in one's own test output and/or debug logs.

    ----

    Kwargs (w/ exception of ``docname``, which is used for document name if
    given) are turned into 'releases_xxx' config settings, so e.g.
    ``make_app(foo='bar')`` is like setting ``releases_foo = 'bar'`` in
    ``conf.py``.
    """
    src, dst, doctree = mkdtemp(), mkdtemp(), mkdtemp()
    try:
        # STFU Sphinx :(
        Sphinx._log = lambda self, message, wfile, nonl=False: None
        app = Sphinx(
            srcdir=src,
            confdir=None,
            outdir=dst,
            doctreedir=doctree,
            buildername='html',
        )
    finally:
        [rmtree(x) for x in (src, doctree)]
    releases_setup(app)
    # Mock out the config within. More horrible assumptions by Sphinx :(
    config = {
        'releases_release_uri': 'foo_%s',
        'releases_issue_uri': 'bar_%s',
        'releases_debug': False,
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
