"""
Tests for the ``releases.util`` module.

These are in the integration suite because they deal with on-disk files.
"""

import os

from docutils.nodes import document
from spec import Spec, ok_, eq_
from sphinx.application import Sphinx

from releases.models import Release, Issue
from releases.util import get_doctree, parse_changelog

support = os.path.join(os.path.dirname(__file__), '_support')
vanilla = os.path.join(support, 'vanilla', 'changelog.rst')


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
    def yields_releases_dict_and_manager_from_changelog_path(self):
        releases, manager = parse_changelog(vanilla)
        ok_(releases)
        ok_(manager)
        ok_(isinstance(releases, dict))
        eq_(
            set(releases.keys()),
            set(('1.0.0', '1.0.1', 'unreleased_1.x_bugfix',
                'unreleased_1.x_feature')),
        )
        eq_(len(releases['1.0.0']), 0)
        eq_(len(releases['unreleased_1.x_bugfix']), 0)
        eq_(len(releases['unreleased_1.x_feature']), 0)
        eq_(len(releases['1.0.1']), 1)
        issue = releases['1.0.1'][0]
        eq_(issue.type, 'bug')
        eq_(issue.number, '1')
        eq_(manager.keys(), [1])
        buckets = manager[1]
        eq_(len(buckets), 3)
        eq_(buckets['1.0'], []) # emptied into 1.0.1
