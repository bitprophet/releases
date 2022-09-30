from pathlib import Path
from unittest.mock import patch, MagicMock as Mock

from pytest import skip  # noqa
from sphinx.application import Sphinx
from docutils.nodes import bullet_list

from releases.util import (
    make_app,
    parse_changelog,
    get_doctree,
    _faux_write_doctree,
)


class parse_changelog_:
    @patch("releases.util.changelog2dict")
    @patch("releases.util.get_doctree")
    @patch("releases.util.construct_releases")
    def _test(
        self, extra_setup, construct_releases, get_doctree, changelog2dict
    ):
        # Setup
        app, doctree = Mock(name="app"), Mock(name="doctree")
        blist = Mock(spec=bullet_list())
        doctree.__getitem__.return_value = [blist]
        releases = Mock(name="releases")
        get_doctree.return_value = app, doctree
        manager = []  # empty iterable
        if extra_setup:
            manager = extra_setup(changelog2dict)
        construct_releases.return_value = releases, manager
        # Do eet (NOTE: also tests that kwargs are passed thru)
        result = parse_changelog("random/changelog.rst", kwarg="value")
        # Calls
        get_doctree.assert_called_once_with(
            "random/changelog.rst", kwarg="value"
        )
        construct_releases.assert_called_once_with(blist.children, app)
        changelog2dict.assert_called_once_with(releases)
        return result, changelog2dict

    def calls_various_methods_and_returns_dict(self):
        result, cl2d = self._test(None)
        assert result is cl2d.return_value

    def omits_unreleased_objects(self):
        # NOTE: this is all a bit slapdash and doesn't 100% represent real
        # return data, just enough to ensure the relevant logic is working
        def extra_setup(cl2d):
            cl2d.return_value = {
                "unreleased_1.2_bugfixes": None,
                "unreleased_1.2_features": None,
                "1.2.3": "stuff!",
            }
            manager = {
                "1": {
                    "unreleased_bugfix": None,
                    "unreleased_feature": "shiny!",
                    "1.2": "hmm",
                },
                "2": {"unreleased_feature": "shinier!", "2.2": "also hmm"},
            }
            return manager

        result, _ = self._test(extra_setup)
        assert result == {
            "1.2": "hmm",
            "1.2.3": "stuff!",
            "2.2": "also hmm",
            "unreleased_1_feature": "shiny!",
            "unreleased_2_feature": "shinier!",
        }


class get_doctree_:
    def setup(self):
        self.cwd = Path.cwd()

    @patch("releases.util.make_app")
    def returns_app_and_doctree_for_file_path(self, make_app):
        # NOTE: using relative path and testing that an absolute one is used,
        # as this prevents internal docutils pseudo-bugs
        path = "nonsense/path.rst"
        app = make_app.return_value
        # Expect awful monkeypatch workaround re: assignment/extraction of read
        # doctree
        assert get_doctree(path) == (app, app.builder._read_doctree)
        make_app.assert_called_once_with(srcdir=self.cwd / "nonsense")
        # Ensure our monkeypatch is active
        # NOTE: this doesn't test inside the monkeypatch; integration/util.py
        # should though
        assert app.builder.__class__.write_doctree is _faux_write_doctree
        # NOTE: still enforcing the STRING form of path is handed to read_doc,
        # as it is not yet Pathlib-aware (apparently)
        # NOTE: use of .stem, a change from sphinx 1.x
        app.builder.read_doc.assert_called_once_with(
            str(self.cwd / "nonsense" / "path")
        )

    @patch("releases.util.make_app")
    def passes_kwargs_to_make_app(self, make_app):
        path = "nonsense/path.rst"
        get_doctree(path, whatever="kwargs")
        make_app.assert_called_once_with(
            srcdir=self.cwd / "nonsense", whatever="kwargs"
        )


class make_app_:
    @patch("releases.util.os.rmdir")
    @patch("releases.util.mkdtemp")
    @patch("releases.util.setup")
    def creates_Sphinx_object_with_temp_dirs(
        self, setup, mkdtemp, rmdir, tmpdir
    ):
        tempdirs = [tmpdir.mkdir(x) for x in ["src", "out", "doc"]]
        mkdtemp.side_effect = tempdirs
        app = make_app()
        assert isinstance(app, Sphinx)
        assert app.srcdir == app.confdir == tempdirs[0]
        assert app.outdir == tempdirs[1]
        assert app.doctreedir == tempdirs[2]
        assert app.builder.name == "html"
        for path in tempdirs:
            rmdir.assert_any_call(path)
        setup.assert_called_once_with(app)
        # TODO: the config bits too, tho those are really just implementation
        # details for now?

    def unused_kwargs_become_releases_config_options(self):
        app = make_app(debug=True, document_name="notchangelog")
        assert app.config.releases_debug is True
        assert app.config.releases_document_name == "notchangelog"

    @patch("releases.util.os.rmdir")
    @patch("releases.util.mkdtemp")
    def dirs_can_be_overridden(self, mkdtemp, rmdir, tmpdir):
        tempdirs = [tmpdir.mkdir(x) for x in ["src", "out", "doc"]]
        app = make_app(
            srcdir=tempdirs[0], dstdir=tempdirs[1], doctreedir=tempdirs[2]
        )
        assert not mkdtemp.called
        assert app.srcdir == app.confdir == tempdirs[0]
        assert app.outdir == tempdirs[1]
        assert app.doctreedir == tempdirs[2]
        # Explicitly given dirs are still rmdir'd (but are never rm -rf'd)
        for path in tempdirs:
            rmdir.assert_any_call(path)
