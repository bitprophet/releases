import six
from spec import Spec, skip, eq_, raises
from mock import Mock

from releases import (
    issue,
    issues_role,
    release,
    release_role,
    construct_releases,
    construct_nodes
)
from docutils.nodes import (
    reference, bullet_list, list_item, title, raw
)


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
    if kwargs.get('line', None):
        text += " (%s+)" % kwargs['line']
    return issues_role(
        name=type_,
        rawtext='',
        text=text,
        lineno=None,
        inliner=_inliner(),
    )[0][0]

def _entry(i):
    """
    Maps simplerish values to a fake list_item + contents, as would be found
    in a real docutils/sphinx changelog document.

    When given a non-iterable, creates [[i]]; outer list is the list_item,
    inner list is the (1st, usually only) paragraph, and 'i' is the actual
    object/node in question.

    When given an iterable, simply returns it as-is (this is as _entry is
    frequently called within another helper.)
    """
    return i if hasattr(i, '__iter__') else [[i]]

def _release(number, **kwargs):
    return release_role(
        name=None,
        rawtext='',
        text='%s <2013-11-20>' % number,
        lineno=None,
        inliner=_inliner(),
    )

def _release_list(*entries):
    entries = list(entries) # lol tuples
    # Translate simple objs into changelog-friendly ones
    for index, item in enumerate(entries):
        if isinstance(item, six.string_types):
            entries[index] = _release(item)
        else:
            entries[index] = _entry(item)
    # Insert initial/empty 1st release to start timeline
    entries.append(_release('1.0.0'))
    return entries

def _changelog2dict(changelog):
    d = {}
    for r in changelog:
        d[r['obj'].number] = r['entries']
    return d

