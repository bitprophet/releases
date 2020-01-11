=========
Changelog
=========

- :release:`1.6.3 <2020-01-10>`
- :support:`87 backported` (via :issue:`88`) Our upper Sphinx version limit was
  mostly defensive and at this point is just too old to even build on
  ReadTheDocs successfully. Removed it for the time being. Thanks to José
  Sánchez-Gallego for the nudge and the patch.
- :release:`1.6.2 <2020-01-10>`
- :release:`1.5.2 <2020-01-10>`
- :support:`84 backported` Pin us to ``semantic-version<2.7`` as they changed
  their APIs (...) in that version in a way that breaks us. We do not need
  anything they've added recently, so the conservative response is to just pin
  until we truly need to upgrade. Thanks to everyone who reported and submitted
  workarounds for this.
- :release:`1.6.1 <2018-07-02>`
- :release:`1.5.1 <2018-07-02>`
- :support:`73 backported` (via :issue:`77`) Add support for Sphinx 1.7.x
  (while retaining support for previous versions of Sphinx). Thanks to Miro
  Hrončok for the patch.
- :release:`1.6.0 <2018-06-20>`
- :feature:`75` Update ``releases.util.parse_changelog`` so it hands kwargs
  into ``releases.util.make_app``, which in turn now accepts a
  ``load_extensions`` argument triggering loading of one's configured
  extensions. This is only of interest if you're using ``parse_changelog``
  directly; it does not impact normal Releases usage.
- :release:`1.5.0 <2018-05-02>`
- :feature:`59` Allow multiple changelog files -- ``releases_document_name``
  may now optionally be a list of strings instead of a single string. Thanks to
  William Minchin for the patch.
- :release:`1.4.2 <2018-04-27>`
- :support:`74 backported` We never pulled our README into our ``setup.py``
  metadata, resulting in a rather sparse PyPI page! This has been fixed. Thanks
  to Peter Demin for the report.
- :release:`1.4.1 <2018-03-28>`
- :support:`73 backported` Sphinx 1.7.x changed some semi-public APIs; given
  this is the second minor release in a row to do so, we're explicitly
  bracketing our ``setup.py`` dependencies to Sphinx >= 1.3 and < 1.7. We
  expect to bump this up one minor release at a time as we add compatibility
  back in.
- :release:`1.4.0 <2017-10-20>`
- :support:`-` Drop Python 2.6 and 3.3 support, to correspond with earlier
  changes in Sphinx and most other public Python projects.
- :bug:`- major` Identified a handful of issues with our Sphinx pin &
  subsequently, internal changes in Sphinx 1.6 which broke (and/or appear to
  break, such as noisy warnings) our own behavior. These have (hopefully) all
  been fixed.
- :release:`1.3.2 <2017-10-19>`
- :support:`68 backported` Update packaging requirements to allow for
  ``sphinx>=1.3,<2``. Thanks to William Minchin.
- :release:`1.3.1 <2017-05-18>`
- :bug:`60` Report extension version to Sphinx for improved Sphinx debug
  output. Credit: William Minchin.
- :bug:`66` (via :issue:`67`) Deal with some Sphinx 1.6.1 brokenness causing
  ``AttributeError`` by leveraging ``getattr()``'s default-value argument.
  Thanks to Ian Cordasco for catch & patch.
- :release:`1.3.0 <2016-12-09>`
- :feature:`-` Add ``releases.util``, exposing (among other things) a highly
  useful ``parse_changelog(path)`` function that returns a user-facing dict
  representing a parsed changelog. Allows users to examine their changelogs
  programmatically and answer questions like "do I have any outstanding bugs in
  the 1.1 release line?".
- :release:`1.2.1 <2016-07-25>`
- :support:`51 backported` Modernize release management so PyPI trove
  classifiers are more accurate, wheel archives are universal instead of Python
  2 only, and release artifacts are GPG signed.
- :bug:`56` Fix exceptions that occurred when no release/issue link options
  were configured. Now those options are truly optional: release version and
  issue number text will simply display normally instead of as hyperlinks.
  Thanks to André Caron for the report.
- :bug:`36` Changelogs with no releases whatsoever should still be viable
  instead of raising exceptions. This is now happily the case. All items in
  such changelogs will end up in a single "unreleased features" list, just as
  with regular prehistory entries. Thanks to Steve Ivy for initial report and
  André Caron for additional feedback.
- :release:`1.2.0 <2016-05-20>`
- :bug:`- major` Fix formatting of release header dates; a "75% text size"
  style rule has had an uncaught typo for some time.
- :bug:`55 major` Non-annotated changelog line items (which implicitly become
  bugs) were incorrectly truncating their contents in some situations
  (basically, any time they included non-regular-text elements like monospace,
  bold etc). This has been fixed.
- :feature:`19` Add ``unstable_prehistory`` option/mode for changelogs whose
  0.x release cycle is "rapid" or "unstable" and doesn't closely follow normal
  semantic version-driven organization. See :ref:`unstable-prehistory`.
- :bug:`53 major` Tweak newly-updated models so bugfix items prior to an
  initial release are considered 'major bugs' so they get rolled into that
  initial release (instead of causing a ``ValueError``).
