import os
import shutil

from pytest import skip
from invoke import run


class integration:
    def setup_method(self):
        self.cwd = os.getcwd()

    def teardown(self):
        os.chdir(self.cwd)

    def _build(
        self,
        folder,
        conf_opts,
        extra_flags,
        target,
        asserts=None,
        conf=".",
        warn=False,
    ):
        # Dynamic sphinx opt overrides
        if conf_opts:
            pairs = map(lambda x: "=".join(x), (conf_opts or {}).items())
            flags = map(lambda x: "-D {}".format(x), pairs)
            flagstr = " ".join(flags)
        else:
            flagstr = ""
        if extra_flags:
            flagstr = flagstr + " " + extra_flags
        # Setup
        os.chdir(os.path.join("integration", "_support"))
        build = os.path.join(folder, "_build")
        try:
            # Build
            cmd = "sphinx-build {} -c {} -W {} {}".format(
                flagstr, conf, folder, build
            )
            result = run(cmd, warn=warn, hide=True, in_stream=False)
            if callable(asserts):
                if isinstance(target, str):
                    targets = [target]
                else:
                    targets = target
                for target in targets:
                    asserts(result, build, target)
            return result
        finally:
            shutil.rmtree(build)
            # TODO: there's apparently NO way to just turn this off instead?
            shutil.rmtree(
                os.path.join(folder, ".doctrees"), ignore_errors=True
            )

    def _assert_worked(
        self,
        folder,
        conf_opts=None,
        extra_flags=None,
        target="changelog",
        conf=".",
    ):
        self._build(
            folder=folder,
            conf_opts=conf_opts,
            extra_flags=extra_flags,
            target=target,
            asserts=self._basic_asserts,
            conf=conf,
        )

    def _basic_asserts(self, result, build, target):
        # Check for errors
        msg = "Build failed w/ stderr: {}"
        assert result.ok, msg.format(result.stderr)
        # Check for vaguely correct output
        changelog = os.path.join(build, "{}.html".format(target))
        with open(changelog) as fd:
            text = fd.read()
            assert "1.0.1" in text
            assert "#1" in text

    def vanilla_invocation(self):
        # Doctree with just-a-changelog-named-changelog
        self._assert_worked("vanilla")

    def vanilla_singlehtml(self):
        # This started breaking sometime after Sphinx >1.8.x support was added,
        # first noticed via RTD's singlehtml-derived builder, but happily it's
        # testable via the default singlehtml builder too.
        self._assert_worked(
            folder="vanilla",
            target="index",  # singlehtml only ever builds one index.html
            extra_flags="-b singlehtml",
            conf_opts={"releases_debug": "1"},
        )

    def singlehtml_with_multiple_lists(self):
        self._assert_worked(
            folder="singlehtml_multilist",
            target="index",  # singlehtml only ever builds one index.html
            extra_flags="-b singlehtml",
            conf_opts={"releases_debug": "1"},
        )

    def customized_filename_with_identical_title(self):
        # Changelog named not 'changelog', same title
        self._assert_worked(
            folder="custom_identical",
            conf_opts={"releases_document_name": "notachangelog"},
            target="notachangelog",
        )

    def customized_filename_with_different_title(self):
        # Changelog named not 'changelog', title distinct
        # NOTE: the difference here is in the fixture!
        self._assert_worked(
            folder="custom_different",
            conf_opts={"releases_document_name": "notachangelog"},
            target="notachangelog",
        )

    def useful_error_if_changelog_is_missed(self):
        # Don't barf with unknown-node errors if changelog not found.
        skip()

    def useful_error_if_buried_issue_nodes(self):
        # Don't unknown-node error if broken ReST causes 'hidden' issue nodes.
        # E.g. an accidental definition-list wrapping one.
        result = self._build(
            folder="hidden_issues",
            conf_opts=None,
            extra_flags=None,
            target="changelog",
            warn=True,
        )
        assert result.failed
        assert (
            # Sphinx <4
            ("Exception occurred" in result.stderr)
            # Sphinx >=4
            or ("Extension error" in result.stderr)
        )
        assert "double-check" in result.stderr
        assert "innocuous" in result.stderr

    def multiple_changelogs(self):
        # support multiple changelogs
        self._assert_worked(
            folder="multiple_changelogs",
            conf_opts=None,
            conf="multiple_changelogs",
            # Ensure the asserts check both changelogs
            target=["a_changelog", "b_changelog"],
        )
