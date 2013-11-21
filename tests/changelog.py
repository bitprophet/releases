from spec import Spec, skip, eq_
from mock import Mock

from releases import (
    issue,
    issues_role,
    release,
    release_role,
    construct_releases,
    construct_nodes
)
from docutils.nodes import reference, bullet_list, list_item, raw


def _app():
    # Fake app obj
    app = Mock('app')
    config = Mock('config')
    config.releases_release_uri = 'foo_%s'
    config.releases_issue_uri = 'bar_%s'
    config.releases_debug = False
    app.config = config
    return app

def _inliner():
    return Mock(document=Mock(settings=Mock(env=Mock(app=_app()))))

# Obtain issue() object w/o wrapping all parse steps
def _issue(type_, number, **kwargs):
    text = str(number)
    if kwargs.get('backported', False):
        text += " backported"
    if kwargs.get('major', False):
        text += " major"
    return issues_role(
        name=type_,
        rawtext='',
        text=text,
        lineno=None,
        inliner=_inliner(),
    )[0][0]

def _entry(i):
    return [[i]]

def _release(number, **kwargs):
    return release_role(
        name=None,
        rawtext='',
        text='%s <2013-11-20>' % number,
        lineno=None,
        inliner=_inliner(),
    )

def _releases(*entries):
    entries = list(entries) # lol tuples
    # Translate simple objs into changelog-friendly ones
    for index, item in enumerate(entries):
        if isinstance(item, basestring):
            entries[index] = _release(item)
        else:
            entries[index] = _entry(item)
    # Insert initial/empty 1st release to start timeline
    entries.append(_release('1.0.0'))
    return construct_releases(entries, _app())

def _setup_issues(self):
    self.f = _issue('feature', '12')
    self.s = _issue('support', '5')
    self.b = _issue('bug', '15')
    self.mb = _issue('bug', '200', major=True)
    self.bf = _issue('feature', '27', backported=True)
    self.bs = _issue('support', '29', backported=True)


class releases(Spec):
    """
    Organization of issues into releases
    """
    def setup(self):
        _setup_issues(self)

    def _expect_entries(self, all_entries, in_, not_in):
        # Grab 2nd release as 1st is the empty 'beginning of time' one
        entries = _releases(*all_entries)[1]['entries']
        eq_(len(entries), len(in_))
        for x in in_:
            assert x in entries
        for x in not_in:
            assert x not in entries

    def feature_releases_include_features_and_support_not_bugs(self):
        self._expect_entries(
            ['1.1.0', self.f, self.b, self.s],
            [self.f, self.s],
            [self.b]
        )

    def feature_releases_include_major_bugs(self):
        self._expect_entries(
            ['1.1.0', self.f, self.b, self.mb],
            [self.f, self.mb],
            [self.b]
        )

    def bugfix_releases_include_bugs(self):
        self._expect_entries(
            ['1.0.2', self.f, self.b, self.mb],
            [self.b],
            [self.mb, self.f],
        )

    def bugfix_releases_include_backported_features(self):
        self._expect_entries(
            ['1.0.2', self.bf, self.b, self.s],
            [self.b, self.bf],
            [self.s]
        )

    def bugfix_releases_include_backported_support(self):
        self._expect_entries(
            ['1.0.2', self.f, self.b, self.s, self.bs],
            [self.b, self.bs],
            [self.s, self.f]
        )

    def unmarked_bullet_list_items_treated_as_bugs(self):
        # Empty list item here stands in for just-a-list-of-nodes,
        # which is what a non-issue/release changelog list item looks like
        entries = _releases('1.0.2', self.f, [])[1]['entries']
        eq_(len(entries), 1)
        assert self.f not in entries
        assert isinstance(entries[0], issue)
        eq_(entries[0].number, None)

    def unreleased_items_go_in_unreleased_release(self):
        releases = _releases('1.0.2', self.f, self.b)
        r = releases[-1]
        eq_(len(r['entries']), 1)
        assert self.f in r['entries']
        eq_(r['obj'].number, 'unreleased')

    def issues_consumed_by_releases_are_not_in_unreleased(self):
        releases = _releases('1.0.2', self.f, self.b, self.s, self.bs)
        release = releases[1]['entries']
        unreleased = releases[-1]['entries']
        assert self.b in release
        assert self.b not in unreleased

    def unreleased_catches_bugs_and_features(self):
        entries = [self.f, self.b, self.mb, self.s, self.bs, self.bf]
        releases = _releases(*entries)
        unreleased = releases[-1]['entries']
        for x in entries:
            assert x in unreleased


def _obj2name(obj):
    cls = obj if isinstance(obj, type) else obj.__class__
    return cls.__name__.split('.')[-1]

def _expect_type(node, cls):
    type_ = _obj2name(node)
    name = _obj2name(cls)
    msg = "Expected %r to be a %s, but it's a %s" % (node, name, type_)
    assert isinstance(node, cls), msg


class nodes(Spec):
    """
    Expansion/extension of docutils nodes
    """
    def setup(self):
        _setup_issues(self)

    def _generate(self, *entries, **kwargs):
        nodes = construct_nodes(_releases(*entries))
        # By default, yield the contents of the bullet list.
        return nodes if kwargs.get('raw', False) else nodes[0][1][0]

    def issues_with_numbers_appear_as_number_links(self):
        nodes = self._generate('1.0.2', self.b)
        link = nodes[0][2]
        _expect_type(link, reference)
        assert link['refuri'] == 'bar_15'

    def _assert_prefix(self, entries, expectation):
        assert expectation in self._generate(*entries)[0][0][0]

    def bugs_marked_as_bugs(self):
        self._assert_prefix(['1.0.2', self.b], 'Bug')

    def features_marked_as_features(self):
        self._assert_prefix(['1.1.0', self.f], 'Feature')

    def support_marked_as_suppot(self):
        self._assert_prefix(['1.1.0', self.s], 'Support')

    def zeroed_issues_appear_as_unlinked_issues(self):
        self._assert_prefix(['1.0.2', _issue('bug', '0')], 'Bug')

    def issues_wrapped_in_unordered_list_nodes(self):
        node = self._generate('1.0.2', self.b, raw=True)[0][1]
        _expect_type(node, bullet_list)
        _expect_type(node[0], list_item)

    def release_headers_have_local_style_tweaks(self):
        title = self._generate('1.0.2', self.b, raw=True)[0][0]
        _expect_type(title, raw)
        assert 'style="margin-bottom: 0.3em"' in title
