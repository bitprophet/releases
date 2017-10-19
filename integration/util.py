"""
Tests for the ``releases.util`` module.

These are in the integration suite because they deal with on-disk files.
"""

import logging
import os

from docutils.nodes import document
from spec import Spec, ok_, eq_
from sphinx.application import Sphinx

from releases.models import Release, Issue
from releases.util import get_doctree, parse_changelog


# Mute Sphinx's own logging, as it makes test output quite verbose
logging.getLogger('sphinx').setLevel(logging.ERROR)

support = os.path.join(os.path.dirname(__file__), '_support')
vanilla = os.path.join(support, 'vanilla', 'changelog.rst')
unreleased_bugs = os.path.join(support, 'unreleased_bugs', 'changelog.rst')

class get_doctree_(Spec):
    def obtains_app_and_doctree_from_filepath(self):
        app, doctree = get_doctree(vanilla)
        # Expect doctree & app
        ok_(doctree)
        ok_(app)
        ok_(isinstance(doctree, document))
        ok_(isinstance(app, Sphinx))
        # Sanity checks of internal nodes, which should be Releases objects
        entries = doctree[0][2]
        ok_(isinstance(entries[0][0][0], Release))
        bug = entries[1][0][0]
        ok_(isinstance(bug, Issue))
        eq_(bug.type, 'bug')
        eq_(bug.number, '1')


class parse_changelog_(Spec):
    def yields_releases_dict_from_changelog_path(self):
        changelog = parse_changelog(vanilla)
        ok_(changelog)
        ok_(isinstance(changelog, dict))
        eq_(
            set(changelog.keys()),
            set(('1.0.0', '1.0.1', '1.0', 'unreleased_1_feature')),
        )
        eq_(len(changelog['1.0.0']), 0)
        eq_(len(changelog['unreleased_1_feature']), 0)
        eq_(len(changelog['1.0.1']), 1)
        issue = changelog['1.0.1'][0]
        eq_(issue.type, 'bug')
        eq_(issue.number, '1')
        eq_(changelog['1.0'], []) # emptied into 1.0.1

    def unreleased_bugfixes_accounted_for(self):
        changelog = parse_changelog(unreleased_bugs)
        # Basic assertions
        v101 = changelog['1.0.1']
        eq_(len(v101), 1)
        eq_(v101[0].number, '1')
        v110 = changelog['1.1.0']
        eq_(len(v110), 1)
        eq_(v110[0].number, '2')
        v102 = changelog['1.0.2']
        eq_(len(v102), 1)
        eq_(v102[0].number, '3')
        # The crux of the matter: 1.0 bucket empty, 1.1 bucket still has bug 3
        line_10 = changelog['1.0']
        eq_(len(line_10), 0)
        line_11 = changelog['1.1']
        eq_(len(line_11), 1)
        eq_(line_11[0].number, '3')
        ok_(line_11[0] is v102[0])
