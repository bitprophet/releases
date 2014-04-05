from spec import Spec, skip


class integration(Spec):
    def vanilla_invocation(self):
        # Doctree with just-a-changelog-named-changelog
        skip()

    def vanilla_with_other_files(self):
        # Same but w/ other files in toctree
        skip()

    def customized_filename_with_identical_title(self):
        # Changelog named not 'changelog', same title
        skip()

    def customized_filename_with_different_title(self):
        # Changelog named not 'changelog', title distinct
        skip()

    def customized_filename_with_other_files(self):
        # Same as above but w/ other files in toctree
        skip()

    def useful_error_if_changelog_is_missed(self):
        # Don't barf with unknown-node errors if changelog not found.
        skip()
