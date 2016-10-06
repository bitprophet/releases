"""
Tests for the ``releases.util`` module.

These are in the integration suite because they deal with on-disk files.
"""

import os

from docutils.nodes import document
from spec import Spec, ok_, eq_

from releases.models import Release, Issue
from releases.util import get_doctree

support = os.path.join(os.path.dirname(__file__), '_support')


class get_doctree_(Spec):
    def turns_changelog_file_into_data_structures(self):
        vanilla = os.path.join(support, 'vanilla', 'changelog.rst')
        doctree = get_doctree(vanilla)
        # Expect doctree
        ok_(doctree)
        ok_(isinstance(doctree, document))
        # Sanity checks of internal nodes, which should be Releases objects
        entries = doctree[0][2]
        ok_(isinstance(entries[0][0][0], Release))
        bug = entries[1][0][0]
        ok_(isinstance(bug, Issue))
        eq_(bug.type, 'bug')
        eq_(bug.number, '1')
