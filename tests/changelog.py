from spec import Spec, skip


class releases(Spec):
    """
    Organization of issues into releases
    """
    def setup(self):
        pass

    def feature_releases_include_features(self):
        skip()

    def feature_releases_include_support(self):
        skip()

    def feature_releases_include_major_bugs(self):
        skip()

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
