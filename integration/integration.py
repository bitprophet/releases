import os
import shutil

from spec import Spec, skip
from invoke import run


class integration(Spec):
    def setup(self):
        self.cwd = os.getcwd()

    def teardown(self):
        os.chdir(self.cwd)

    def _build(self, folder, opts, target, asserts=None):
        # Dynamic sphinx opt overrides
        pairs = map(lambda x: '='.join(x), (opts or {}).items())
        flags = map(lambda x: '-D {0}'.format(x), pairs)
        flagstr = ' '.join(flags)
        # Setup
        os.chdir(os.path.join('integration', '_support'))
        build = os.path.join(folder, '_build')
        try:
            # Build
            cmd = 'sphinx-build {2} -c . -W {0} {1}'.format(
                folder, build, flagstr)
            result = run(cmd, warn=True, hide=True)
            if callable(asserts):
                asserts(result, build, target)
            return result
        finally:
            shutil.rmtree(build)

    def _assert_worked(self, folder, opts=None, target='changelog'):
        self._build(folder, opts, target, asserts=self._basic_asserts)

    def _basic_asserts(self, result, build, target):
        # Check for errors
        msg = "Build failed w/ stderr: {0}"
        assert result.ok, msg.format(result.stderr)
        # Check for vaguely correct output
        changelog = os.path.join(build, '{0}.html'.format(target))
        with open(changelog) as fd:
            text = fd.read()
            assert "1.0.1" in text
            assert "#1" in text

    def vanilla_invocation(self):
        # Doctree with just-a-changelog-named-changelog
        self._assert_worked('vanilla')

    def customized_filename_with_identical_title(self):
        # Changelog named not 'changelog', same title
        self._assert_worked(
            folder='custom_identical',
            opts={'releases_document_name': 'notachangelog'},
            target='notachangelog',
        )

    def customized_filename_with_different_title(self):
        # Changelog named not 'changelog', title distinct
        # NOTE: the difference here is in the fixture!
        self._assert_worked(
            folder='custom_different',
            opts={'releases_document_name': 'notachangelog'},
            target='notachangelog',
        )

    def useful_error_if_changelog_is_missed(self):
        # Don't barf with unknown-node errors if changelog not found.
        skip()

    def useful_error_if_buried_issue_nodes(self):
        # Don't unknown-node error if broken ReST causes 'hidden' issue nodes.
        # E.g. an accidental definition-list wrapping one.
        result = self._build(
            folder='hidden_issues',
            opts=None,
            target='changelog',
        )
        assert result.failed
        assert "ValueError" in result.stderr
        assert "double-check" in result.stderr
