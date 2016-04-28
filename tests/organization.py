import six
from spec import Spec, eq_, raises, skip
from docutils.nodes import (
    list_item, raw, paragraph, Text,
)

from releases import (
    Issue,
    construct_releases,
)

from _util import (
    b, f, s,
    changelog2dict,
    expect_releases,
    make_app,
    release_list,
    releases,
    setup_issues,
)


class organization(Spec):
    """
    Organization of issues into releases (parsing)
    """
    def setup(self):
        setup_issues(self)

    def _expect_entries(self, all_entries, in_, not_in):
        # Grab 2nd release as 1st is the empty 'beginning of time' one
        entries = releases(*all_entries)[1]['entries']
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
        fake = list_item('', paragraph('', '', raw('', 'whatever')))
        changelog = releases('1.0.2', self.f, fake)
        entries = changelog[1]['entries']
        eq_(len(entries), 1)
        assert self.f not in entries
        assert isinstance(entries[0], Issue)
        eq_(entries[0].number, None)

    def unreleased_items_go_in_unreleased_releases(self):
        changelog = releases(self.f, self.b)
        # Should have two unreleased lists, one feature w/ feature, one bugfix
        # w/ bugfix.
        bugfix, feature = changelog[1:]
        eq_(len(feature['entries']), 1)
        eq_(len(bugfix['entries']), 1)
        assert self.f in feature['entries']
        assert self.b in bugfix['entries']
        eq_(feature['obj'].number, 'unreleased_1.x_feature')
        eq_(bugfix['obj'].number, 'unreleased_1.x_bugfix')

    def issues_consumed_by_releases_are_not_in_unreleased(self):
        changelog = releases('1.0.2', self.f, self.b, self.s, self.bs)
        release = changelog[1]['entries']
        unreleased = changelog[-1]['entries']
        assert self.b in release
        assert self.b not in unreleased

    def oddly_ordered_bugfix_releases_and_unreleased_list(self):
        # Release set up w/ non-contiguous feature+bugfix releases; catches
        # funky problems with 'unreleased' buckets
        b2 = b(2)
        f3 = f(3)
        changelog = releases(
            '1.1.1', '1.0.2', self.f, b2, '1.1.0', f3, self.b
        )
        assert f3 in changelog[1]['entries']
        assert b2 in changelog[2]['entries']
        assert b2 in changelog[3]['entries']

    def release_line_bugfix_specifier(self):
        b50 = b(50)
        b42 = b(42, line='1.1')
        f25 = f(25)
        b35 = b(35)
        b34 = b(34)
        f22 = f(22)
        b20 = b(20)
        c = changelog2dict(releases(
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
        b2 = b(2)
        b3 = b(3)
        changelog = release_list(
            '1.0.1', '1.1.1', b3, b2, self.b, '1.1.0', self.f
        )
        # Modify 1.0.1 release to be speshul
        changelog[0][0].append(Text("2, 3"))
        rendered = construct_releases(changelog, make_app())
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
        changelog = release_list('1.0.1', b(17))
        changelog[0][0].append(Text(six.text_type('17')))
        # When using naive method calls, this explodes
        construct_releases(changelog, make_app())

    def explicit_feature_release_features_are_removed_from_unreleased(self):
        f1 = f(1)
        f2 = f(2)
        changelog = release_list('1.1.0', f1, f2)
        # Ensure that 1.1.0 specifies feature 2
        changelog[0][0].append(Text("2"))
        rendered = changelog2dict(construct_releases(changelog, make_app()))
        # 1.1.0 should have feature 2 only
        assert f2 in rendered['1.1.0']
        assert f1 not in rendered['1.1.0']
        # unreleased feature list should still get/see feature 1
        assert f1 in rendered['unreleased_1.x_feature']
        # now-released feature 2 should not be in unreleased_feature
        assert f2 not in rendered['unreleased_1.x_feature']

    def explicit_bugfix_releases_get_removed_from_unreleased(self):
        b1 = b(1)
        b2 = b(2)
        changelog = release_list('1.0.1', b1, b2)
        # Ensure that 1.0.1 specifies bug 2
        changelog[0][0].append(Text('2'))
        rendered = construct_releases(changelog, make_app())
        # 1.0.1 should have bug 2 only
        assert b2 in rendered[1]['entries']
        assert b1 not in rendered[1]['entries']
        # unreleased bug list should still get/see bug 1
        assert b1 in rendered[2]['entries']

    @raises(ValueError)
    def explicit_releases_error_on_unfound_issues(self):
        # Just a release - result will have 1.0.0, 1.0.1, and unreleased
        changelog = release_list('1.0.1')
        # No issues listed -> this clearly doesn't exist in any buckets
        changelog[1][0].append(Text("25"))
        # This should asplode
        construct_releases(changelog, make_app())

    def duplicate_issue_numbers_adds_two_issue_items(self):
        test_changelog = releases('1.0.1', self.b, self.b)
        test_changelog = changelog2dict(test_changelog)
        eq_(len(test_changelog['1.0.1']), 2)

    def duplicate_zeroes_dont_error(self):
        cl = releases('1.0.1', b(0), b(0))
        cl = changelog2dict(cl)
        assert len(cl['1.0.1']) == 2

    def issues_are_sorted_by_type_within_releases(self):
        b1 = b(123, major=True)
        b2 = b(124, major=True)
        s1 = s(25)
        s2 = s(26)
        f1 = f(3455)
        f2 = f(3456)

        # Semi random definitely-not-in-desired-order order
        changelog = changelog2dict(releases('1.1', b1, s1, s2, f1, b2, f2))

        # Order should be feature, bug, support. While it doesn't REALLY
        # matter, assert that within each category the order matches the old
        # 'reverse chronological' order.
        eq_(changelog['1.1'], [f2, f1, b2, b1, s2, s1])

    def rolling_release_works_without_annotation(self):
        b1 = b(1)
        b2 = b(2)
        f3 = f(3)
        f4 = f(4)
        f5 = f(5)
        b6 = b(6)
        f7 = f(7)
        entries = (
            '2.1.0', '2.0.1', f7, b6, '2.0.0', f5, f4, '1.1.0', '1.0.1', f3,
            b2, b1
        )
        expected = {
            '1.0.1': [b1, b2],
            '1.1.0': [f3],
            '2.0.0': [f4, f5],
            '2.0.1': [b6],
            '2.1.0': [f7],
        }
        expect_releases(entries, expected)

    def plus_annotations_let_old_lines_continue_getting_released(self):
        b9 = b(9)
        f8 = f(8)
        f7 = f(7, line='1.0')
        b6 = b(6, line='1.0')
        f5 = f(5)
        f4 = f(4)
        f3 = f(3)
        b2 = b(2)
        b1 = b(1)
        entries = (
            '2.1.0', '2.0.1', '1.2.0', '1.1.1', '1.0.2', b9, f8, f7, b6,
            '2.0.0', f5, f4, '1.1.0', '1.0.1', f3, b2, b1,
        )
        expected = {
            '2.1.0': [f7, f8],
            '2.0.1': [b6, b9],
            '1.2.0': [f7], # but not f8
            '1.1.1': [b6], # but not b9
            '1.0.2': [b6], # but not b9
            '2.0.0': [f4, f5],
            '1.1.0': [f3],
            '1.0.1': [b1, b2],
        }
        expect_releases(entries, expected)

    def semver_spec_annotations_allow_preventing_forward_porting(self):
        skip()

    def semver_double_ended_specs_work_when_more_than_two_major_versions(self):
        skip()

    def can_disable_default_pin_to_latest_major_version(self):
        skip()

    def issues_before_first_release_function_correctly(self):
        f0 = f(0)
        b1 = b(1)
        f2 = f(2)
        entries = (
            '0.2.0', f2, '0.1.1', b1, '0.1.0', f0
        )
        expected = {
            '0.1.0': [f0],
            '0.1.1': [b1],
            '0.2.0': [f2],
        }
        # Make sure to skip typically-implicit 1.0.0 release.
        # TODO: consider removing that entirely; arguably needing it is a bug?
        expect_releases(entries, expected, skip_initial=True)
