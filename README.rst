=================================
Releases, a Sphinx changelog tool
=================================

About
=====

Releases is a `Sphinx <http://sphinx-doc.org>`_ extension designed to help you
keep a source control friendly, merge friendly changelog file & turn it into
useful, human readable HTML output.

Specifically:

* The source format (kept in your Sphinx tree as ``changelog.rst``) is a
  stream-like timeline that plays well with source control & only requires one
  entry per change (even for changes that exist in multiple release lines).
* The output (when you have the extension installed and run your Sphinx build
  command) is a traditional looking changelog page with a section for every
  release; multi-release issues are copied automatically into each release.
* By default, feature and support issues are only displayed under feature
  releases, and bugs are only displayed under bugfix releases. This can be
  overridden on a per-issue basis.

Some background on why this tool was created can be found in `this blog post
<http://bitprophet.org/blog/2013/09/14/a-better-changelog/>`_.

Usage
=====

Mimic the format seen `in Fabric's changelog
<https://raw.github.com/fabric/fabric/master/docs/changelog.rst>`_:

* Install ``releases`` and update your Sphinx ``conf.py`` to include it in the
  ``extensions`` list setting: ``extensions = ['releases']``.

    * Also set the ``releases_release_uri`` and ``releases_issue_uri`` top
      level options - they determine the targets of the issue & release links
      in the HTML output. Both should have an unevaluated ``%s`` where the
      release/issue number would go.
    * See `Fabric's docs/conf.py
      <https://github.com/fabric/fabric/blob/4afd33e971f1c6831cc33fd3228013f7484fbe35/docs/conf.py#L31>`_
      for an example.

* Create a Sphinx document named ``changelog.rst`` with a top-level header
  followed by a bulleted list.
* Bullet list items should use the ``:support:``, ``:feature:`` or ``:bug:``
  roles to mark issues, or ``:release:`` to mark a release. These special roles
  must be the first element in each list item.

    * Line-items that do not start with any issue role will be considered bugs
      (both in terms of inclusion in releases, and formatting) and, naturally,
      will not be given a hyperlink.

* Issue roles are of the form ``:type:`number[ keyword]```. Specifically:
  
    * ``number`` is used to generate the link to the actual issue in your issue
      tracker (going by the ``releases_issue_uri`` option). It's used for both
      the link target & (part of) the link text.
    * If ``number`` is ``0`` no issue link will be generated. You can use this
      for items without a related issue.
    * Keywords are optional and may be one of:

        * ``backported``: Given on *support* or *feature* issues to denote
          backporting to bugfix releases; such issues will show up in both
          release types. E.g. placing ``:support:`123 backported``` in your
          changelog below releases '1.1.1' and '1.2.0' will cause it to appear
          in both of those releases' lists.
        * ``major``: Given on bug issues to denote inclusion in feature,
          instead of bugfix, releases. E.g. placing ``:bug:`22 major``` below
          releases '1.1.1' and '1.2.0' will cause it to appear in '1.2.0'
          **only**.

* Regular Sphinx content may be given after issue roles and will be preserved
  as-is when rendering. For example, in ``:bug:`123` Fixed a bug, thanks
  `@somebody`!``, the rendered changelog will preserve/render "Fixed a bug,
  thanks ``@somebody``!" after the issue link.
* Release roles are of the form ``:release:`number <date>```. Do not place any
  additional content after release roles - it will be ignored.

Then build your docs; in the rendered output, ``changelog.html`` should show
issues grouped by release, as per the above rules. Example: `Fabric's rendered
changelog <http://docs.fabfile.org/en/latest/changelog.html>`_.

Changes
=======

In a fit of irony, Releases is too simple for a full Sphinx doc treatment (or
for multiple release lines) and thus doesn't use itself. Here's a by-hand
changelog:

* 2013.11.05: **0.3.0**:

    * Issues #1, #3, #10 - allow using '0' as a dummy issue number, which will
      result in no issue number/link being displayed. Thanks to Markus
      Zapke-Gründemann and Hynek Schlawack for patches & discussion.

        * This feature lets you categorize changes that aren't directly related
          to issues in your tracker. It's an improvement over, and replacement
          for, the previous "vanilla bullet list items are treated as bugs"
          behavior.
        * Said behavior (non-role-prefixed bullet list items turning into
          regular bugs) is being retained as there's not a lot to gain from
          deactivating it.

* 2013.10.04: **0.2.4**:

    * Handful of typos, doc tweaks & addition of a .gitignore file. Thanks to
      Markus Zapke-Gründemann.
    * Fix duplicate display of "bare" (not prefixed with an issue role)
      changelog entries. Thanks again to Markus.
    * Edited the README/docs to be clearer about how Releases works/operates.
    * Explicitly documented how non-role-prefixed line items are preserved.
    * Updated non-role-prefixed line items so they get prefixed with a '[Bug]'
      signifier (since they are otherwise treated as bugfix items.)

* 2013.09.16: **0.2.3**:

    * Fix a handful of bugs in release assignment logic.

* 2013.09.15: **0.2.2**:

    * Python 3 compatibility.

* 2013.09.15: **0.2.1**:

    * Fixed a stupid bug causing invalid issue hyperlinks.
    * Added this README.

* 2013.09.15: **0.2.0**:

  * Basic functionality.


TODO
====

* Tests would be nice.
* Possibly add more keywords to allow control over additional edge cases.
* Add shortcut format option for the release/issue URI settings - GitHub users
  can just give their GitHub acct/repo and we will fill in the rest.
* Maybe say pre-1.0 releases consider all bugs 'major' (so one can e.g. put out
  an 0.4.0 which is all bugfixes). Iffy because what if you *wanted* regular
  feature-vs-bugfix releases pre-1.0? (which is common.)