- :release:`1.1.0 <2016-04-28>`
- :feature:`45` Add support for major version transitions (e.g. 1.0 to 2.0).

  .. note::
    This adds a new install-time dependency: the `semantic_version library
    <https://python-semanticversion.readthedocs.io>`_. It's pure Python, so
    installation should be trivial.

- :bug:`44 major` Update one of our internal docutils-related classes for
  compatibility with Sphinx 1.4.x. Thanks to Gabi Davar for catch & patch.
- :release:`1.0.0 <2015-11-05>`
- :feature:`42` For readability, issues within each release so they are
  displayed in feature->bug->support order.
- :feature:`41` Clean up changelog discovery so one can have comments,
  paragraphs or other non-bullet-list elements above or below the changelog.
  Thanks to Rodrigue Cloutier for the original request/patch.
- :release:`0.7.0 <2014-09-04>`
- :bug:`30 major` Add LICENSE (plus a handful of other administrative files) to
  a ``MANIFEST.in`` so sdists pick it up. Thanks to Zygmunt Krynicki for catch
  & original patch (:issue:`33`).
- :feature:`21` Allow duplicate issue numbers; not allowing them was
  technically an implementation detail. Thanks to Dorian Puła for the patch.
- :release:`0.6.1 <2014-04-06>`
- :bug:`-` Fix a silly issue with the new feature from :issue:`22` where it
  accidentally referred to the Sphinx document *title* instead of the document
  *filename*.
- :release:`0.6.0 <2014-04-03>`
- :feature:`22` Make the document name used as the changelog - previously
  hardcoded as ``changelog`` (``.rst``) - configurable. Thanks to James Mills
  for the feature request.
- :feature:`26` Allow specifying Github path shorthand config option instead of
  explicit release/issue URL strings.
- :release:`0.5.3 <2014-03-15>`
- :bug:`25` Empty/no-issue line items broke at some point; fixed.
- :bug:`24` Broke inline issue parsing; fixed now.
- :release:`0.5.2 <2014-03-13>`
- :bug:`23` Rework implementation to deal with issue descriptions that span
  more than one paragraph - subsequent paragraphs/blocks were not being
  displayed prior.
- :release:`0.5.1 <2014-02-11>`
- :bug:`-` Fix silly bug in :issue:`20` that cropped up on Python 3.x.
- :release:`0.5.0 <2014-02-11>`
- :feature:`20` Allow specifying minimum release line in bugfixes that don't
  apply to all active lines (e.g. because they pertain to a recently added
  feature.)
- :release:`0.4.0 <2013-12-24>`
- :feature:`17` Allow releases to explicitly define which issues they include.
  Useful for overriding default assumptions (e.g. a special bugfix release from
  an otherwise dormant line.)
- :release:`0.3.1 <2013-12-18>`
- :bug:`16` Fix some edge cases regarding release ordering & unreleased issue
  display. Includes splitting unreleased display info into two 'Next release'
  pseudo-release entries.
- :support:`15` Add :doc:`/concepts` to flesh out some assumptions not
  adequately explained in :doc:`/usage`.
- :release:`0.3.0 <2013-11-21>`
- :feature:`11` Fix up styling so changelogs don't look suboptimal under `the
  new Read The Docs theme
  <http://ericholscher.com/blog/2013/nov/4/new-theme-read-the-docs/>`_. Still
  looks OK under their old theme too!
- :support:`0` Move to actual Sphinx docs so we can use ourselves.
- :support:`0` Created a basic test suite to protect against regressions.
- :bug:`9 major` Clean up additional 'unreleased' display/organization
  behavior, including making sure ALL unreleased issues show up as
  'unreleased'. Thanks to Donald Stufft for the report.
- :feature:`1` (also :issue:`3`, :issue:`10`) Allow using ``-`` or ``0`` as a
  dummy issue 'number', which will result in no issue number/link being
  displayed.  Thanks to Markus Zapke-Gründemann and Hynek Schlawack for patches
  & discussion.

    * This feature lets you categorize changes that aren't directly related
      to issues in your tracker. It's an improvement over, and replacement
      for, the previous "vanilla bullet list items are treated as bugs"
      behavior.
    * Said behavior (non-role-prefixed bullet list items turning into
      regular bugs) is being retained as there's not a lot to gain from
      deactivating it.

- :release:`0.2.4 <2013.10.04>`
- :support:`0 backported` Handful of typos, doc tweaks & addition of a
  .gitignore file.  Thanks to Markus Zapke-Gründemann.
- :bug:`0` Fix duplicate display of "bare" (not prefixed with an issue role)
  changelog entries. Thanks again to Markus.
- :support:`0 backported` Edited the README/docs to be clearer about how
  Releases works/operates.
- :support:`0 backported` Explicitly documented how non-role-prefixed line
  items are preserved.
- :bug:`0` Updated non-role-prefixed line items so they get prefixed with a
  '[Bug]' signifier (since they are otherwise treated as bugfix items.)
- :release:`0.2.3 <2013.09.16>`
- :bug:`0` Fix a handful of bugs in release assignment logic.
- :release:`0.2.2 <2013.09.15>`
- :bug:`0` Ensured Python 3 compatibility.
- :release:`0.2.1 <2013.09.15>`
- :bug:`0` Fixed a stupid bug causing invalid issue hyperlinks.
- :release:`0.2.0 <2013.09.15>`
- :feature:`0` Basic functionality.
