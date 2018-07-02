"""
Utility functions, such as helpers for standalone changelog parsing.
"""

import logging
import os
from tempfile import mkdtemp

import sphinx
from docutils.core import Publisher
from docutils.io import NullOutput
from docutils.nodes import bullet_list
from sphinx.application import Sphinx # not exposed at top level
try:
    from sphinx.io import (
        SphinxStandaloneReader, SphinxFileInput, SphinxDummyWriter,
    )
except ImportError:
    # NOTE: backwards compat with Sphinx 1.3
    from sphinx.environment import (
        SphinxStandaloneReader, SphinxFileInput, SphinxDummyWriter,
    )
# sphinx_domains is only in Sphinx 1.5+, but is presumably necessary from then
# onwards.
try:
    from sphinx.util.docutils import sphinx_domains
except ImportError:
    # Just dummy it up.
    from contextlib import contextmanager
    @contextmanager
    def sphinx_domains(env):
        yield

from . import construct_releases, setup


def parse_changelog(path, **kwargs):
    """
    Load and parse changelog file from ``path``, returning data structures.

    This function does not alter any files on disk; it is solely for
    introspecting a Releases ``changelog.rst`` and programmatically answering
    questions like "are there any unreleased bugfixes for the 2.3 line?" or
    "what was included in release 1.2.1?".

    For example, answering the above questions is as simple as::

        changelog = parse_changelog("/path/to/changelog")
        print("Unreleased issues for 2.3.x: {}".format(changelog['2.3']))
        print("Contents of v1.2.1: {}".format(changelog['1.2.1']))

    Aside from the documented arguments, any additional keyword arguments are
    passed unmodified into an internal `get_doctree` call (which then passes
    them to `make_app`).

    :param str path: A relative or absolute file path string.

    :returns:
        A dict whose keys map to lists of ``releases.models.Issue`` objects, as
        follows:

        - Actual releases are full version number keys, such as ``"1.2.1"`` or
          ``"2.0.0"``.
        - Unreleased bugs (or bug-like issues; see the Releases docs) are
          stored in minor-release buckets, e.g. ``"1.2"`` or ``"2.0"``.
        - Unreleased features (or feature-like issues) are found in
          ``"unreleased_N_feature"``, where ``N`` is one of the major release
          families (so, a changelog spanning only 1.x will only have
          ``unreleased_1_feature``, whereas one with 1.x and 2.x releases will
          have ``unreleased_1_feature`` and ``unreleased_2_feature``, etc).

    .. versionchanged:: 1.6
        Added support for passing kwargs to `get_doctree`/`make_app`.
    """
    app, doctree = get_doctree(path, **kwargs)
    # Have to semi-reproduce the 'find first bullet list' bit from main code,
    # which is unfortunately side-effect-heavy (thanks to Sphinx plugin
    # design).
    first_list = None
    for node in doctree[0]:
        if isinstance(node, bullet_list):
            first_list = node
            break
    # Initial parse into the structures Releases finds useful internally
    releases, manager = construct_releases(first_list.children, app)
    ret = changelog2dict(releases)
    # Stitch them together into something an end-user would find better:
    # - nuke unreleased_N.N_Y as their contents will be represented in the
    # per-line buckets
    for key in ret.copy():
        if key.startswith('unreleased'):
            del ret[key]
    for family in manager:
        # - remove unreleased_bugfix, as they are accounted for in the per-line
        # buckets too. No need to store anywhere.
        manager[family].pop('unreleased_bugfix', None)
        # - bring over each major family's unreleased_feature as
        # unreleased_N_feature
        unreleased = manager[family].pop('unreleased_feature', None)
        if unreleased is not None:
            ret['unreleased_{}_feature'.format(family)] = unreleased
        # - bring over all per-line buckets from manager (flattening)
        # Here, all that's left in the per-family bucket should be lines, not
        # unreleased_*
        ret.update(manager[family])
    return ret


