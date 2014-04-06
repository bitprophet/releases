import os
import shutil

from spec import Spec, skip
from invoke import run


class integration(Spec):
    def setup(self):
        self.cwd = os.getcwd()

    def teardown(self):
        os.chdir(self.cwd)

    def _assert_worked(self, folder):
        os.chdir(os.path.join('tests', '_support'))
        build = os.path.join(folder, '_build')
        try:
            cmd = 'sphinx-build -c . -W {0} {1}'.format(folder, build)
            result = run(cmd, warn=True, hide=True)
            msg = "Build failed w/ stderr: {0}"
            assert result.ok, msg.format(result.stderr)
            changelog = os.path.join(build, 'changelog.html')
            with open(changelog) as fd:
                text = fd.read()
                assert "1.0.1" in text
                assert "#1" in text
        finally:
            shutil.rmtree(build)

    def vanilla_invocation(self):
        # Doctree with just-a-changelog-named-changelog
        self._assert_worked('vanilla')

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
