=================================
Releases, a Sphinx changelog tool
=================================

About
=====

Releases is a `Sphinx <http://sphinx-doc.org>`_ extension designed to help you
keep a source control friendly, merge friendly changelog file & turn it into a
useful, human readable HTML output.

Specifically:

* The source format is a stream-like timeline that plays well with source
  control & only requires one entry per change (even for changes that exist in
  multiple release lines).
* The output is a traditional looking changelog with a section for every
  release; multi-release issues are copied automatically into each release.
* By default, feature and support issues are only displayed under feature
  releases, and bugs are only displayed under bugfix releases. This can be
  overridden on a per-issue basis.

Usage
=====

Mimic the format seen `in Fabric's changelog
<https://raw.github.com/fabric/fabric/master/docs/changelog.rst>`_:

* Install ``releases`` and update your Sphinx ``conf.py`` to include it in the
  ``extensions`` list setting: ``extensions = ['releases']``.

    * Also set the ``releases_release_uri`` and ``releases_issue_uri`` top
      level options. Both should have an unevaluated ``%s`` where the
      release/issue number would go.
    * See `Fabric's docs/conf.py
      <https://github.com/fabric/fabric/blob/4afd33e971f1c6831cc33fd3228013f7484fbe35/docs/conf.py#L31>`_
      for an example.

* Create a docs file named ``changelog.rst`` with a top-level header followed
  by a bulleted list.
* Bullet list items must use the ``:support:``, ``:feature`` or ``:bug`` roles to
  mark issues, or ``:release:`` to mark a release. These special roles must be
  the first element in each list item.
* Issue roles are of the form ``:type:`number[ keyword]```. Keywords are
  optional and may be one of:

    * ``backported``: Given on support or feature issues to denote
      backporting to bugfix releases; will show up in both release types.
    * ``major``: Given on bug issues to denote inclusion in feature, instead
      of bugfix, releases.

* Regular Sphinx content may be given after issue roles and will be preserved
  as-is when rendering.
* Release roles are of the form ``:release:`number <date>```. Do not place any
  additional elements after release roles.

Then build your docs; ``changelog.html`` should show issues grouped by release,
as per the above rules. Example: `Fabric's rendered changelog
<http://docs.fabfile.org/en/latest/changelog.html>`_.

Changes
=======

In a fit of irony, Releases is too simple for a full Sphinx doc treatment (or
for multiple release lines) and thus doesn't use itself. Here's a by-hand
changelog:

* 2013.09.15: **0.2.2**:

    * Python 3 compatibility.

* 2013.09.15: **0.2.1**:

    * Fixed a stupid bug causing invalid issue hyperlinks.
    * Added this README.

* 2013.09.15: **0.2.0**:

  * Basic functionality.


TODO
====

* Migrate to a directive-driven (vs role-driven) format. Existing format
  evolved from a purely role-oriented, prose-embedded setup; roles are no
  longer the right way to do this.
* Possibly add more keywords to allow control over additional edge cases.
* Add shortcut format option for the release/issue URI settings - Github users
  can just give their Github acct/repo and we will fill in the rest.