def get_doctree(path, **kwargs):
    """
    Obtain a Sphinx doctree from the RST file at ``path``.

    Performs no Releases-specific processing; this code would, ideally, be in
    Sphinx itself, but things there are pretty tightly coupled. So we wrote
    this.

    Any additional kwargs are passed unmodified into an internal `make_app`
    call.

    :param str path: A relative or absolute file path string.

    :returns:
        A two-tuple of the generated ``sphinx.application.Sphinx`` app and the
        doctree (a ``docutils.document`` object).

    .. versionchanged:: 1.6
        Added support for passing kwargs to `make_app`.
    """
    root, filename = os.path.split(path)
    docname, _ = os.path.splitext(filename)
    # TODO: this only works for top level changelog files (i.e. ones where
    # their dirname is the project/doc root)
    app = make_app(srcdir=root, **kwargs)
    # Create & init a BuildEnvironment. Mm, tasty side effects.
    app._init_env(freshenv=True)
    env = app.env
    # More arity/API changes: Sphinx 1.3/1.4-ish require one to pass in the app
    # obj in BuildEnvironment.update(); modern Sphinx performs that inside
    # Application._init_env() (which we just called above) and so that kwarg is
    # removed from update(). EAFP.
    kwargs = dict(
        config=app.config,
        srcdir=root,
        doctreedir=app.doctreedir,
        app=app,
    )
    try:
        env.update(**kwargs)
    except TypeError:
        # Assume newer Sphinx w/o an app= kwarg
        del kwargs['app']
        env.update(**kwargs)
    # Code taken from sphinx.environment.read_doc; easier to manually call
    # it with a working Environment object, instead of doing more random crap
    # to trick the higher up build system into thinking our single changelog
    # document was "updated".
    env.temp_data['docname'] = docname
    env.app = app
    # NOTE: SphinxStandaloneReader API changed in 1.4 :(
    reader_kwargs = {
        'app': app,
        'parsers': env.config.source_parsers,
    }
    if sphinx.version_info[:2] < (1, 4):
        del reader_kwargs['app']
    # This monkeypatches (!!!) docutils to 'inject' all registered Sphinx
    # domains' roles & so forth. Without this, rendering the doctree lacks
    # almost all Sphinx magic, including things like :ref: and :doc:!
    with sphinx_domains(env):
        try:
            reader = SphinxStandaloneReader(**reader_kwargs)
        except TypeError:
            # If we import from io, this happens automagically, not in API
            del reader_kwargs['parsers']
            reader = SphinxStandaloneReader(**reader_kwargs)
        pub = Publisher(reader=reader,
                        writer=SphinxDummyWriter(),
                        destination_class=NullOutput)
        pub.set_components(None, 'restructuredtext', None)
        pub.process_programmatic_settings(None, env.settings, None)
        # NOTE: docname derived higher up, from our given path
        src_path = env.doc2path(docname)
        source = SphinxFileInput(
            app,
            env,
            source=None,
            source_path=src_path,
            encoding=env.config.source_encoding,
        )
        pub.source = source
        pub.settings._source = src_path
        pub.set_destination(None, None)
        pub.publish()
        return app, pub.document


def load_conf(srcdir):
    """
    Load ``conf.py`` from given ``srcdir``.

    :returns: Dictionary derived from the conf module.
    """
    path = os.path.join(srcdir, 'conf.py')
    mylocals = {'__file__': path}
    with open(path) as fd:
        exec(fd.read(), mylocals)
    return mylocals


def make_app(**kwargs):
    """
    Create a dummy Sphinx app, filling in various hardcoded assumptions.

    For example, Sphinx assumes the existence of various source/dest
    directories, even if you're only calling internals that never generate (or
    sometimes, even read!) on-disk files. This function creates safe temp
    directories for these instances.

    It also neuters Sphinx's internal logging, which otherwise causes verbosity
    in one's own test output and/or debug logs.

    Finally, it does load the given srcdir's ``conf.py``, but only to read
    specific bits like ``extensions`` (if requested); most of it is ignored.

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

    :param bool load_extensions:
        Whether to load the real ``conf.py`` and setup any extensions it
        configures. Default: ``False``.

    :returns: A Sphinx ``Application`` instance.

    .. versionchanged:: 1.6
        Added the ``load_extensions`` kwarg.
    """
    srcdir = kwargs.pop('srcdir', mkdtemp())
    dstdir = kwargs.pop('dstdir', mkdtemp())
    doctreedir = kwargs.pop('doctreedir', mkdtemp())
    load_extensions = kwargs.pop('load_extensions', False)
    real_conf = None
    try:
        # Sphinx <1.6ish
        Sphinx._log = lambda self, message, wfile, nonl=False: None
        # Sphinx >=1.6ish. Technically still lets Very Bad Things through,
        # unlike the total muting above, but probably OK.
        # NOTE: used to just do 'sphinx' but that stopped working, even on
        # sphinx 1.6.x. Weird. Unsure why hierarchy not functioning.
        for name in ('sphinx', 'sphinx.sphinx.application'):
            logging.getLogger(name).setLevel(logging.ERROR)
        # App API seems to work on all versions so far.
        app = Sphinx(
            srcdir=srcdir,
            confdir=None,
            outdir=dstdir,
            doctreedir=doctreedir,
            buildername='html',
        )
        # Might as well load the conf file here too.
        if load_extensions:
            real_conf = load_conf(srcdir)
    finally:
        for d in (srcdir, dstdir, doctreedir):
            # Only remove empty dirs; non-empty dirs are implicitly something
            # that existed before we ran, and should not be touched.
            try:
                os.rmdir(d)
            except OSError:
                pass
    setup(app)
    # Mock out the config within. More assumptions by Sphinx :(
    # TODO: just use real config and overlay what truly needs changing? is that
    # feasible given the rest of the weird ordering we have to do? If it is,
    # maybe just literally slap this over the return value of load_conf()...
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
        config['releases_{}'.format(name)] = kwargs[name]
    # Stitch together as the sphinx app init() usually does w/ real conf files
    app.config._raw_config = config
    # init_values() requires a 'warn' runner on Sphinx 1.3-1.6, so if we seem
    # to be hitting arity errors, give it a dummy such callable. Hopefully
    # calling twice doesn't introduce any wacko state issues :(
    try:
        app.config.init_values()
    except TypeError: # boy I wish Python had an ArityError or w/e
        app.config.init_values(lambda x: x)
    # Initialize extensions (the internal call to this happens at init time,
    # which of course had no valid config yet here...)
    if load_extensions:
        for extension in real_conf.get('extensions', []):
            # But don't set up ourselves again, that causes errors
            if extension == 'releases':
                continue
            app.setup_extension(extension)
    return app


def changelog2dict(changelog):
    """
    Helper turning internal list-o-releases structure into a dict.

    See `parse_changelog` docstring for return value details.
    """
    return {r['obj'].number: r['entries'] for r in changelog}
