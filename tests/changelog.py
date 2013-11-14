from spec import Spec, skip, eq_
from mock import Mock

from releases import (
    issue,
    release,
    construct_releases
)


# Wrap dumb nodeutils-derived shit for easier creation
def _issue(type_, number, **kwargs):
    kwargs['type_'] = type_
    kwargs['number'] = number
    kwargs.setdefault('major', False)
    kwargs.setdefault('backported', False)
    return issue(**kwargs)

def _entry(i):
    return [[i, []]]

def _release(number, **kwargs):
    r = release(number=number, **kwargs)
    return [[r]]


class releases(Spec):
    """
    Organization of issues into releases
    """
    def setup(self):
        # Fake app obj
        app = Mock('app')
        config = Mock('config')
        config.releases_release_uri = 'foo_%s'
        config.releases_issue_uri = 'bar_%s'
        config.releases_debug = False
        app.config = config
        self.app = app
        # Changelog components
        self.f = _issue('feature', '12')
        self.s = _issue('support', '5')
        self.b = _issue('bug', '15')
        self.mb = _issue('bug', '200', major=True)

    def _process(self, *entries):
        return construct_releases(entries, self.app)[0]['entries']

    def feature_releases_include_features_and_support_not_bugs(self):
        entries = self._process(
            _release('1.0.0'),
            _entry(self.f),
            _entry(self.b),
            _entry(self.s),
        )
        eq_(len(entries), 2)
        assert self.f in entries
        assert self.s in entries
        assert self.b not in entries

    def feature_releases_include_major_bugs(self):
        entries = self._process(
            _release('1.0.0'),
            _entry(self.f),
            _entry(self.b),
            _entry(self.mb),
        )
        eq_(len(entries), 2)
        assert self.f in entries
        assert self.mb in entries
        assert self.b not in entries

    def bugfix_releases_include_bugs(self):
        skip()

    def bugfix_releases_include_backported_features(self):
        skip()

    def bugfix_releases_include_backported_support(self):
        skip()

    def unmarked_bullet_list_items_treated_as_bugs(self):
        skip()


class nodes(Spec):
    """
    Expansion/extension of docutils nodes
    """
    def issues_with_numbers_appear_as_number_links(self):
        skip()

    def bugs_marked_as_bugs(self):
        skip()

    def features_marked_as_features(self):
        skip()

    def support_marked_as_suppot(self):
        skip()

    def zeroed_issues_appear_as_unlinked_issues(self):
        skip()
