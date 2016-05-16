from spec import Spec, eq_
from docutils.nodes import (
    reference, bullet_list, list_item, literal, raw, paragraph, Text
)

from releases import (
    Issue,
    construct_releases,
    construct_nodes,
)

from _util import (
    b, f, s,
    entry,
    make_app,
    release,
    releases,
    setup_issues,
)


def _obj2name(obj):
    cls = obj if isinstance(obj, type) else obj.__class__
    return cls.__name__.split('.')[-1]

def _expect_type(node, cls):
    type_ = _obj2name(node)
    name = _obj2name(cls)
    msg = "Expected %r to be a %s, but it's a %s" % (node, name, type_)
    assert isinstance(node, cls), msg


class presentation(Spec):
    """
    Expansion/extension of docutils nodes (rendering)
    """
    def setup(self):
        setup_issues(self)

    def _generate(self, *entries, **kwargs):
        raw = kwargs.pop('raw', False)
        nodes = construct_nodes(releases(*entries, **kwargs))
        # By default, yield the contents of the bullet list.
        return nodes if raw else nodes[0][1][0]

    def _test_link(self, kwargs, type_, expected):
        app = make_app(**kwargs)
        nodes = construct_nodes(construct_releases([
            release('1.0.2', app=app),
            entry(b(15, app=app)),
            release('1.0.0'),
        ], app=app))
        if type_ == 'release':
            header = nodes[0][0][0].astext()
            assert expected in header
        elif type_ == 'issue':
            link = nodes[0][1][0][0][2]
            eq_(link['refuri'], expected)
        else:
            raise Exception("Gave unknown type_ kwarg to _test_link()!")

    def issues_with_numbers_appear_as_number_links(self):
        self._test_link({}, 'issue', 'bar_15')

    def releases_appear_as_header_links(self):
        self._test_link({}, 'release', 'foo_1.0.2')

    def links_will_use_github_option_if_defined(self):
        kwargs = {
            'release_uri': None,
            'issue_uri': None,
            'github_path': 'foo/bar',
        }
        for type_, expected in (
            ('issue', 'https://github.com/foo/bar/issues/15'),
            ('release', 'https://github.com/foo/bar/tree/1.0.2'),
        ):
            self._test_link(kwargs, type_, expected)

    def issue_links_prefer_explicit_setting_over_github_setting(self):
        kwargs = {
            'release_uri': None,
            'issue_uri': 'explicit_issue_%s',
            'github_path': 'foo/bar',
        }
        self._test_link(kwargs, 'issue', 'explicit_issue_15')

    def release_links_prefer_explicit_setting_over_github_setting(self):
        kwargs = {
            'release_uri': 'explicit_release_%s',
            'issue_uri': None,
            'github_path': 'foo/bar',
        }
        self._test_link(kwargs, 'release', 'explicit_release_1.0.2')

    def _assert_prefix(self, entries, expectation):
        assert expectation in self._generate(*entries)[0][0][0]

    def bugs_marked_as_bugs(self):
        self._assert_prefix(['1.0.2', self.b], 'Bug')

    def features_marked_as_features(self):
        self._assert_prefix(['1.1.0', self.f], 'Feature')

    def support_marked_as_support(self):
        self._assert_prefix(['1.1.0', self.s], 'Support')

    def dashed_issues_appear_as_unlinked_issues(self):
        node = self._generate('1.0.2', b('-'))
        assert not isinstance(node[0][2], reference)

    def zeroed_issues_appear_as_unlinked_issues(self):
        node = self._generate('1.0.2', b(0))
        assert not isinstance(node[0][2], reference)

    def un_prefixed_list_items_appear_as_unlinked_bugs(self):
        fake = list_item('', paragraph('', '',
            Text("fixes an issue in "), literal('', 'methodname')))
        node = self._generate('1.0.2', fake)
        # [<raw prefix>, <inline colon>, <inline space>, <text>, <monospace>]
        eq_(len(node[0]), 5)
        assert 'Bug' in str(node[0][0])
        assert 'fixes an issue' in str(node[0][3])
        assert 'methodname' in str(node[0][4])

    def un_prefixed_list_items_get_no_prefix_under_unstable_prehistory(self):
        app = make_app(unstable_prehistory=True)
        fake = list_item('', paragraph('', '', raw('', 'whatever')))
        node = self._generate('0.1.0', fake, app=app, skip_initial=True)
        # [<raw bug text>]
        eq_(len(node[0]), 1)
        assert 'Bug' not in str(node[0][0])
        assert 'whatever' in str(node[0][0])

    def issues_remain_wrapped_in_unordered_list_nodes(self):
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
        issue = list_item('',
            paragraph('', '', self.b.deepcopy(), raw('', 'x')),
        )
        # Trailing nodes should appear post-processing after the link/etc
        rest = self._generate('1.0.2', issue)[0]
        eq_(len(rest), 5)
        _expect_type(rest[4], raw)
        eq_(rest[4].astext(), 'x')

    def complex_descriptions_are_preserved(self):
        # Complex 'entry' mapping to an outer list_item (list) containing two
        # paragraphs, one w/ the real issue + desc, another simply a 2nd text
        # paragraph. Using 'raw' nodes for filler as needed.
        issue = list_item('',
            paragraph('', '', self.b.deepcopy(), raw('', 'x')),
            paragraph('', '', raw('', 'y')),
        )
        li = self._generate('1.0.2', issue)
        # Expect that the machinery parsing issue nodes/nodelists, is not
        # discarding our 2nd 'paragraph'
        eq_(len(li), 2)
        p1, p2 = li
        # Last item in 1st para is our 1st raw node
        _expect_type(p1[4], raw)
        eq_(p1[4].astext(), 'x')
        # Only item in 2nd para is our 2nd raw node
        _expect_type(p2[0], raw)
        eq_(p2[0].astext(), 'y')

    def descriptions_are_parsed_for_issue_roles(self):
        item = list_item('',
            paragraph('', '', self.b.deepcopy(), s(5))
        )
        para = self._generate('1.0.2', item)[0]
        # Sanity check - in a broken parsing scenarion, the 4th child will be a
        # raw issue object
        assert not isinstance(para[4], Issue)
        # First/primary link
        _expect_type(para[2], reference)
        eq_(para[2].astext(), '#15')
        assert 'Bug' in para[0].astext()
        # Second/inline link
        _expect_type(para[6], reference)
        eq_(para[6].astext(), '#5')
        assert 'Support' in para[4].astext()

    def unreleased_buckets_omit_major_version_when_only_one_exists(self):
        result = self._generate(b(1), raw=True)[0][0][0]
        html = str(result) # since repr() from test-fail hides actual text
        assert "Next bugfix release" in html

    def unreleased_buckets_display_major_version_when_multiple(self):
        entries = (
            b(3), # should appear in unreleased bugs for 2.x
            '2.0.0',
            b(2), # should appear in unreleased bugs for 1.x
            '1.0.1',
            b(1),
        )
        # Expectation: [2.x unreleased, 1.x unreleased, 1.0.1]
        two_x, one_x, _ = self._generate(*entries, raw=True)
        html = str(two_x[0][0])
        assert "Next 2.x bugfix release" in html
        html = str(one_x[0][0])
        assert "Next 1.x bugfix release" in html

    def unreleased_displays_version_when_only_some_lines_displayed(self):
        # I.e. if there's unreleased 1.x stuff but no unreleased 2.x, still
        # display the "1.x".
        entries = (
            # Note lack of any bugfixes post 2.0.0
            '2.0.0',
            b(2),
            '1.0.1',
            b(1),
        )
        # Expectation: [1.x unreleased, 1.0.1] - no 2.x.
        result = self._generate(*entries, raw=True)
        eq_(len(result), 2)
        html = str(result[0][0][0])
        assert "Next 1.x bugfix release" in html

    def unstable_prehistory_active_means_only_one_unreleased_release(self):
        app = make_app(unstable_prehistory=True)
        entries = (b(2), f(3), '0.1.0', b(1))
        result = self._generate(*entries, app=app, raw=True, skip_initial=True)
        html = str(result[0][0][0])
        assert "Next release" in html