def _releases(*entries):
    return construct_releases(_release_list(*entries), _app())

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
        # Empty nested list stands in for just-a-list-of-nodes,
        # which is what a non-issue/release changelog list item looks like.
        # E.g. list_item(paragraph(more_nodes))
        entries = _releases('1.0.2', self.f, [[[]]])[1]['entries']
        eq_(len(entries), 1)
        assert self.f not in entries
        assert isinstance(entries[0], issue)
        eq_(entries[0].number, None)

    def unreleased_items_go_in_unreleased_releases(self):
        releases = _releases(self.f, self.b)
        # Should have two unreleased lists, one feature w/ feature, one bugfix
        # w/ bugfix.
        bugfix, feature = releases[1:]
        eq_(len(feature['entries']), 1)
        eq_(len(bugfix['entries']), 1)
        assert self.f in feature['entries']
        assert self.b in bugfix['entries']
        eq_(feature['obj'].number, 'unreleased_feature')
        eq_(bugfix['obj'].number, 'unreleased_bugfix')

    def issues_consumed_by_releases_are_not_in_unreleased(self):
        releases = _releases('1.0.2', self.f, self.b, self.s, self.bs)
        release = releases[1]['entries']
        unreleased = releases[-1]['entries']
        assert self.b in release
        assert self.b not in unreleased

    def oddly_ordered_bugfix_releases_and_unreleased_list(self):
        # Release set up w/ non-contiguous feature+bugfix releases; catches
        # funky problems with 'unreleased' buckets
        b2 = _issue('bug', '2')
        f3 = _issue('feature', '3')
        changelog = _releases(
            '1.1.1', '1.0.2', self.f, b2, '1.1.0', f3, self.b
        )
        assert f3 in changelog[1]['entries']
        assert b2 in changelog[2]['entries']
        assert b2 in changelog[3]['entries']

    def release_line_bugfix_specifier(self):
        b50 = _issue('bug', '50')
        b42 = _issue('bug', '42', line='1.1')
        f25 = _issue('feature', '25')
        b35 = _issue('bug', '35')
        b34 = _issue('bug', '34')
        f22 = _issue('feature', '22')
        b20 = _issue('bug', '20')
        c = _changelog2dict(_releases(
            '1.2.1', '1.1.2', '1.0.3',
            b50, b42,
            '1.2.0', '1.1.1', '1.0.2',
            f25, b35, b34,
            '1.1.0', '1.0.1',
            f22, b20
        ))
        for rel, issues in (
            ('1.0.1', [b20]),
            ('1.1.0', [f22]),
            ('1.0.2', [b34, b35]),
            ('1.1.1', [b34, b35]),
            ('1.2.0', [f25]),
            ('1.0.3', [b50]), # the crux - is not b50 + b42
            ('1.1.2', [b50, b42]),
            ('1.2.1', [b50, b42]),
        ):
            eq_(set(c[rel]), set(issues))


    def releases_can_specify_issues_explicitly(self):
        # Build regular list-o-entries
        b2 = _issue('bug', '2')
        b3 = _issue('bug', '3')
        changelog = _release_list(
            '1.0.1', '1.1.1', b3, b2, self.b, '1.1.0', self.f
        )
        # Modify 1.0.1 release to be speshul
        changelog[0][0].append("2, 3")
        rendered = construct_releases(changelog, _app())
        # 1.0.1 includes just 2 and 3, not bug 1
        one_0_1 = rendered[3]['entries']
        one_1_1 = rendered[2]['entries']
        assert self.b not in one_0_1
        assert b2 in one_0_1
        assert b3 in one_0_1
        # 1.1.1 includes all 3 (i.e. the explicitness of 1.0.1 didn't affect
        # the 1.1 line bucket.)
        assert self.b in one_1_1
        assert b2 in one_1_1
        assert b3 in one_1_1

    def explicit_release_list_split_works_with_unicode(self):
        b = _issue('bug', '17')
        changelog = _release_list('1.0.1', b)
        changelog[0][0].append(six.text_type('17'))
        # When using naive method calls, this explodes
        construct_releases(changelog, _app())

    def explicit_feature_release_features_are_removed_from_unreleased(self):
        f1 = _issue('feature', '1')
        f2 = _issue('feature', '2')
        changelog = _release_list('1.1.0', f1, f2)
        # Ensure that 1.1.0 specifies feature 2
        changelog[0][0].append("2")
        rendered = _changelog2dict(construct_releases(changelog, _app()))
        # 1.1.0 should have feature 2 only
        assert f2 in rendered['1.1.0']
        assert f1 not in rendered['1.1.0']
        # unreleased feature list should still get/see feature 1
        assert f1 in rendered['unreleased_feature']
        # now-released feature 2 should not be in unreleased_feature
        assert f2 not in rendered['unreleased_feature']

    def explicit_bugfix_releases_get_removed_from_unreleased(self):
        b1 = _issue('bug', '1')
        b2 = _issue('bug', '2')
        changelog = _release_list('1.0.1', b1, b2)
        # Ensure that 1.0.1 specifies bug 2
        changelog[0][0].append("2")
        rendered = construct_releases(changelog, _app())
        # 1.0.1 should have bug 2 only
        assert b2 in rendered[1]['entries']
        assert b1 not in rendered[1]['entries']
        # unreleased bug list should still get/see bug 1
        assert b1 in rendered[2]['entries']

    @raises(ValueError)
    def explicit_releases_error_on_unfound_issues(self):
        # Just a release - result will have 1.0.0, 1.0.1, and unreleased
        changelog = _release_list('1.0.1')
        # No issues listed -> this clearly doesn't exist in any buckets
        changelog[1][0].append("25")
        # This should asplode
        construct_releases(changelog, _app())

    @raises(ValueError)
    def duplicate_issue_numbers_raises_error(self):
        _releases('1.0.1', self.b, self.b)

    def duplicate_zeroes_dont_error(self):
        cl = _releases('1.0.1', _issue('bug', '0'), _issue('bug', '0'))
        cl = _changelog2dict(cl)
        assert len(cl['1.0.1']) == 2


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

    def dashed_issues_appear_as_unlinked_issues(self):
        node = self._generate('1.0.2', _issue('bug', '-'))
        assert not isinstance(node[0][2], reference)

    def zeroed_issues_appear_as_unlinked_issues(self):
        node = self._generate('1.0.2', _issue('bug', '0'))
        assert not isinstance(node[0][2], reference)

    def issues_wrapped_in_unordered_list_nodes(self):
        node = self._generate('1.0.2', self.b, raw=True)[0][1]
        _expect_type(node, bullet_list)
        _expect_type(node[0], list_item)

    def release_headers_have_local_style_tweaks(self):
        node = self._generate('1.0.2', self.b, raw=True)[0][0]
        _expect_type(node, raw)
        # Header w/ bottom margin
        assert '<h2 style="margin-bottom' in str(node)
        # Date span w/ font-size
        assert '<span style="font-size' in str(node)

    def descriptions_are_preserved(self):
        # Changelog containing an issue item w/ trailing node
        issue = [[self.b, raw('', 'x')]]
        node = self._generate('1.0.2', issue, raw=True)[0][1]
        # Trailing nodes should appear post-processing after the link/etc
        rest = node[0][0]
        eq_(len(rest), 5)
        _expect_type(rest[4], raw)
        eq_(rest[4].astext(), 'x')

    def sub_bullet_lists_are_preserved(self):
        pass
