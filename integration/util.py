"""
Tests for the ``releases.util`` module.

These are in the integration suite because they deal with on-disk files.
"""

import os

from spec import Spec

from releases.util import get_doctree

support = os.path.join(os.path.dirname(__file__), '_support')


class get_doctree_(Spec):
    def turns_changelog_file_into_data_structures(self):
        vanilla = os.path.join(support, 'vanilla', 'changelog.rst')
        doctree = get_doctree(vanilla)
        assert doctree
