========
Concepts
========

Basic conceptual info about how Releases organizes and thinks about issues and
releases. For details on formatting/etc (e.g. so you can interpret the examples
below), see :doc:`/usage`.


Issue and release types
=======================

* Issues are always one of three types: **features**, **bug fixes** or
  **support items**.

    * **Features** are (typically larger) changes adding new behavior.
    * **Bug fixes** are (typically minor) changes addressing incorrect
      behavior, crashes, etc.
    * **Support items** vary in size but are usually non-code-related changes,
      such as documentation or packaging updates.

* Releases also happen to come in three flavors:

    * **Major releases** are backwards incompatible releases, often with
      large/sweeping changes to a codebase.
      
        * They increment the first version number only, e.g. ``1.0.0``.

    * **Feature releases** (sometimes called **minor** or **secondary**) are
      backwards compatible with the previous major release, and focus on adding
      new functionality (code, or support, or both.) They sometimes include
      major/complex bug fixes which are too risky to include in a bugfix
      release.
      
        * The second version number is incremented for these, e.g.  ``1.1.0``.

    * **Bugfix releases** (sometimes called **tertiary**) focus on fixing
      incorrect behavior while minimizing the risk of creating more bugs.
      Rarely, they will include small new features deemed important enough to
      backport from their 'native' feature release.
      
        * These releases increment the third/final version number, e.g.
          ``1.1.1``.
 

Release organization
====================

We parse changelog timelines so the resulting per-release issue lists honor the
above descriptions. Here are the core rules, with examples. See :doc:`/usage`
for details on formatting/etc.

* **By default, bugfixes go into bugfix releases, features and support items go
  into feature releases.**

    * Input::

        * :release:`1.1.0 <date>`
        * :release:`1.0.1 <date>`
        * :support:`4` Updated our test runner
        * :bug:`3` Another bugfix
        * :feature:`2` Implemented new feature
        * :bug:`1` Fixed a bug
        * :release:`1.0.0 <date>`

    * Result:

        * ``1.0.1``: bug #1, bug #3
        * ``1.1.0``: feature #2, support #4

* **Bugfixes are assumed to backport to all stable release lines, and are
  displayed as such.** (Unless the release explicitly states - see later
  bullet points.)

    * Input::

        * :release:`1.1.1 <date>`
        * :release:`1.0.2 <date>`
        * :bug:`3` Fixed another bug, onoes
        * :release:`1.1.0 <date>`
        * :release:`1.0.1 <date>`
        * :feature:`2` Implemented new feature
        * :bug:`1` Fixed a bug
        * :release:`1.0.0 <date>`

    * Result:

        * ``1.0.1``: bug #1
        * ``1.1.0``: feature #2
        * ``1.0.2``: bug #3
        * ``1.1.1``: bug #3

* **Bugfixes marked 'major' go into feature releases instead.**

    * Input::
    
        * :release:`1.1.0 <date>`
        * :release:`1.0.1 <date>`
        * :bug:`3 major` Big bugfix with lots of changes
        * :feature:`2` Implemented new feature
        * :bug:`1` Fixed a bug
        * :release:`1.0.0 <date>`

    * Result:

        * ``1.0.1``: bug #1
        * ``1.1.0``: feature #2, bug #3

* **Features or support items marked 'backported' appear in both bugfix and
  feature releases.**

    * Input::
    
        * :release:`1.1.0 <date>`
        * :release:`1.0.1 <date>`
        * :bug:`4` Fixed another bug
        * :feature:`3` Regular feature
        * :feature:`2 backported` Small new feature worth backporting
        * :bug:`1` Fixed a bug
        * :release:`1.0.0 <date>`

    * Result:

        * ``1.0.1``: bug #1, feature #2, bug #4
        * ``1.1.0``: feature #2, feature #3

* **Releases implicitly include all issues from their own, and prior, release
  lines.** (Again, unless the release explicitly states otherwise - see below.)

    * For example, in the below changelog (remembering that changelogs are
      written in descending order from newest to oldest entry) the code
      released as ``1.1.0`` includes the changes from bugs #1 and #3, in
      addition to its explicitly stated contents of feature #2::

        * :release:`1.1.0 <date>`
        * :release:`1.0.1 <date>`
        * :bug:`3` Another bugfix
        * :feature:`2` Implemented new feature
        * :bug:`1` Fixed a bug
        * :release:`1.0.0 <date>`

    * Again, to be explicit, the rendered changelog displays this breakdown:

        * ``1.0.1``: bug #1, bug #3
        * ``1.1.0``: feature #2

      But it's *implied* that ``1.1.0`` includes the contents of ``1.0.1``
      because it released afterwards/simultaneously and is a higher release
      line.

* **Releases may be told explicitly which issues to include** (using a
  comma-separated list.) This is useful for the rare bugfix that gets
  backported beyond the actively supported release lines.

  For example, below shows a project whose lifecycle is "release 1.0; release
  1.1 and drop active support for 1.0; put out a special 1.0.x release."
  Without the explicit issue list for 1.0.1, Releases would roll up all
  bugfixes, including the two that didn't actually apply to the 1.0 line.

    * Input::
    
        * :release:`1.0.1 <date>` 1, 5
        * :release:`1.1.1 <date>`
        * :bug:`5` Bugfix that applied back to 1.0.
        * :bug:`4` Bugfix that didn't apply to 1.0, only 1.1
        * :bug:`3` Bugfix that didn't apply to 1.0, only 1.1
        * :release:`1.1.0 <date>`
        * :feature:`2` Implemented new feature
        * :bug:`1` Fixed a 1.0.0 bug
        * :release:`1.0.0 <date>`

    * Result:

        * ``1.1.0``: feature #2
        * ``1.1.1``: bugs #3, #4 and #5
        * ``1.0.1``: bugs #1 and #5 only
