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
      
        * Feature releases are implicitly assumed to include all bugfixes
          released before them, in addition to their own contents. In other
          words, bugs fixed in older release lines are always forward-ported
          when possible.
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
