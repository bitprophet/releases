import os
import shutil

from spec import Spec, skip
from invoke import run


class integration(Spec):
    def setup(self):
        self.cwd = os.getcwd()

    def teardown(self):
        os.chdir(self.cwd)

    def vanilla_invocation(self):
        # Doctree with just-a-changelog-named-changelog
        os.chdir('tests/_support')
        try:
            cmd = 'sphinx-build -c . -W vanilla vanilla/_build'
            result = run(cmd, warn=True, hide=True)
            msg = "Build failed w/ stderr: {0}"
            assert result.ok, msg.format(result.stderr)
            with open('vanilla/_build/changelog.html') as fd:
                text = fd.read()
                assert "1.0.1" in text
                assert "#1" in text
        finally:
            shutil.rmtree('vanilla/_build')

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
