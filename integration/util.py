"""
Tests for the ``releases.util`` module.

These are in the integration suite because they deal with on-disk files.
"""

import os

from docutils.nodes import document
from sphinx.application import Sphinx

from releases.models import Release, Issue
from releases.util import get_doctree, parse_changelog


support = os.path.join(os.path.dirname(__file__), "_support")
vanilla = os.path.join(support, "vanilla", "changelog.rst")
unreleased_bugs = os.path.join(support, "unreleased_bugs", "changelog.rst")


class get_doctree_:
    def obtains_app_and_doctree_from_filepath(self):
        app, doctree = get_doctree(vanilla)
        # Expect doctree & app
        assert doctree
        assert app
        assert isinstance(doctree, document)
        assert isinstance(app, Sphinx)
        # Sanity checks of internal nodes, which should be Releases objects
        entries = doctree[0][2]
        for x in (entries, entries[0], entries[0][0]):
            print("{!r} ({})".format(x, type(x)))
        obj = entries[0][0][0]
        assert isinstance(obj, Release), "{!r} was not a Release!".format(obj)
        bug = entries[1][0][0]
        assert isinstance(bug, Issue)
        assert bug.type == "bug"
        assert bug.number == "1"


class parse_changelog_:
    def yields_releases_dict_from_changelog_path(self):
        changelog = parse_changelog(vanilla)
        assert changelog
        assert isinstance(changelog, dict)
        assert set(changelog.keys()) == {
            "1.0.0",
            "1.0.1",
            "1.0",
            "unreleased_1_feature",
        }
        assert len(changelog["1.0.0"]) == 0
        assert len(changelog["unreleased_1_feature"]) == 0
        assert len(changelog["1.0.1"]) == 1
        issue = changelog["1.0.1"][0]
        assert issue.type == "bug"
        assert issue.number == "1"
        assert changelog["1.0"] == []  # emptied into 1.0.1

    def unreleased_bugfixes_accounted_for(self):
        changelog = parse_changelog(unreleased_bugs)
        # Basic assertions
        v101 = changelog["1.0.1"]
        assert len(v101) == 1
        assert v101[0].number == "1"
        v110 = changelog["1.1.0"]
        assert len(v110) == 1
        assert v110[0].number == "2"
        v102 = changelog["1.0.2"]
        assert len(v102) == 1
        assert v102[0].number == "3"
        # The crux of the matter: 1.0 bucket empty, 1.1 bucket still has bug 3
        line_10 = changelog["1.0"]
        assert len(line_10) == 0
        line_11 = changelog["1.1"]
        assert len(line_11) == 1
        assert line_11[0].number == "3"
        assert line_11[0] is v102[0]
